"""End-to-end controller tests with fake model and fake typed forensic tool."""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from conftest import ManualClock
from unchained.agent import (
    AgentProtocolError,
    UnchainedAgent,
    _parse_investigation,
    _parse_verdicts,
)
from unchained.audit import AuditLog
from unchained.caps import CapConfig, CapKind, RunBudget
from unchained.model import ModelRequest
from unchained.models import (
    EvidenceItem,
    EvidenceProfile,
    FindingStatus,
    FunctionCall,
    ModelResponse,
    ModelUsage,
    RunStatus,
)
from unchained.prompts import INVESTIGATOR_PROMPT
from unchained.tools import ToolDefinition, ToolRegistry

EMPTY_PARAMETERS = {
    "type": "object",
    "properties": {},
    "required": [],
    "additionalProperties": False,
}


def profile(tmp_path: Path) -> EvidenceProfile:
    evidence = tmp_path / "memory.bin"
    evidence.write_bytes(b"PAGEDUMP" + b"\0" * 64)
    item = EvidenceItem(
        evidence_id="evidence-001",
        path=evidence,
        kind="memory",
        size=evidence.stat().st_size,
        sha256="0" * 64,
        os_hint="windows",
        health="ready",
        symbols="ready",
    )
    return EvidenceProfile(
        root=tmp_path,
        os="windows",
        shape="memory-only",
        filesystems=(),
        sizes={item.evidence_id: item.size},
        health={item.evidence_id: "ready"},
        symbols={item.evidence_id: "ready"},
        hashes={item.evidence_id: item.sha256},
        available_tool_families=("memory",),
        capability_label="Windows tested path",
        items=(item,),
    )


def tool_definition(
    name: str = "windows.pslist",
    executor: object | None = None,
) -> ToolDefinition:
    run_tool = executor if callable(executor) else lambda arguments: "PID 4 System"
    return ToolDefinition(
        name=name,
        description=f"Return fake records from {name}.",
        parameters=EMPTY_PARAMETERS,
        families=("memory",),
        os_families=("windows",),
        executor=run_tool,
    )


def tool_names(request: ModelRequest) -> set[str]:
    return {
        str(schema.get("name"))
        for schema in request.tools
        if schema.get("type") == "function" and schema.get("name")
    }


@dataclass
class FakeInvestigatorModel:
    """Script decisions from request capabilities without calling a provider."""

    usage: ModelUsage = ModelUsage(input_tokens=10, output_tokens=5)
    always_request_tool: bool = False
    opening_tool_names: tuple[str, ...] = ("windows.pslist",)
    terminal_text: str = "DONE\n"
    done_with_tool: bool = False
    requests: list[ModelRequest] = field(default_factory=list)

    @property
    def model_id(self) -> str:
        return "fake-gpt-5.6"

    def create(self, request: ModelRequest) -> ModelResponse:
        self.requests.append(request)
        index = len(self.requests)
        names = tool_names(request)

        if "submit_judgment" in names:
            return ModelResponse(
                response_id=f"response-{index}",
                function_calls=(
                    FunctionCall(
                        call_id=f"judge-{index}",
                        name="submit_judgment",
                        arguments={
                            "verdicts": [
                                {
                                    "finding_id": "F001",
                                    "status": "UNSUPPORTED",
                                    "rationale": "The cited process list does not prove execution.",
                                    "cited_tool_call_ids": ["opening-tool"],
                                    "annotations": ["Acquire corroborating execution artifacts."],
                                }
                            ]
                        },
                    ),
                ),
                usage=self.usage,
            )

        if not names:
            return ModelResponse(
                response_id=f"response-{index}",
                text=(
                    "## Narrative\n\nThe claimed execution is unsupported [opening-tool].\n\n"
                    "## Findings\n\n"
                    "| ID | Status | Tool calls |\n|---|---|---|\n"
                    "| F001 | UNSUPPORTED | [opening-tool] |\n\n"
                    "## IOC list\n\nNo independently supported IOCs.\n\n"
                    "## Limitations\n\n"
                    "This system has no deterministic validator by design."
                ),
                usage=self.usage,
            )

        if request.phase == "investigation-finalize":
            return ModelResponse(
                response_id=f"response-{index}",
                function_calls=(
                    FunctionCall(
                        call_id=f"done-{index}",
                        name="submit_investigation",
                        arguments={
                            "status": "DONE",
                            "case_notes": (
                                "System is present in the process listing [opening-tool]."
                            ),
                            "findings": [
                                {
                                    "finding_id": "F001",
                                    "title": "Unproven execution claim",
                                    "summary": (
                                        "A process listing was over-interpreted [opening-tool]."
                                    ),
                                    "proposed_status": "CONFIRMED",
                                    "severity": "HIGH",
                                    "tool_call_ids": ["opening-tool"],
                                    "iocs": [],
                                    "limitations": [],
                                }
                            ],
                            "limitations": [],
                            "unresolved_questions": [],
                        },
                    ),
                ),
                usage=self.usage,
            )

        if request.phase == "investigate" and not self.always_request_tool:
            if self.done_with_tool:
                return ModelResponse(
                    response_id=f"response-{index}",
                    text="DONE",
                    function_calls=(
                        FunctionCall(
                            call_id="ambiguous-loop-tool",
                            name="windows.pslist",
                            arguments={},
                        ),
                    ),
                    usage=self.usage,
                )
            return ModelResponse(
                response_id=f"response-{index}",
                text=self.terminal_text,
                usage=self.usage,
            )

        opening_calls = tuple(
            FunctionCall(
                call_id="opening-tool" if offset == 0 else f"opening-tool-{offset + 1}",
                name=name,
                arguments={},
            )
            for offset, name in enumerate(self.opening_tool_names)
        )
        return ModelResponse(
            response_id=f"response-{index}",
            function_calls=(
                opening_calls
                if index == 1
                else (
                    FunctionCall(
                        call_id=f"loop-tool-{index}",
                        name="windows.pslist",
                        arguments={},
                    ),
                )
            ),
            usage=self.usage,
        )


