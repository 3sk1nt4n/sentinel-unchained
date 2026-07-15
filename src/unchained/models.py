"""Small, dependency-free domain models shared by the Unchained runtime."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal, TypeAlias

JsonValue: TypeAlias = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
OsFamily: TypeAlias = Literal["windows", "linux", "macos", "unknown"]
EvidenceShape: TypeAlias = Literal["memory-only", "disk-only", "both", "logs-only", "unknown"]
MODEL_TOOL_OUTPUT_MAX_BYTES = 64 * 1024


class RunStatus(StrEnum):
    """Terminal run state used by the CLI and report header."""

    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    FATAL = "FATAL"
    INVALID = "INVALID"


class FindingStatus(StrEnum):
    """Investigator proposal and judge verdict vocabulary."""

    CONFIRMED = "CONFIRMED"
    NEEDS_REVIEW = "NEEDS-REVIEW"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    """One original input file and its deterministic classification."""

    evidence_id: str
    path: Path
    kind: Literal["memory", "disk", "log", "unknown"]
    size: int
    sha256: str
    filesystem: str | None = None
    filesystem_offset: int | None = None
    os_hint: OsFamily = "unknown"
    health: str = "unknown"
    symbols: str = "not-applicable"
    available: bool = True
    warnings: tuple[str, ...] = ()

    def public_dict(self) -> dict[str, JsonValue]:
        """Return a model-safe view; local paths stay inside the trusted runner."""

        data = asdict(self)
        data.pop("path", None)
        data["warnings"] = list(self.warnings)
        return data

    def local_dict(self) -> dict[str, JsonValue]:
        """Return the model-safe view plus the runner-local evidence path."""

        return {**self.public_dict(), "path": str(self.path)}


@dataclass(frozen=True, slots=True)
class EvidenceProfile:
    """The complete deterministic Step-0 result handed to the investigator."""

    root: Path
    os: OsFamily
    shape: EvidenceShape
    filesystems: tuple[str, ...]
    sizes: dict[str, int]
    health: dict[str, str]
    symbols: dict[str, str]
    hashes: dict[str, str]
    available_tool_families: tuple[str, ...]
    capability_label: str
    items: tuple[EvidenceItem, ...]
    mount_path: Path | None = None
    warnings: tuple[str, ...] = ()

    @property
    def memory_items(self) -> tuple[EvidenceItem, ...]:
        return tuple(item for item in self.items if item.kind == "memory" and item.available)

    @property
    def disk_items(self) -> tuple[EvidenceItem, ...]:
        return tuple(item for item in self.items if item.kind == "disk" and item.available)

    @property
    def fs(self) -> tuple[str, ...]:
        """Expose the prompt's canonical ``fs`` field without duplicating state."""

        return self.filesystems

    def public_dict(self) -> dict[str, JsonValue]:
        """Return the bounded profile representation sent to the model."""

        return {
            "os": self.os,
            "shape": self.shape,
            "fs": list(self.filesystems),
            "filesystems": list(self.filesystems),
            "sizes": dict(self.sizes),
            "health": dict(self.health),
            "symbols": dict(self.symbols),
            "hashes": dict(self.hashes),
            "available_tool_families": list(self.available_tool_families),
            "capability_label": self.capability_label,
            "warnings": list(self.warnings),
            "evidence": [item.public_dict() for item in self.items],
        }


@dataclass(frozen=True, slots=True)
class FunctionCall:
    """A parsed Responses API function call."""

    call_id: str
    name: str
    arguments: dict[str, JsonValue]
    arguments_valid: bool = True
    parse_error: str | None = None


@dataclass(frozen=True, slots=True)
class ModelUsage:
    """Observed token usage for one model response."""

    input_tokens: int = 0
    output_tokens: int = 0
    cached_input_tokens: int = 0
    cache_write_tokens: int = 0
    reasoning_tokens: int = 0
    provider_total_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        """Return the most conservative provider or component total."""

        return max(self.provider_total_tokens, self.input_tokens + self.output_tokens)


@dataclass(frozen=True, slots=True)
class ModelResponse:
    """Provider-neutral response used by the agent and offline fakes."""

    response_id: str
    provider_model: str | None = None
    text: str = ""
    function_calls: tuple[FunctionCall, ...] = ()
    usage: ModelUsage = ModelUsage()
    output_items: tuple[dict[str, JsonValue], ...] = ()
    request_id: str | None = None
    status: str = "completed"
    incomplete_details: JsonValue = None
    error: JsonValue = None
    usage_error: str | None = None


