"""GPT-driven opening, investigation loop, fresh judge, and report phases."""

from __future__ import annotations

import json
import re
import string
from dataclasses import dataclass
from typing import Any

from .audit import AuditLog, canonical_json
from .caps import CapExceeded, RunBudget
from .model import (
    AuditedModel,
    ModelClient,
    ModelProviderError,
    ModelRequest,
    function_output,
    model_response_dict,
)
from .models import (
    EvidenceProfile,
    EvidenceQuote,
    Finding,
    FindingStatus,
    FunctionCall,
    InvestigationState,
    JsonValue,
    JudgeVerdict,
    RunStatus,
    ToolResult,
)
from .prompts import HOSTILE_DATA_RULE, INVESTIGATOR_PROMPT
from .tools import ToolProtocolError, ToolRegistry, tool_catalog


class AgentProtocolError(RuntimeError):
    """Raised when a required structured model action cannot be accepted."""


@dataclass(frozen=True, slots=True)
class AgentRun:
    """Complete controller result returned to the CLI and offline tests."""

    status: RunStatus
    findings: tuple[Finding, ...]
    verdicts: tuple[JudgeVerdict, ...]
    report_markdown: str
    cap: CapExceeded | None = None
    partial_reason: str | None = None


def _submit_investigation_schema() -> dict[str, JsonValue]:
    finding = {
        "type": "object",
        "properties": {
            "finding_id": {"type": "string"},
            "title": {"type": "string"},
            "summary": {"type": "string"},
            "proposed_status": {
                "type": "string",
                "enum": ["CONFIRMED", "NEEDS-REVIEW", "UNSUPPORTED"],
            },
            "severity": {"type": "string"},
            "tool_call_ids": {"type": "array", "items": {"type": "string"}},
            "iocs": {"type": "array", "items": {"type": "string"}},
            "limitations": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "finding_id",
            "title",
            "summary",
            "proposed_status",
            "severity",
            "tool_call_ids",
            "iocs",
            "limitations",
        ],
        "additionalProperties": False,
    }
    return {
        "type": "function",
        "name": "submit_investigation",
        "description": "Finish the investigation and submit case notes and existing findings.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["DONE"]},
                "case_notes": {"type": "string"},
                "findings": {"type": "array", "items": finding},
                "limitations": {"type": "array", "items": {"type": "string"}},
                "unresolved_questions": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "status",
                "case_notes",
                "findings",
                "limitations",
                "unresolved_questions",
            ],
            "additionalProperties": False,
        },
    }


def _submit_judgment_schema() -> dict[str, JsonValue]:
    quoted_span = {
        "type": "object",
        "properties": {
            "tool_call_id": {"type": "string"},
            "text": {"type": "string"},
        },
        "required": ["tool_call_id", "text"],
        "additionalProperties": False,
    }
    verdict = {
        "type": "object",
        "properties": {
            "finding_id": {"type": "string"},
            "status": {
                "type": "string",
                "enum": ["CONFIRMED", "NEEDS-REVIEW", "UNSUPPORTED"],
            },
            "rationale": {"type": "string"},
            "cited_tool_call_ids": {"type": "array", "items": {"type": "string"}},
            "quoted_spans": {"type": "array", "items": quoted_span},
            "annotations": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "finding_id",
            "status",
            "rationale",
            "cited_tool_call_ids",
            "quoted_spans",
            "annotations",
        ],
        "additionalProperties": False,
    }
    return {
        "type": "function",
        "name": "submit_judgment",
        "description": (
            "Adjudicate every supplied finding without creating any new finding. "
            "Keep or downgrade status; never upgrade it."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {"verdicts": {"type": "array", "items": verdict}},
            "required": ["verdicts"],
            "additionalProperties": False,
        },
    }