def build_agent(
    tmp_path: Path,
    *,
    model: FakeInvestigatorModel,
    budget: RunBudget,
) -> tuple[UnchainedAgent, AuditLog]:
    audit = AuditLog(tmp_path / "audit.jsonl", "agent-test", fsync=False)
    registry = ToolRegistry(definitions=(tool_definition(),), audit=audit, budget=budget)
    return UnchainedAgent(model=model, tools=registry, audit=audit, budget=budget), audit


def test_fresh_judge_downgrades_deliberately_unsupported_finding(tmp_path: Path) -> None:
    model = FakeInvestigatorModel()
    budget = RunBudget(CapConfig())
    agent, audit = build_agent(tmp_path, model=model, budget=budget)

    try:
        run = agent.run(profile(tmp_path))
    finally:
        audit.close()

    assert run.status is RunStatus.COMPLETE
    assert run.findings[0].proposed_status is FindingStatus.CONFIRMED
    assert run.verdicts[0].finding_id == "F001"
    assert run.verdicts[0].status is FindingStatus.UNSUPPORTED
    assert run.verdicts[0].cited_tool_call_ids == ("opening-tool",)
    assert "no deterministic validator by design" in run.report_markdown.lower()

    judge_requests = [
        request for request in model.requests if "submit_judgment" in tool_names(request)
    ]
    assert len(judge_requests) == 1
    assert judge_requests[0].previous_response_id is None

    phases = [request.phase for request in model.requests]
    assert phases == [
        "opening",
        "investigate",
        "investigation-finalize",
        "judge",
        "report",
    ]
    loop_request = model.requests[1]
    assert loop_request.parallel_tool_calls is False
    assert loop_request.tool_choice == "auto"
    assert "submit_investigation" not in tool_names(loop_request)
    finalizer_request = model.requests[2]
    assert finalizer_request.tool_choice == {
        "type": "function",
        "name": "submit_investigation",
    }
    assert finalizer_request.reasoning_context == "all_turns"
    assert tool_names(finalizer_request) == {"submit_investigation"}
    judge_packet = json.loads(str(model.requests[3].input_items[0]["content"][0]["text"]))
    assert "available_catalog" in judge_packet

    entries = AuditLog.verify(audit.path)
    assert [
        entry["payload"]["phase"] for entry in entries if entry["event_type"] == "model.request"
    ] == ["opening", "investigate", "investigation-finalize", "judge", "report"]
    assert [
        entry["payload"]["phase"] for entry in entries if entry["event_type"] == "model.response"
    ] == ["opening", "investigate", "investigation-finalize", "judge", "report"]
    assert sum(entry["event_type"] == "tool.started" for entry in entries) == 1
    assert sum(entry["event_type"] == "tool.completed" for entry in entries) == 1
    assert sum(entry["event_type"] == "investigator.done" for entry in entries) == 1
    finished = next(entry for entry in entries if entry["event_type"] == "investigator.finished")
    assert finished["payload"]["case_notes"] != "DONE"


def test_investigator_must_end_with_literal_done(tmp_path: Path) -> None:
    model = FakeInvestigatorModel(terminal_text="Investigation complete")
    budget = RunBudget(CapConfig())
    agent, audit = build_agent(tmp_path, model=model, budget=budget)

    try:
        run = agent.run(profile(tmp_path))
    finally:
        audit.close()

    assert run.status is RunStatus.PARTIAL
    assert run.cap is None
    assert run.partial_reason == "investigator without a tool call must output exactly DONE"
    assert all(request.phase != "investigation-finalize" for request in model.requests)


