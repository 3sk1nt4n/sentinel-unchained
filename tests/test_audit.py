"""Audit completeness, ordering, excerpts, and hash-chain verification."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from unchained.audit import GENESIS_HASH, AuditIntegrityError, AuditLog
from unchained.models import FunctionCall, ModelResponse, ModelUsage, ToolResult


def completed_tool(output: str) -> ToolResult:
    """Create one deterministic fake tool receipt."""

    return ToolResult(
        call_id="call-001",
        tool_name="windows.pslist",
        arguments={"pid": None},
        output=output,
        output_sha256=hashlib.sha256(output.encode()).hexdigest(),
        status="success",
        started_at="2026-01-01T00:00:00+00:00",
        ended_at="2026-01-01T00:00:00.010000+00:00",
        duration_ms=10,
    )


def test_audit_is_complete_ordered_and_hash_chained(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    output = "x" * 3_000
    response = ModelResponse(
        response_id="resp-001",
        text="Inspecting the process tree.",
        function_calls=(
            FunctionCall(call_id="call-001", name="windows.pslist", arguments={"pid": None}),
        ),
        usage=ModelUsage(input_tokens=80, output_tokens=20, cached_input_tokens=30),
    )
    result = completed_tool(output)

    with AuditLog(path, "run-001", fsync=False) as audit:
        audit.model_request(
            phase="opening-book",
            model="fake-gpt-5.6",
            instructions="Use only the provided tools.",
            input_items=[{"role": "user", "content": "bounded profile"}],
            tools=[{"type": "function", "name": "windows.pslist"}],
            previous_response_id=None,
        )
        audit.model_response(
            phase="opening-book",
            model="fake-gpt-5.6",
            response=response,
            call_cost_usd=0.001,
            running_cost_usd=0.001,
        )
        audit.tool_started(result.call_id, result.tool_name, result.arguments)
        audit.tool_completed(result)

    entries = AuditLog.verify(path)
    assert [entry["sequence"] for entry in entries] == [1, 2, 3, 4]
    assert [entry["event_type"] for entry in entries] == [
        "model.request",
        "model.response",
        "tool.started",
        "tool.completed",
    ]
    assert entries[0]["previous_hash"] == GENESIS_HASH
    assert all(
        later["previous_hash"] == earlier["entry_hash"]
        for earlier, later in zip(entries[:-1], entries[1:], strict=True)
    )

    model_payload = entries[1]["payload"]
    assert model_payload["message"] == response.text
    assert model_payload["function_calls"][0]["call_id"] == "call-001"
    assert model_payload["token_counts"] == {
        "cached_input_tokens": 30,
        "cache_write_tokens": 0,
        "input_tokens": 80,
        "output_tokens": 20,
        "provider_total_tokens": 0,
        "reasoning_tokens": 0,
    }

    tool_payload = entries[3]["payload"]
    assert tool_payload["arguments"] == {"pid": None}
    assert tool_payload["output_sha256"] == result.output_sha256
    assert len(tool_payload["output_first_2kb"].encode()) == 2_048
    assert "output" not in tool_payload


def test_audit_verifier_detects_post_run_tampering(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    with AuditLog(path, "run-001", fsync=False) as audit:
        audit.append("run.started", {"status": "running"})

    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace("running", "tampered"), encoding="utf-8")

    with pytest.raises(AuditIntegrityError, match="entry hash mismatch"):
        AuditLog.verify(path)