class UnchainedAgent:
    """Controller that constrains mechanics while leaving forensic judgment to GPT."""

    def __init__(
        self,
        *,
        model: ModelClient,
        tools: ToolRegistry,
        audit: AuditLog,
        budget: RunBudget,
    ) -> None:
        self.model = (
            model if isinstance(model, AuditedModel) else AuditedModel(model, audit, budget)
        )
        self.tools = tools
        self.audit = audit
        self.budget = budget

    def run(self, profile: EvidenceProfile) -> AgentRun:
        """Run all model phases, converting any hard cap into a PARTIAL result."""

        state = InvestigationState()
        findings: tuple[Finding, ...] = ()
        verdicts: tuple[JudgeVerdict, ...] = ()
        self.audit.append(
            "investigation.started",
            {"profile": profile.public_dict(), "budget": self.budget.snapshot().public_dict()},
            actor="investigator",
        )
        try:
            opening_history, opening_results = self._opening(profile)
            state = self._investigate(profile, opening_history, opening_results, state)
            findings = tuple(state.findings)
            verdicts = self._judge(profile, state)
            report = self._report(profile, state, verdicts)
            self.audit.append(
                "investigation.completed",
                {
                    "status": RunStatus.COMPLETE.value,
                    "finding_count": len(findings),
                    "verdict_count": len(verdicts),
                    "budget": self.budget.snapshot().public_dict(),
                },
                actor="investigator",
            )
            return AgentRun(RunStatus.COMPLETE, findings, verdicts, report)
        except CapExceeded as exc:
            self._record_cap(exc)
            report = self._partial_report(profile, state, exc)
            self.audit.append(
                "investigation.completed",
                {
                    "status": RunStatus.PARTIAL.value,
                    "reason": str(exc),
                    "budget": exc.snapshot.public_dict(),
                },
                actor="investigator",
            )
            return AgentRun(
                RunStatus.PARTIAL,
                tuple(state.findings),
                verdicts,
                report,
                cap=exc,
                partial_reason=str(exc),
            )
        except (AgentProtocolError, ModelProviderError, ToolProtocolError) as exc:
            report = self._protocol_partial_report(profile, state, str(exc))
            self.audit.append(
                "investigation.completed",
                {
                    "status": RunStatus.PARTIAL.value,
                    "reason": str(exc),
                    "failure_kind": "model_protocol",
                },
                actor="investigator",
            )
            return AgentRun(
                RunStatus.PARTIAL,
                tuple(state.findings),
                verdicts,
                report,
                partial_reason=str(exc),
            )

    def _opening(
        self,
        profile: EvidenceProfile,
    ) -> tuple[tuple[dict[str, JsonValue], ...], tuple[ToolResult, ...]]:
        instructions = f"""
{INVESTIGATOR_PROMPT}

This is TURN 0, the OPENING BOOK. Choose up to six distinct,
highest-information forensic functions for this exact OS and evidence shape.
Select at least one because this phase starts only when a ready typed function
exists. Use only functions provided in this request. Do not finish, report, or
invent unavailable capability in this turn. The controller will execute accepted
calls concurrently and return every output at once.

{HOSTILE_DATA_RULE}
""".strip()
        packet = {
            "evidence_profile": profile.public_dict(),
            "available_catalog": tool_catalog(self.tools),
        }
        opening_input = _user_input(packet)
        response = self.model.create(
            ModelRequest(
                phase="opening",
                instructions=instructions,
                input_items=opening_input,
                tools=self.tools.schemas(),
                parallel_tool_calls=True,
                tool_choice="required",
                max_output_tokens=8_192,
            )
        )
        if not response.function_calls:
            self.audit.append(
                "model.protocol_error",
                {"phase": "opening", "response": model_response_dict(response)},
                actor="investigator",
            )
            raise AgentProtocolError("opening response selected no forensic tools")

        accepted: list[FunctionCall] = []
        rejected: list[ToolResult] = []
        seen: set[str] = set()
        for call in response.function_calls:
            key = call.name
            reason: str | None = None
            if key in seen:
                reason = "duplicate opening call"
            elif len(accepted) >= 6:
                reason = "opening selection exceeded six calls"
            else:
                try:
                    self.tools.validate(call)
                except ToolProtocolError as exc:
                    reason = str(exc)
            seen.add(key)
            if reason is None:
                accepted.append(call)
            else:
                rejected.append(self.tools.rejected(call, reason))
        if not accepted:
            raise AgentProtocolError("opening response contained no valid available tool")
        executed = self.tools.execute_batch(accepted)
        results_by_call = {result.call_id: result for result in (*executed, *rejected)}
        ordered = tuple(
            results_by_call[call.call_id]
            for call in response.function_calls
            if call.call_id in results_by_call
        )
        self.audit.append(
            "opening.completed",
            {
                "response_id": response.response_id,
                "selected": len(response.function_calls),
                "executed": len(executed),
                "rejected": len(rejected),
                "tool_call_ids": [result.call_id for result in ordered],
            },
            actor="investigator",
        )
        history = tuple(opening_input) + _response_history_items(response)
        return history, ordered

    def _investigate(
        self,
        profile: EvidenceProfile,
        history: tuple[dict[str, JsonValue], ...],
        observations: tuple[ToolResult, ...],
        state: InvestigationState,
    ) -> InvestigationState:
        current_input = [
            *history,
            *(function_output(result.call_id, result.model_output()) for result in observations),
        ]
        available = self.tools.schemas()
        instructions = f"""
{INVESTIGATOR_PROMPT}

Continue the case-level DFIR investigation. For every turn:
1. PLAN what the current evidence leaves unanswered.
2. ACT by calling exactly one provided forensic function when another result
   can still change the conclusions.
3. OBSERVE only the returned data.
4. UPDATE your running case notes before the next decision.

Never call more than one function in a turn. When further calls have stopped
changing the conclusions, return no function call and output exactly DONE, with
no other text. Before that terminal turn, factual statements in visible notes
must cite exact tool_call_ids in square brackets. Distinguish support,
uncertainty, contradiction, tool failure, and absence of records. A zero-record
result is not proof of absence unless coverage is established. Do not claim
analysis from an unavailable capability.

{HOSTILE_DATA_RULE}
""".strip()
        while True:
            self.budget.check()
            response = self.model.create(
                ModelRequest(
                    phase="investigate",
                    instructions=instructions,
                    input_items=current_input,
                    tools=available,
                    parallel_tool_calls=False,
                    tool_choice="auto",
                    previous_response_id=None,
                    max_output_tokens=16_384,
                    reasoning_context="all_turns",
                )
            )
            state.turns += 1
            terminal_done = not response.function_calls and response.text.strip() == "DONE"
            if not response.function_calls:
                if not terminal_done:
                    self.audit.append(
                        "model.protocol_error",
                        {"phase": "investigate", "response": model_response_dict(response)},
                        actor="investigator",
                    )
                    raise AgentProtocolError(
                        "investigator without a tool call must output exactly DONE"
                    )
                current_input.extend(_response_history_items(response))
                self.audit.append(
                    "investigator.done",
                    {"turn": state.turns, "response_id": response.response_id},
                    actor="investigator",
                )
                return self._finalize_investigation(profile, current_input, state)
            if len(response.function_calls) != 1:
                self.audit.append(
                    "model.protocol_error",
                    {"phase": "investigate", "response": model_response_dict(response)},
                    actor="investigator",
                )
                raise AgentProtocolError("investigator must issue exactly one function call")
            call = response.function_calls[0]
            if response.text.strip() == "DONE":
                raise AgentProtocolError(
                    "DONE must be the only output and cannot accompany a tool call"
                )
            if response.text.strip():
                state.case_notes = _append_notes(state.case_notes, response.text.strip())
                self.audit.append(
                    "investigator.notes.updated",
                    {"turn": state.turns, "case_notes": state.case_notes},
                    actor="investigator",
                )
            result = self.tools.execute(call)
            self.audit.append(
                "investigator.action",
                {
                    "turn": state.turns,
                    "tool_call_id": result.call_id,
                    "tool_name": result.tool_name,
                    "status": result.status,
                },
                actor="investigator",
            )
            current_input.extend(_response_history_items(response))
            current_input.append(function_output(result.call_id, result.model_output()))

    def _finalize_investigation(
        self,
        profile: EvidenceProfile,
        history: list[dict[str, JsonValue]],
        state: InvestigationState,
    ) -> InvestigationState:
        """Serialize the already-finished investigation for the fresh judge."""

        receipts = self.audit.tool_receipts()
        instructions = f"""
{INVESTIGATOR_PROMPT}

The investigative loop has ended because you output DONE. Do not resume the
investigation and do not request another forensic tool. Serialize only the
hypotheses, dead ends, limitations, and findings already supported or
contradicted by this run into submit_investigation. Every factual finding
summary must cite each supporting tool-call id inline in square brackets.
CONFIRMED requires affirmative cited output; use NEEDS-REVIEW or UNSUPPORTED
when corroboration is absent or contradictory.

{HOSTILE_DATA_RULE}
""".strip()
        serialization_input = [
            *history,
            *_user_input(
                {
                    "controller_request": "Serialize the completed investigation only.",
                    "evidence_profile": profile.public_dict(),
                    "case_notes_so_far": state.case_notes,
                    "audit_tool_receipts": receipts,
                }
            ),
        ]
        response = self.model.create(
            ModelRequest(
                phase="investigation-finalize",
                instructions=instructions,
                input_items=serialization_input,
                tools=(_submit_investigation_schema(),),
                parallel_tool_calls=False,
                tool_choice={"type": "function", "name": "submit_investigation"},
                max_output_tokens=16_384,
                reasoning_context="all_turns",
            )
        )
        if (
            len(response.function_calls) != 1
            or response.function_calls[0].name != "submit_investigation"
        ):
            raise AgentProtocolError("investigator finalizer did not submit structured findings")
        receipt_statuses = {
            str(receipt.get("tool_call_id")): str(receipt.get("status")) for receipt in receipts
        }
        submitted_arguments = dict(response.function_calls[0].arguments)
        if not submitted_arguments.get("case_notes") and state.case_notes:
            submitted_arguments["case_notes"] = state.case_notes
        completed = _parse_investigation(
            submitted_arguments,
            state.turns,
            receipt_statuses,
        )
        if state.case_notes and not completed.case_notes:
            completed.case_notes = state.case_notes
        state.case_notes = completed.case_notes
        state.findings = completed.findings
        state.limitations = completed.limitations
        state.unresolved_questions = completed.unresolved_questions
        self.audit.append(
            "investigator.finished",
            {
                "turns": completed.turns,
                "case_notes": completed.case_notes,
                "findings": [finding.public_dict() for finding in completed.findings],
                "limitations": completed.limitations,
                "unresolved_questions": completed.unresolved_questions,
            },
            actor="investigator",
        )
        return state

    def _judge(
        self, profile: EvidenceProfile, state: InvestigationState
    ) -> tuple[JudgeVerdict, ...]:
        receipts = self.audit.tool_receipts()
        schema = _submit_judgment_schema()
        instructions = f"""
You are a fresh, adversarial DFIR judge. Re-examine every supplied investigator
finding against the supplied audit receipts. Each receipt exposes a bounded
retained output excerpt, not necessarily the complete native-tool stdout or
stderr. Return exactly one verdict for every existing finding: CONFIRMED,
NEEDS-REVIEW, or UNSUPPORTED. Cite only tool_call_ids present in the receipts.
For every cited call, include at least one quoted_spans object whose text is an
exact, nonempty substring of that receipt's bounded excerpt and is at most 1024
UTF-8 bytes; quote only what you can actually see and explain the proof or gap.
You may keep or downgrade a proposed status and annotate it; never upgrade it
and never add a finding. A parser success, a zero-record result, or a tool error
is not affirmative proof by itself. If both healthy memory and disk evidence
were available, prefer corroboration from both domains before retaining
CONFIRMED; otherwise explain the single-domain limitation explicitly. Never
characterize this review as a full-native-output review unless the receipt
explicitly establishes that scope.

{HOSTILE_DATA_RULE}
""".strip()
        packet = {
            "evidence_profile": profile.public_dict(),
            "case_notes": state.case_notes,
            "findings": [finding.public_dict() for finding in state.findings],
            "audit_tool_receipts": receipts,
            "available_catalog": tool_catalog(self.tools),
        }
        self.audit.append(
            "judge.started",
            {"finding_count": len(state.findings), "receipt_count": len(receipts)},
            actor="judge",
        )
        response = self.model.create(
            ModelRequest(
                phase="judge",
                instructions=instructions,
                input_items=_user_input(packet),
                tools=(schema,),
                parallel_tool_calls=False,
                tool_choice={"type": "function", "name": "submit_judgment"},
                previous_response_id=None,
                max_output_tokens=16_384,
            )
        )
        if (
            len(response.function_calls) != 1
            or response.function_calls[0].name != "submit_judgment"
        ):
            raise AgentProtocolError("fresh judge did not submit one structured judgment")
        verdicts = _parse_verdicts(
            response.function_calls[0].arguments,
            tuple(state.findings),
            {str(receipt.get("tool_call_id")): receipt for receipt in receipts},
            self.audit,
        )
        self.audit.append(
            "judge.completed",
            {"verdicts": [verdict.public_dict() for verdict in verdicts]},
            actor="judge",
        )
        return verdicts

    def _report(
        self,
        profile: EvidenceProfile,
        state: InvestigationState,
        verdicts: tuple[JudgeVerdict, ...],
    ) -> str:
        instructions = f"""
Write the final analyst-facing DFIR report in Markdown. Include an investigative
narrative; a findings table whose rows preserve the supplied judge status and
cite tool-call IDs; an IOC list; and an honest Limitations section. State
explicitly that this system has no deterministic validator by design. Do not
add findings, change judge verdicts, or introduce uncited case facts. Cite every
evidence-derived factual statement inline as [tool-call-id], and render each
findings-table citation in that same bracketed form.

{HOSTILE_DATA_RULE}
""".strip()
        packet = {
            "run_status": RunStatus.COMPLETE.value,
            "evidence_profile": profile.public_dict(),
            "case_notes": state.case_notes,
            "findings": [finding.public_dict() for finding in state.findings],
            "judge_verdicts": [verdict.public_dict() for verdict in verdicts],
            "limitations": state.limitations,
            "unresolved_questions": state.unresolved_questions,
            "audit_tool_receipts": self.audit.tool_receipts(),
        }
        self.audit.append("report.started", {"status": "COMPLETE"}, actor="reporter")
        response = self.model.create(
            ModelRequest(
                phase="report",
                instructions=instructions,
                input_items=_user_input(packet),
                tools=(),
                previous_response_id=None,
                max_output_tokens=32_768,
            )
        )
        body = response.text.strip()
        if not body:
            raise AgentProtocolError("report model returned no Markdown")
        _validate_report_body(body, tuple(state.findings), verdicts)
        body = _sanitize_markdown(body)
        report = f"# Sentinel Unchained DFIR Report - COMPLETE\n\n{body}\n"
        self.audit.append(
            "report.completed",
            {"status": "COMPLETE", "characters": len(report)},
            actor="reporter",
        )
        return report

    def _record_cap(self, exc: CapExceeded) -> None:
        entries = AuditLog.verify(self.audit.path)
        already_recorded = any(
            entry.get("event_type") == "cap.fired"
            and isinstance(entry.get("payload"), dict)
            and entry["payload"].get("kind") == exc.kind.value
            for entry in entries
        )
        if not already_recorded:
            self.audit.append(
                "cap.fired",
                {
                    "kind": exc.kind.value,
                    "detail": exc.detail,
                    "budget": exc.snapshot.public_dict(),
                },
            )

    @staticmethod
    def _partial_report(
        profile: EvidenceProfile, state: InvestigationState, exc: CapExceeded
    ) -> str:
        detail = defang_untrusted_inline(exc.detail)
        return f"""# Sentinel Unchained DFIR Report - PARTIAL

The investigation stopped gracefully because the hard cap `{exc.kind.value}` fired.

## Work preserved

- Evidence route: `{profile.os}` / `{profile.shape}`
- Investigator turns completed: {state.turns}
- Findings submitted before the stop: {len(state.findings)}
- Stop detail: {detail}

## Limitations

This is a PARTIAL report. The judge and/or narrative phase may not have run.
This system has no deterministic validator by design. All retained observations
and model judgments require analyst review against `audit.jsonl`.
"""

    @staticmethod
    def _protocol_partial_report(
        profile: EvidenceProfile, state: InvestigationState, reason: str
    ) -> str:
        safe_reason = defang_untrusted_inline(reason)
        return f"""# Sentinel Unchained DFIR Report - PARTIAL

The model protocol could not complete safely: {safe_reason}

## Work preserved

- Evidence route: `{profile.os}` / `{profile.shape}`
- Investigator turns completed: {state.turns}

## Limitations

The investigation, judge, or report phase is incomplete. This system has no
deterministic validator by design. Review the ordered `audit.jsonl` receipts.
"""


