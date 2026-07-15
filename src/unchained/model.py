"""Provider seam for audited OpenAI Responses API calls and offline fakes."""

from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass, replace
from typing import Any, Protocol

from .audit import AuditLog, canonical_json, first_2kb, sha256_text
from .caps import CapExceeded, RunBudget, estimate_usage_cost
from .models import FunctionCall, JsonValue, ModelResponse, ModelUsage


@dataclass(frozen=True, slots=True)
class ModelRequest:
    """One provider-neutral model request issued by the controller."""

    phase: str
    instructions: str
    input_items: list[dict[str, JsonValue]] | str
    tools: tuple[dict[str, JsonValue], ...] = ()
    parallel_tool_calls: bool | None = None
    tool_choice: str | dict[str, JsonValue] | None = None
    previous_response_id: str | None = None
    max_output_tokens: int = 16_384
    timeout_seconds: float | None = None
    store: bool = False
    include: tuple[str, ...] = ("reasoning.encrypted_content",)
    reasoning_context: str = "current_turn"
    prompt_cache_mode: str = "explicit"


class ModelProviderError(RuntimeError):
    """Raised after a provider/protocol failure has been safely audited."""


class ModelClient(Protocol):
    """Small interface implemented by the live provider and test doubles."""

    @property
    def model_id(self) -> str:
        """Return the exact configured model identifier."""

    def create(self, request: ModelRequest) -> ModelResponse:
        """Create one response without applying investigation policy."""


def _json_value(value: Any) -> JsonValue:
    """Normalize SDK objects without depending on their concrete classes."""

    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return _json_value(model_dump(mode="json"))
    return str(value)


class OpenAIResponsesModel:
    """Lazy OpenAI SDK adapter using the Responses function-calling protocol."""

    def __init__(self, *, model_id: str | None = None, api_key: str | None = None) -> None:
        configured_model = model_id or os.getenv("UNCHAINED_MODEL")
        if not configured_model:
            raise ValueError("UNCHAINED_MODEL is required (for example: gpt-5.6)")
        if not (configured_model == "gpt-5.6" or configured_model.startswith("gpt-5.6-sol")):
            raise ValueError("UNCHAINED_MODEL must identify GPT-5.6 Sol")
        configured_key = api_key or os.getenv("OPENAI_API_KEY")
        if not configured_key:
            raise ValueError("OPENAI_API_KEY is required")

        # Import only for a live run. Tests and evidence profiling need no SDK import.
        from openai import OpenAI

        self._model_id = configured_model
        self._client = OpenAI(api_key=configured_key, max_retries=0)

    @property
    def model_id(self) -> str:
        return self._model_id

    def create(self, request: ModelRequest) -> ModelResponse:
        kwargs: dict[str, Any] = {
            "model": self._model_id,
            "instructions": request.instructions,
            "input": request.input_items,
            "max_output_tokens": request.max_output_tokens,
            "store": request.store,
            "include": list(request.include),
            "reasoning": {"context": request.reasoning_context},
            # GPT-5.6 exposes this experimental request field before the pinned
            # SDK's typed ``Responses.create`` signature does.  ``extra_body``
            # is the SDK-supported escape hatch for forwarding such fields.
            # Explicit mode without a content breakpoint disables caching.
            "extra_body": {
                "prompt_cache_options": {"mode": request.prompt_cache_mode},
            },
        }
        if request.tools:
            kwargs["tools"] = list(request.tools)
        if request.parallel_tool_calls is not None:
            kwargs["parallel_tool_calls"] = request.parallel_tool_calls
        if request.tool_choice is not None:
            kwargs["tool_choice"] = request.tool_choice
        if request.previous_response_id:
            kwargs["previous_response_id"] = request.previous_response_id
        if request.timeout_seconds is not None:
            kwargs["timeout"] = request.timeout_seconds

        response = self._client.responses.create(**kwargs)
        output_items: list[dict[str, JsonValue]] = []
        function_calls: list[FunctionCall] = []
        for raw_item in getattr(response, "output", ()):
            normalized = _json_value(raw_item)
            if not isinstance(normalized, dict):
                continue
            output_items.append(normalized)
            if normalized.get("type") != "function_call":
                continue
            arguments_raw = normalized.get("arguments", "{}")
            parse_error: str | None = None
            try:
                arguments = (
                    json.loads(arguments_raw) if isinstance(arguments_raw, str) else arguments_raw
                )
            except json.JSONDecodeError as exc:
                arguments = {}
                parse_error = f"invalid JSON arguments: {exc.msg}"
            if not isinstance(arguments, dict):
                arguments = {}
                parse_error = "function arguments must decode to an object"
            call_id = str(normalized.get("call_id") or "")
            name = str(normalized.get("name") or "")
            if not call_id:
                parse_error = _join_error(parse_error, "function call_id is empty")
            if not name:
                parse_error = _join_error(parse_error, "function name is empty")
            if normalized.get("status") == "incomplete":
                parse_error = _join_error(parse_error, "function call item is incomplete")
            function_calls.append(
                FunctionCall(
                    call_id=call_id,
                    name=name,
                    arguments={str(key): _json_value(value) for key, value in arguments.items()},
                    arguments_valid=parse_error is None,
                    parse_error=parse_error,
                )
            )

        usage, usage_error = _parse_provider_usage(getattr(response, "usage", None))
        request_id = getattr(response, "_request_id", None)
        return ModelResponse(
            response_id=str(getattr(response, "id", "")),
            text=str(getattr(response, "output_text", "") or ""),
            function_calls=tuple(function_calls),
            usage=usage,
            output_items=tuple(output_items),
            request_id=str(request_id) if request_id else None,
            status=str(getattr(response, "status", "completed") or "completed"),
            incomplete_details=_json_value(getattr(response, "incomplete_details", None)),
            error=_json_value(getattr(response, "error", None)),
            usage_error=usage_error,
        )