def test_done_cannot_accompany_a_tool_call(tmp_path: Path) -> None:
    model = FakeInvestigatorModel(done_with_tool=True)
    budget = RunBudget(CapConfig())
    agent, audit = build_agent(tmp_path, model=model, budget=budget)

    try:
        run = agent.run(profile(tmp_path))
    finally:
        audit.close()

    assert run.status is RunStatus.PARTIAL
    assert run.partial_reason == "DONE must be the only output and cannot accompany a tool call"
    entries = AuditLog.verify(audit.path)
    assert sum(entry["event_type"] == "tool.started" for entry in entries) == 1
    assert all(
        entry.get("payload", {}).get("tool_call_id") != "ambiguous-loop-tool" for entry in entries
    )


def test_structured_findings_reject_uncited_and_invented_citations() -> None:
    baseline = {
        "status": "DONE",
        "case_notes": "The listing does not establish execution [t17].",
        "findings": [
            {
                "finding_id": "F001",
                "title": "Dead-end execution hypothesis",
                "summary": "The listing does not establish execution [t17].",
                "proposed_status": "UNSUPPORTED",
                "severity": "LOW",
                "tool_call_ids": ["t17"],
                "iocs": [],
                "limitations": [],
            }
        ],
        "limitations": [],
        "unresolved_questions": [],
    }
    parsed = _parse_investigation(baseline, 2, {"t17": "success"})
    assert parsed.findings[0].proposed_status is FindingStatus.UNSUPPORTED

    uncited = {**baseline, "findings": [{**baseline["findings"][0], "tool_call_ids": []}]}
    with pytest.raises(AgentProtocolError, match="has no tool-call citation"):
        _parse_investigation(uncited, 2, {"t17": "success"})

    invented = {
        **baseline,
        "findings": [
            {
                **baseline["findings"][0],
                "summary": "The listing does not establish execution [t17] [invented].",
            }
        ],
    }
    with pytest.raises(AgentProtocolError, match="inline citations do not match"):
        _parse_investigation(invented, 2, {"t17": "success"})


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"rationale": ""}, "without a rationale"),
        ({"cited_tool_call_ids": []}, "without a tool-call citation"),
        ({"cited_tool_call_ids": ["t17", "t17"]}, "duplicated tool-call citations"),
        ({"cited_tool_call_ids": ["t18"]}, "outside F001"),
    ],
)
def test_judge_requires_proof_for_every_verdict(
    tmp_path: Path,
    override: dict[str, object],
    message: str,
) -> None:
    finding = _parse_investigation(
        {
            "status": "DONE",
            "case_notes": "The hypothesis is not established [t17].",
            "findings": [
                {
                    "finding_id": "F001",
                    "title": "Unsupported hypothesis",
                    "summary": "The hypothesis is not established [t17].",
                    "proposed_status": "UNSUPPORTED",
                    "severity": "LOW",
                    "tool_call_ids": ["t17"],
                    "iocs": [],
                    "limitations": [],
                }
            ],
            "limitations": [],
            "unresolved_questions": [],
        },
        2,
        {"t17": "success", "t18": "success"},
    ).findings[0]
    raw_verdict = {
        "finding_id": "F001",
        "status": "UNSUPPORTED",
        "rationale": "The receipt does not prove the hypothesis.",
        "cited_tool_call_ids": ["t17"],
        "annotations": [],
        **override,
    }
    audit_path = tmp_path / f"judge-{message.replace(' ', '-')}.jsonl"
    with (
        AuditLog(audit_path, "judge-proof-test", fsync=False) as audit,
        pytest.raises(AgentProtocolError, match=message),
    ):
        _parse_verdicts(
            {"verdicts": [raw_verdict]},
            (finding,),
            {"t17": "success", "t18": "success"},
            audit,
        )


def test_prompt_two_canonical_rules_are_regression_protected() -> None:
    normalized = " ".join(INVESTIGATOR_PROMPT.split())
    assert "no shell" in normalized
    assert "no internet" in normalized
    assert "up to 6 tools" in normalized
    assert "memory is UNAVAILABLE" in normalized
    assert "[t17]" in normalized
    assert "Dead ends are findings too" in normalized
    assert "single word DONE" in normalized