def _user_input(packet: dict[str, Any]) -> list[dict[str, JsonValue]]:
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": canonical_json(packet),
                }
            ],
        }
    ]


def _response_history_items(response: Any) -> tuple[dict[str, JsonValue], ...]:
    """Carry provider output locally so live requests can use ``store=false``."""

    if response.output_items:
        normalized: list[dict[str, JsonValue]] = []
        for item in response.output_items:
            if not isinstance(item, dict):
                continue
            copied = dict(item)
            # Responses output items may carry provider-only lifecycle fields
            # such as ``status``. They are valid in response output but are not
            # valid when the item is replayed as request input.
            if copied.get("type") == "function_call":
                copied.pop("status", None)
            normalized.append(copied)
        return tuple(normalized)
    synthesized: list[dict[str, JsonValue]] = []
    if response.text:
        synthesized.append(
            {
                "role": "assistant",
                "content": [{"type": "output_text", "text": response.text}],
            }
        )
    synthesized.extend(
        {
            "type": "function_call",
            "call_id": call.call_id,
            "name": call.name,
            "arguments": canonical_json(call.arguments),
        }
        for call in response.function_calls
    )
    return tuple(synthesized)


def _append_notes(current: str, update: str) -> str:
    return update if not current else f"{current}\n\n{update}"


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise AgentProtocolError("structured list field has the wrong type")
    return [str(item) for item in value]