class AuditedModel:
    """Apply wall/token/cost caps and complete audit recording to every model call."""

    def __init__(self, client: ModelClient, audit: AuditLog, budget: RunBudget) -> None:
        self.client = client
        self.audit = audit
        self.budget = budget

    @property
    def model_id(self) -> str:
        return self.client.model_id

    def create(self, request: ModelRequest) -> ModelResponse:
        self.budget.check()
        estimated_input_tokens = _estimate_request_tokens(request)
        allowed_output_tokens = self.budget.prepare_model_request(
            estimated_input_tokens,
            request.max_output_tokens,
            self.model_id,
        )
        remaining_wall = self.budget.remaining_wall_seconds()
        bounded = replace(
            request,
            max_output_tokens=allowed_output_tokens,
            timeout_seconds=min(request.timeout_seconds or remaining_wall, remaining_wall),
        )
        self.audit.model_request(
            phase=bounded.phase,
            model=self.model_id,
            instructions=bounded.instructions,
            input_items=_redact_tool_outputs(bounded.input_items),
            tools=bounded.tools,
            previous_response_id=bounded.previous_response_id,
        )
        self.audit.append(
            "model.request.options",
            {
                "phase": bounded.phase,
                "parallel_tool_calls": bounded.parallel_tool_calls,
                "tool_choice": bounded.tool_choice,
                "max_output_tokens": bounded.max_output_tokens,
                "estimated_input_tokens": estimated_input_tokens,
                "timeout_seconds": bounded.timeout_seconds,
                "store": bounded.store,
                "include": list(bounded.include),
                "reasoning_context": bounded.reasoning_context,
                "prompt_cache_mode": bounded.prompt_cache_mode,
            },
            actor="model-client",
        )
        try:
            response = self.client.create(bounded)
        except Exception as exc:
            self.audit.append(
                "model.error",
                {
                    "phase": bounded.phase,
                    "error_type": type(exc).__name__,
                    "error": str(exc)[:2_000],
                },
                actor="model-client",
            )
            try:
                self.budget.check()
            except CapExceeded as cap_error:
                self._record_cap(cap_error)
                raise
            raise ModelProviderError(
                f"model request failed during {bounded.phase}: {type(exc).__name__}: {exc}"
            ) from exc
        if response.usage_error is not None:
            snapshot = self.budget.snapshot()
            self.audit.model_response(
                phase=bounded.phase,
                model=self.model_id,
                response=response,
                call_cost_usd=0.0,
                running_cost_usd=snapshot.estimated_cost_usd,
            )
            self.audit.append(
                "model.error",
                {
                    "phase": bounded.phase,
                    "error_type": "usage_protocol",
                    "error": response.usage_error,
                },
                actor="model-client",
            )
            raise ModelProviderError(
                f"model response during {bounded.phase} had invalid usage: {response.usage_error}"
            )
        try:
            call_cost = estimate_usage_cost(self.budget.config, response.usage, self.model_id)
        except ValueError as exc:
            snapshot = self.budget.snapshot()
            self.audit.model_response(
                phase=bounded.phase,
                model=self.model_id,
                response=response,
                call_cost_usd=0.0,
                running_cost_usd=snapshot.estimated_cost_usd,
            )
            self.audit.append(
                "model.error",
                {
                    "phase": bounded.phase,
                    "error_type": "usage_protocol",
                    "error": str(exc),
                },
                actor="model-client",
            )
            raise ModelProviderError(
                f"model response during {bounded.phase} had invalid usage: {exc}"
            ) from exc
        cap_error: CapExceeded | None = None
        try:
            self.budget.record_model_usage(response.usage, self.model_id)
        except CapExceeded as exc:
            cap_error = exc
        snapshot = self.budget.snapshot()
        self.audit.model_response(
            phase=bounded.phase,
            model=self.model_id,
            response=response,
            call_cost_usd=call_cost,
            running_cost_usd=snapshot.estimated_cost_usd,
        )
        if cap_error is not None:
            self._record_cap(cap_error)
            raise cap_error
        try:
            self.budget.check()
        except CapExceeded as wall_error:
            self._record_cap(wall_error)
            raise
        try:
            self._validate_response(response, bounded.phase)
        except ModelProviderError as exc:
            self.audit.append(
                "model.error",
                {
                    "phase": bounded.phase,
                    "error_type": "response_protocol",
                    "error": str(exc),
                },
                actor="model-client",
            )
            raise
        return response

    def _record_cap(self, error: CapExceeded) -> None:
        self.audit.append(
            "cap.fired",
            {
                "kind": error.kind.value,
                "detail": error.detail,
                "budget": error.snapshot.public_dict(),
            },
        )

    def _validate_response(self, response: ModelResponse, phase: str) -> None:
        if response.status != "completed":
            raise ModelProviderError(
                f"model response during {phase} was {response.status}: "
                f"{response.incomplete_details or response.error or 'no detail'}"
            )
        call_ids: set[str] = set()
        for call in response.function_calls:
            if not call.arguments_valid:
                raise ModelProviderError(
                    f"model returned an invalid function call during {phase}: {call.parse_error}"
                )
            if call.call_id in call_ids:
                raise ModelProviderError(
                    f"model returned duplicate call_id {call.call_id!r} during {phase}"
                )
            call_ids.add(call.call_id)