def test_agent_opening_book_traverses_parallel_batch_path(tmp_path: Path) -> None:
    barrier = threading.Barrier(2, timeout=2.0)
    thread_ids: set[int] = set()
    lock = threading.Lock()

    def synchronized_tool(arguments: dict[str, object]) -> str:
        assert arguments == {}
        with lock:
            thread_ids.add(threading.get_ident())
        barrier.wait()
        return "raw opening output"

    model = FakeInvestigatorModel(opening_tool_names=("windows.pslist", "windows.netscan"))
    budget = RunBudget(CapConfig())
    audit = AuditLog(tmp_path / "audit.jsonl", "opening-agent-test", fsync=False)
    registry = ToolRegistry(
        definitions=(
            tool_definition("windows.pslist", synchronized_tool),
            tool_definition("windows.netscan", synchronized_tool),
        ),
        audit=audit,
        budget=budget,
    )
    agent = UnchainedAgent(model=model, tools=registry, audit=audit, budget=budget)

    try:
        run = agent.run(profile(tmp_path))
    finally:
        audit.close()

    assert run.status is RunStatus.COMPLETE
    assert len(thread_ids) == 2
    opening_events = [
        entry for entry in AuditLog.verify(audit.path) if entry["event_type"] == "opening.completed"
    ]
    assert len(opening_events) == 1
    assert opening_events[0]["payload"]["executed"] == 2


def test_opening_book_runs_each_distinct_function_at_most_once(tmp_path: Path) -> None:
    """Different PID arguments do not turn one function into multiple opening tools."""

    executed: list[dict[str, object]] = []

    @dataclass
    class RepeatedFunctionModel:
        @property
        def model_id(self) -> str:
            return "fake-gpt-5.6"

        def create(self, _request: ModelRequest) -> ModelResponse:
            return ModelResponse(
                response_id="repeat-opening",
                function_calls=(
                    FunctionCall(
                        call_id="pid-one",
                        name="windows.cmdline",
                        arguments={"pid": 1},
                    ),
                    FunctionCall(
                        call_id="pid-two",
                        name="windows.cmdline",
                        arguments={"pid": 2},
                    ),
                ),
                usage=ModelUsage(input_tokens=10, output_tokens=5),
            )

    definition = ToolDefinition(
        name="windows.cmdline",
        description="Return a command line for one PID.",
        parameters={
            "type": "object",
            "properties": {"pid": {"type": "integer"}},
            "required": ["pid"],
            "additionalProperties": False,
        },
        families=("memory",),
        os_families=("windows",),
        executor=lambda arguments: executed.append(arguments) or "cmd.exe",
    )
    audit = AuditLog(tmp_path / "audit.jsonl", "distinct-opening", fsync=False)
    budget = RunBudget(CapConfig())
    registry = ToolRegistry((definition,), audit, budget)
    agent = UnchainedAgent(
        model=RepeatedFunctionModel(),
        tools=registry,
        audit=audit,
        budget=budget,
    )

    try:
        _history, results = agent._opening(profile(tmp_path))  # noqa: SLF001
    finally:
        audit.close()

    assert executed == [{"pid": 1}]
    assert [result.status for result in results] == ["success", "rejected"]
    assert "duplicate opening call" in results[1].output


@pytest.mark.parametrize(
    ("cap_kind", "config_overrides", "usage", "advance_wall"),
    [
        (CapKind.TOOL_CALLS, {"max_tool_calls": 1}, ModelUsage(10, 5), False),
        (CapKind.TOTAL_TOKENS, {"max_total_tokens": 10}, ModelUsage(6, 5), False),
        (
            CapKind.COST_USD,
            {
                "max_cost_usd": 0.50,
                "input_usd_per_million": 1_000_000.0,
                "output_usd_per_million": 1_000_000.0,
            },
            ModelUsage(input_tokens=1),
            False,
        ),
        (CapKind.WALL_SECONDS, {"max_wall_seconds": 1.0}, ModelUsage(10, 5), True),
    ],
)
def test_agent_loop_gracefully_terminates_on_every_cap(
    tmp_path: Path,
    cap_kind: CapKind,
    config_overrides: dict[str, int | float],
    usage: ModelUsage,
    advance_wall: bool,
) -> None:
    values: dict[str, int | float] = {
        "max_tool_calls": 100,
        "max_total_tokens": 1_000_000,
        "max_wall_seconds": 30.0,
        "max_cost_usd": 1_000.0,
    }
    values.update(config_overrides)
    clock = ManualClock()
    budget = RunBudget(CapConfig(**values), clock=clock)
    if advance_wall:
        clock.advance(1.0)
    model = FakeInvestigatorModel(usage=usage, always_request_tool=True)
    agent, audit = build_agent(tmp_path, model=model, budget=budget)

    try:
        run = agent.run(profile(tmp_path))
    finally:
        audit.close()

    assert run.status is RunStatus.PARTIAL
    assert run.cap is not None
    assert run.cap.kind is cap_kind
    assert "PARTIAL" in run.report_markdown
    assert budget.fired is cap_kind