def _inline_citations(value: str) -> set[str]:
    """Extract square-bracket tool-call citations from model-authored text."""

    return {match.strip() for match in re.findall(r"\[([^\[\]\r\n]+)\]", value)}


def _parse_investigation(
    arguments: dict[str, JsonValue],
    turns: int,
    receipt_statuses: dict[str, str],
) -> InvestigationState:
    if arguments.get("status") != "DONE":
        raise AgentProtocolError("submit_investigation status must be DONE")
    raw_findings = arguments.get("findings")
    if not isinstance(raw_findings, list):
        raise AgentProtocolError("submit_investigation findings must be a list")
    findings: list[Finding] = []
    identifiers: set[str] = set()
    for index, raw in enumerate(raw_findings, start=1):
        if not isinstance(raw, dict):
            raise AgentProtocolError("each investigation finding must be an object")
        finding = Finding.from_mapping(raw, index)
        if finding.finding_id in identifiers:
            raise AgentProtocolError(f"duplicate finding id: {finding.finding_id}")
        if not finding.tool_call_ids:
            raise AgentProtocolError(
                f"finding {finding.finding_id} has no tool-call citation; "
                "put uncited readiness facts in limitations"
            )
        if len(set(finding.tool_call_ids)) != len(finding.tool_call_ids):
            raise AgentProtocolError(
                f"finding {finding.finding_id} contains duplicate tool-call citations"
            )
        unknown_calls = sorted(set(finding.tool_call_ids) - set(receipt_statuses))
        if unknown_calls:
            raise AgentProtocolError(
                f"finding {finding.finding_id} cites nonexistent tool calls: {unknown_calls}"
            )
        if finding.proposed_status is FindingStatus.CONFIRMED:
            if not finding.tool_call_ids:
                raise AgentProtocolError(
                    f"confirmed finding {finding.finding_id} has no tool-call citation"
                )
            if not any(receipt_statuses[call_id] == "success" for call_id in finding.tool_call_ids):
                raise AgentProtocolError(
                    f"confirmed finding {finding.finding_id} cites no successful tool receipt"
                )
        summary_citations = _inline_citations(finding.summary)
        expected_citations = set(finding.tool_call_ids)
        if summary_citations != expected_citations:
            raise AgentProtocolError(
                f"finding {finding.finding_id} inline citations do not match its "
                f"tool_call_ids: expected {sorted(expected_citations)}, "
                f"got {sorted(summary_citations)}"
            )
        identifiers.add(finding.finding_id)
        findings.append(finding)
    case_notes = str(arguments.get("case_notes") or "")
    if not case_notes.strip():
        raise AgentProtocolError("investigator submitted empty case notes")
    note_citations = _inline_citations(case_notes)
    unknown_note_citations = sorted(note_citations - set(receipt_statuses))
    if unknown_note_citations:
        raise AgentProtocolError(
            f"case notes contain nonexistent tool-call citations: {unknown_note_citations}"
        )
    cited_calls = {call_id for finding in findings for call_id in finding.tool_call_ids}
    missing_from_notes = sorted(cited_calls - note_citations)
    if missing_from_notes:
        raise AgentProtocolError(
            f"case notes lack inline citations for tool calls: {missing_from_notes}"
        )
    return InvestigationState(
        case_notes=case_notes,
        findings=findings,
        limitations=_as_string_list(arguments.get("limitations")),
        unresolved_questions=_as_string_list(arguments.get("unresolved_questions")),
        turns=turns,
    )