def _join_error(current: str | None, extra: str) -> str:
    return extra if current is None else f"{current}; {extra}"


def _parse_provider_usage(raw: Any) -> tuple[ModelUsage, str | None]:
    """Parse mandatory usage counters without converting anomalies to zero."""

    if raw is None:
        return ModelUsage(), "provider response omitted mandatory usage accounting"

    def count(source: Any, field: str, *, required: bool) -> int:
        value = getattr(source, field, None)
        if value is None and not required:
            return 0
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            requirement = "nonnegative integer" if required else "nonnegative integer when present"
            raise ValueError(f"usage.{field} must be a {requirement}")
        return value

    try:
        input_tokens = count(raw, "input_tokens", required=True)
        output_tokens = count(raw, "output_tokens", required=True)
        provider_total_tokens = count(raw, "total_tokens", required=True)
        input_details = getattr(raw, "input_tokens_details", None)
        output_details = getattr(raw, "output_tokens_details", None)
        cached_tokens = count(input_details, "cached_tokens", required=False)
        cache_write_tokens = count(input_details, "cache_write_tokens", required=False)
        reasoning_tokens = count(output_details, "reasoning_tokens", required=False)
    except ValueError as exc:
        return ModelUsage(), str(exc)
    component_total = input_tokens + output_tokens
    if provider_total_tokens != component_total:
        return (
            ModelUsage(),
            "usage.total_tokens does not equal input_tokens + output_tokens",
        )
    return (
        ModelUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_input_tokens=cached_tokens,
            cache_write_tokens=cache_write_tokens,
            reasoning_tokens=reasoning_tokens,
            provider_total_tokens=provider_total_tokens,
        ),
        None,
    )


def _estimate_request_tokens(request: ModelRequest) -> int:
    """Estimate model-visible tokens with a safety margin before dispatch."""

    serialized = canonical_json(
        {
            "instructions": request.instructions,
            "input": request.input_items,
            "tools": request.tools,
            "tool_choice": request.tool_choice,
            "include": request.include,
            "reasoning_context": request.reasoning_context,
            "prompt_cache_mode": request.prompt_cache_mode,
        }
    )
    try:
        import tiktoken

        encoded = tiktoken.get_encoding("o200k_base").encode(serialized)
        estimate = len(encoded)
    except (ImportError, KeyError, ValueError):
        # A BPE token consumes at least one source byte. Counting every byte as
        # a token is deliberately pessimistic when the tokenizer is unavailable.
        estimate = len(serialized.encode("utf-8"))
    return max(1, math.ceil(estimate * 1.10) + 256)


def _redact_tool_outputs(value: Any) -> JsonValue:
    """Keep model audit inputs bounded while preserving tool-output receipts."""

    if isinstance(value, dict):
        if value.get("type") == "function_call_output" and "output" in value:
            output = str(value.get("output") or "")
            return {
                "type": "function_call_output",
                "call_id": str(value.get("call_id") or ""),
                "output_sha256": sha256_text(output),
                "output_first_2kb": first_2kb(output),
                "output_bytes": len(output.encode("utf-8", errors="replace")),
            }
        return {str(key): _redact_tool_outputs(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact_tool_outputs(item) for item in value]
    return _json_value(value)


def function_output(call_id: str, output: str) -> dict[str, JsonValue]:
    """Build the exact Responses API item used to return local tool output."""

    return {"type": "function_call_output", "call_id": call_id, "output": output}


def model_response_dict(response: ModelResponse) -> dict[str, JsonValue]:
    """Return a compact normalized response for protocol-error audit events."""

    return {
        "response_id": response.response_id,
        "text": response.text,
        "function_calls": [asdict(call) for call in response.function_calls],
        "usage": asdict(response.usage),
        "status": response.status,
        "incomplete_details": response.incomplete_details,
        "error": response.error,
        "usage_error": response.usage_error,
    }