@dataclass(frozen=True, slots=True)
class ToolResult:
    """Immutable receipt returned by the trusted tool runner."""

    call_id: str
    tool_name: str
    arguments: dict[str, JsonValue]
    output: str
    output_sha256: str
    status: Literal["success", "error", "timeout", "not-applicable", "rejected", "capped"]
    started_at: str
    ended_at: str
    duration_ms: int
    error: str | None = None

    def model_output(self) -> str:
        """Return a byte-bounded view while retaining the full accepted output on disk."""

        accepted_bytes = len(self.output.encode("utf-8"))
        if accepted_bytes <= MODEL_TOOL_OUTPUT_MAX_BYTES:
            return self.output

        def render(prefix_characters: int) -> str:
            return json.dumps(
                {
                    "accepted_output_prefix": self.output[:prefix_characters],
                    "delivery_receipt": {
                        "accepted_output_bytes": accepted_bytes,
                        "accepted_output_sha256": self.output_sha256,
                        "model_view_complete": False,
                        "model_view_max_bytes": MODEL_TOOL_OUTPUT_MAX_BYTES,
                        "model_view_prefix_characters": prefix_characters,
                        "selection": "native-order UTF-8 prefix",
                    },
                },
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            )

        low = 0
        high = len(self.output)
        best = render(0)
        while low <= high:
            middle = (low + high) // 2
            candidate = render(middle)
            if len(candidate.encode("utf-8")) <= MODEL_TOOL_OUTPUT_MAX_BYTES:
                best = candidate
                low = middle + 1
            else:
                high = middle - 1
        return best


@dataclass(frozen=True, slots=True)
class Finding:
    """One investigator-produced finding before or after judge review."""

    finding_id: str
    title: str
    summary: str
    proposed_status: FindingStatus
    severity: str
    tool_call_ids: tuple[str, ...]
    iocs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, data: dict[str, Any], index: int) -> Finding:
        """Normalize a model-provided finding while preserving model semantics."""

        raw_status = str(data.get("proposed_status") or "NEEDS-REVIEW").upper().replace("_", "-")
        try:
            status = FindingStatus(raw_status)
        except ValueError:
            status = FindingStatus.NEEDS_REVIEW
        return cls(
            finding_id=str(data.get("finding_id") or f"F{index:03d}"),
            title=str(data.get("title") or "Untitled finding"),
            summary=str(data.get("summary") or ""),
            proposed_status=status,
            severity=str(data.get("severity") or "UNKNOWN").upper(),
            tool_call_ids=tuple(str(value) for value in data.get("tool_call_ids") or ()),
            iocs=tuple(str(value) for value in data.get("iocs") or ()),
            limitations=tuple(str(value) for value in data.get("limitations") or ()),
        )

    def public_dict(self) -> dict[str, JsonValue]:
        data = asdict(self)
        data["proposed_status"] = self.proposed_status.value
        for key in ("tool_call_ids", "iocs", "limitations"):
            data[key] = list(data[key])
        return data


@dataclass(frozen=True, slots=True)
class EvidenceQuote:
    """Exact bounded receipt text used by the fresh judge for one verdict."""

    tool_call_id: str
    text: str

    def public_dict(self) -> dict[str, JsonValue]:
        """Return the quote in the stable proof-bundle representation."""

        return {"tool_call_id": self.tool_call_id, "text": self.text}


@dataclass(frozen=True, slots=True)
class JudgeVerdict:
    """Fresh-model adjudication for one existing investigator finding."""

    finding_id: str
    status: FindingStatus
    rationale: str
    cited_tool_call_ids: tuple[str, ...]
    quoted_spans: tuple[EvidenceQuote, ...]
    annotations: tuple[str, ...] = ()

    def public_dict(self) -> dict[str, JsonValue]:
        data = asdict(self)
        data["status"] = self.status.value
        data["cited_tool_call_ids"] = list(self.cited_tool_call_ids)
        data["quoted_spans"] = [quote.public_dict() for quote in self.quoted_spans]
        data["annotations"] = list(self.annotations)
        return data


@dataclass(slots=True)
class InvestigationState:
    """Mutable run-local scratchpad owned by the investigator controller."""

    case_notes: str = ""
    findings: list[Finding] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    unresolved_questions: list[str] = field(default_factory=list)
    turns: int = 0