def _parse_verdicts(
    arguments: dict[str, JsonValue],
    findings: tuple[Finding, ...],
    receipts_by_call_id: dict[str, dict[str, JsonValue]],
    audit: AuditLog,
) -> tuple[JudgeVerdict, ...]:
    raw_verdicts = arguments.get("verdicts")
    if not isinstance(raw_verdicts, list):
        raise AgentProtocolError("judge verdicts must be a list")
    by_id = {finding.finding_id: finding for finding in findings}
    submitted: dict[str, dict[str, Any]] = {}
    for raw in raw_verdicts:
        if not isinstance(raw, dict):
            raise AgentProtocolError("each judge verdict must be an object")
        finding_id = str(raw.get("finding_id") or "")
        if finding_id not in by_id:
            audit.append(
                "judge.unknown_finding_ignored",
                {"finding_id": finding_id},
                actor="judge-controller",
            )
            continue
        if finding_id in submitted:
            raise AgentProtocolError(f"judge duplicated verdict for {finding_id}")
        submitted[finding_id] = raw
    missing = sorted(set(by_id) - set(submitted))
    if missing:
        raise AgentProtocolError(f"judge omitted findings: {missing}")

    rank = {
        FindingStatus.UNSUPPORTED: 0,
        FindingStatus.NEEDS_REVIEW: 1,
        FindingStatus.CONFIRMED: 2,
    }
    verdicts: list[JudgeVerdict] = []
    for finding in findings:
        raw = submitted[finding.finding_id]
        normalized = str(raw.get("status") or "").upper().replace("_", "-")
        try:
            status = FindingStatus(normalized)
        except ValueError as exc:
            raise AgentProtocolError(
                f"judge returned invalid status for {finding.finding_id}: {normalized}"
            ) from exc
        annotations = _as_string_list(raw.get("annotations"))
        if rank[status] > rank[finding.proposed_status]:
            annotations.append(
                f"Judge upgrade to {status.value} was not applied; retained "
                f"investigator status {finding.proposed_status.value}."
            )
            status = finding.proposed_status
        citations = tuple(_as_string_list(raw.get("cited_tool_call_ids")))
        if len(citations) != len(set(citations)):
            raise AgentProtocolError(
                f"judge duplicated tool-call citations for {finding.finding_id}"
            )
        invalid = sorted(set(citations) - set(receipts_by_call_id))
        if invalid:
            raise AgentProtocolError(
                f"judge cited nonexistent tool calls for {finding.finding_id}: {invalid}"
            )
        unrelated = sorted(set(citations) - set(finding.tool_call_ids))
        if unrelated:
            raise AgentProtocolError(
                f"judge cited receipts outside {finding.finding_id}: {unrelated}"
            )
        if not citations:
            raise AgentProtocolError(
                f"judge returned {status.value} for {finding.finding_id} "
                "without a tool-call citation"
            )
        rationale = str(raw.get("rationale") or "").strip()
        if not rationale:
            raise AgentProtocolError(
                f"judge returned {status.value} for {finding.finding_id} without a rationale"
            )

        raw_quotes = raw.get("quoted_spans")
        if not isinstance(raw_quotes, list):
            raise AgentProtocolError(
                f"judge returned malformed quoted spans for {finding.finding_id}"
            )
        quotes: list[EvidenceQuote] = []
        quote_pairs: set[tuple[str, str]] = set()
        quoted_call_ids: set[str] = set()
        for raw_quote in raw_quotes:
            if not isinstance(raw_quote, dict):
                raise AgentProtocolError(
                    f"judge returned malformed quoted span for {finding.finding_id}"
                )
            quote_call_id = raw_quote.get("tool_call_id")
            quote_text = raw_quote.get("text")
            if not isinstance(quote_call_id, str) or not quote_call_id:
                raise AgentProtocolError(
                    f"judge returned quoted span without a tool-call id for {finding.finding_id}"
                )
            if not isinstance(quote_text, str) or not quote_text.strip():
                raise AgentProtocolError(
                    f"judge returned an empty quoted span for {finding.finding_id}"
                )
            try:
                quote_size = len(quote_text.encode("utf-8"))
            except UnicodeEncodeError as exc:
                raise AgentProtocolError(
                    f"judge returned a non-UTF-8 quoted span for {finding.finding_id}"
                ) from exc
            if quote_size > 1024:
                raise AgentProtocolError(
                    f"judge quoted more than 1024 UTF-8 bytes for {finding.finding_id}"
                )
            if quote_call_id not in citations:
                raise AgentProtocolError(
                    f"judge quoted a call outside its citations for {finding.finding_id}: "
                    f"{quote_call_id}"
                )
            if quote_call_id not in finding.tool_call_ids:
                raise AgentProtocolError(
                    f"judge quoted a receipt outside {finding.finding_id}: {quote_call_id}"
                )
            quote_pair = (quote_call_id, quote_text)
            if quote_pair in quote_pairs:
                raise AgentProtocolError(
                    f"judge duplicated an evidence quote for {finding.finding_id}"
                )
            receipt = receipts_by_call_id[quote_call_id]
            excerpt = receipt.get("output_excerpt")
            if not isinstance(excerpt, str):
                excerpt = receipt.get("output_first_2kb")
            if not isinstance(excerpt, str):
                raise AgentProtocolError(f"receipt {quote_call_id} has no bounded output excerpt")
            if quote_text not in excerpt:
                raise AgentProtocolError(
                    f"judge quote does not resolve in receipt {quote_call_id} "
                    f"for {finding.finding_id}"
                )
            quote_pairs.add(quote_pair)
            quoted_call_ids.add(quote_call_id)
            quotes.append(EvidenceQuote(tool_call_id=quote_call_id, text=quote_text))
        unquoted_citations = sorted(set(citations) - quoted_call_ids)
        if unquoted_citations:
            raise AgentProtocolError(
                f"judge omitted exact evidence quotes for {finding.finding_id}: "
                f"{unquoted_citations}"
            )
        if status is FindingStatus.CONFIRMED and not any(
            str(receipts_by_call_id[call_id].get("status")) == "success" for call_id in citations
        ):
            raise AgentProtocolError(
                f"judge confirmed {finding.finding_id} without a successful receipt"
            )
        verdicts.append(
            JudgeVerdict(
                finding_id=finding.finding_id,
                status=status,
                rationale=rationale,
                cited_tool_call_ids=citations,
                quoted_spans=tuple(quotes),
                annotations=tuple(annotations),
            )
        )
    return tuple(verdicts)


def _validate_report_body(
    body: str,
    findings: tuple[Finding, ...],
    verdicts: tuple[JudgeVerdict, ...],
) -> None:
    """Enforce report structure and reference integrity, not forensic truth."""

    lowered = body.lower()
    sections = _markdown_sections(body)
    required_sections = ("narrative", "findings", "ioc", "limitations")
    missing_sections = [name for name in required_sections if name not in sections]
    if missing_sections:
        raise AgentProtocolError(f"report omitted required Markdown sections: {missing_sections}")
    if not sections["narrative"].strip():
        raise AgentProtocolError("report investigative narrative is empty")
    if not sections["ioc"].strip():
        raise AgentProtocolError("report IOC list is empty; use an explicit none-found statement")
    if not sections["limitations"].strip():
        raise AgentProtocolError("report Limitations section is empty")
    findings_section = sections["findings"]
    table_lines = [line.strip() for line in findings_section.splitlines() if line.strip()]
    if len(table_lines) < 3 or not any(_is_markdown_table_separator(line) for line in table_lines):
        raise AgentProtocolError("report findings section is not a Markdown table")
    header = next((line for line in table_lines if "|" in line), "").casefold()
    if "status" not in header or "tool" not in header:
        raise AgentProtocolError("report findings table lacks status/tool-call columns")
    verdict_by_id = {verdict.finding_id: verdict for verdict in verdicts}
    rows: dict[str, str] = {}
    for finding in findings:
        matching = [line for line in table_lines if _table_cell_present(line, finding.finding_id)]
        if len(matching) != 1:
            raise AgentProtocolError(
                f"report findings table must contain exactly one row for {finding.finding_id}"
            )
        rows[finding.finding_id] = matching[0]
    if "no deterministic validator by design" not in lowered:
        raise AgentProtocolError("report omitted the no-deterministic-validator limitation")
    for finding in findings:
        row = rows[finding.finding_id]
        verdict = verdict_by_id[finding.finding_id]
        if verdict.status.value not in row:
            raise AgentProtocolError(
                f"report row for {finding.finding_id} omitted judge status {verdict.status.value}"
            )
        for call_id in finding.tool_call_ids:
            if f"[{call_id}]" not in row:
                raise AgentProtocolError(
                    f"report row for {finding.finding_id} omitted inline citation [{call_id}]"
                )
    for verdict in verdicts:
        for call_id in verdict.cited_tool_call_ids:
            if call_id not in rows[verdict.finding_id]:
                raise AgentProtocolError(
                    f"report row for {verdict.finding_id} omitted judge citation {call_id}"
                )
    known_ids = {finding.finding_id for finding in findings}
    report_ids = set(re.findall(r"\bF\d{3,}\b", body))
    unknown_ids = sorted(report_ids - known_ids)
    if unknown_ids:
        raise AgentProtocolError(f"report introduced unknown finding IDs: {unknown_ids}")


def _sanitize_markdown(body: str) -> str:
    """Render model-authored Markdown as a fail-closed, link-free safe subset.

    Parsing links and images with regular expressions is unsafe because
    CommonMark permits escapes, nesting, reference forms, and error recovery.
    Instead, make every bracket data rather than Markdown punctuation.  This
    preserves visible citations such as ``[t17]`` and leaves headings, lists,
    emphasis, and tables readable, while making *all* Markdown link and image
    forms structurally impossible.  Ampersands are escaped first so an
    attacker cannot smuggle a delimiter or raw HTML through a character
    reference.
    """

    sanitized = re.sub(
        r"(?i)\b([a-z][a-z0-9+.-]{1,31})://",
        lambda match: f"{match.group(1)}[:]//",
        body,
    )
    sanitized = re.sub(
        r"(?i)\b(javascript|vbscript|data|file|mailto):",
        lambda match: f"blocked-{match.group(1).casefold()}[:]",
        sanitized,
    )
    sanitized = re.sub(r"(?<![:/])//(?=[a-z0-9])", "/ /", sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r"(?i)\bwww\.", "www[.]", sanitized)
    sanitized = re.sub(
        r"(?i)(?<=\w)@(?=[a-z0-9.-]+\.[a-z]{2,63}\b)",
        "[at]",
        sanitized,
    )

    sanitized = sanitized.replace("&", "&amp;")
    sanitized = sanitized.replace("<", "&lt;").replace(">", "&gt;")
    return sanitized.replace("[", "&#91;").replace("]", "&#93;")


def defang_untrusted_inline(value: object) -> str:
    """Render hostile diagnostics as one inert, visibly escaped Markdown line."""

    # JSON escaping makes every control/newline visible instead of structural.
    serialized = json.dumps(str(value), ensure_ascii=False)[1:-1]
    sanitized = _sanitize_markdown(serialized)
    return re.sub(f"([{re.escape(string.punctuation)}])", r"\\\1", sanitized)


def _markdown_sections(body: str) -> dict[str, str]:
    """Return normalized required section bodies from Markdown headings."""

    matches = list(re.finditer(r"(?im)^#{1,6}\s+([^\r\n#]+?)\s*$", body))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        title = match.group(1).strip().casefold()
        key: str | None = None
        if "narrative" in title:
            key = "narrative"
        elif "finding" in title:
            key = "findings"
        elif re.search(r"\bioc\b", title):
            key = "ioc"
        elif "limitation" in title:
            key = "limitations"
        if key is None or key in sections:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[key] = body[match.end() : end]
    return sections


def _is_markdown_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip("|").split("|")]
    return len(cells) >= 2 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _table_cell_present(line: str, expected: str) -> bool:
    cells = [cell.strip() for cell in line.strip("|").split("|")]
    return expected in cells
