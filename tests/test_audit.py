"""Audit completeness, ordering, excerpts, and hash-chain verification."""

from __future__ import annotations

import hashlib
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import pytest

from unchained.audit import GENESIS_HASH, AuditIntegrityError, AuditLog, canonical_json
from unchained.models import FunctionCall, ModelResponse, ModelUsage, ToolResult


def completed_tool(output: str, *, call_id: str = "call-001") -> ToolResult:
    """Create one deterministic fake tool receipt."""

    return ToolResult(
        call_id=call_id,
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
            requested_model="fake-gpt-5.6",
            instructions="Use only the provided tools.",
            input_items=[{"role": "user", "content": "bounded profile"}],
            tools=[{"type": "function", "name": "windows.pslist"}],
            previous_response_id=None,
        )
        audit.model_response(
            phase="opening-book",
            requested_model="fake-gpt-5.6",
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
    assert tool_payload["output_bytes"] == len(output.encode("utf-8"))
    assert tool_payload["output_encoding"] == "utf-8"
    assert tool_payload["output_media_type"] == "text/plain"
    assert tool_payload["accepted_output_complete"] is True
    assert tool_payload["output_artifact_path"] == (f"tool-outputs/{result.output_sha256}.txt")
    assert tool_payload["output_artifact"] == {
        "bytes": len(output.encode("utf-8")),
        "complete": True,
        "encoding": "utf-8",
        "media_type": "text/plain",
        "path": f"tool-outputs/{result.output_sha256}.txt",
        "sha256": result.output_sha256,
    }
    assert tool_payload["output_excerpt"] == tool_payload["output_first_2kb"]
    assert tool_payload["output_excerpt_bytes"] == 2_048
    assert tool_payload["output_excerpt_limit_bytes"] == 2_048
    assert tool_payload["output_excerpt_kind"] == "utf-8-byte-prefix"
    assert "output" not in tool_payload

    artifact = path.parent / tool_payload["output_artifact_path"]
    assert artifact.is_file()
    assert not artifact.is_symlink()
    assert artifact.read_bytes() == output.encode("utf-8")
    assert hashlib.sha256(artifact.read_bytes()).hexdigest() == result.output_sha256


def test_content_addressed_output_is_concurrent_duplicate_safe(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    output = '{"rows":[' + ",".join(str(number) for number in range(1_000)) + "]}"
    results = tuple(completed_tool(output, call_id=f"call-{number:03d}") for number in range(12))

    with (
        AuditLog(path, "run-001", fsync=False) as audit,
        ThreadPoolExecutor(max_workers=12) as pool,
    ):
        tuple(pool.map(audit.tool_completed, results))

    digest = hashlib.sha256(output.encode("utf-8")).hexdigest()
    output_directory = tmp_path / "tool-outputs"
    assert [artifact.name for artifact in output_directory.iterdir()] == [f"{digest}.json"]
    assert (output_directory / f"{digest}.json").read_bytes() == output.encode("utf-8")

    entries = AuditLog.verify(path)
    assert len(entries) == len(results)
    assert {entry["payload"]["tool_call_id"] for entry in entries} == {
        result.call_id for result in results
    }
    assert all(entry["payload"]["output_media_type"] == "application/json" for entry in entries)
    assert all(
        entry["payload"]["output_artifact_path"] == f"tool-outputs/{digest}.json"
        for entry in entries
    )


def test_hash_mismatch_fails_closed_without_completion_event(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    result = replace(completed_tool("exact output"), output_sha256="0" * 64)

    with (
        AuditLog(path, "run-001", fsync=False) as audit,
        pytest.raises(AuditIntegrityError, match="SHA-256 mismatch"),
    ):
        audit.tool_completed(result)

    entries = AuditLog.verify(path)
    assert [entry["event_type"] for entry in entries] == ["tool.output_persistence_failed"]
    assert entries[0]["payload"]["claimed_output_sha256"] == "0" * 64
    assert (
        entries[0]["payload"]["actual_output_sha256"]
        == completed_tool("exact output").output_sha256
    )
    assert not (tmp_path / "tool-outputs").exists()


def test_hash_value_cannot_traverse_outside_artifact_directory(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    result = replace(completed_tool("exact output"), output_sha256="../../outside")

    with (
        AuditLog(path, "run-001", fsync=False) as audit,
        pytest.raises(AuditIntegrityError, match="SHA-256 mismatch"),
    ):
        audit.tool_completed(result)

    assert [entry["event_type"] for entry in AuditLog.verify(path)] == [
        "tool.output_persistence_failed"
    ]
    assert not (tmp_path / "outside").exists()
    assert not (tmp_path / "tool-outputs").exists()


def test_preexisting_symlink_artifact_is_rejected_without_following_it(tmp_path: Path) -> None:
    if not hasattr(os, "symlink"):
        pytest.skip("host does not expose symbolic links")

    path = tmp_path / "audit.jsonl"
    result = completed_tool("do not write through this link")
    output_directory = tmp_path / "tool-outputs"
    output_directory.mkdir()
    victim = tmp_path / "victim.txt"
    victim.write_text("unchanged", encoding="utf-8")
    artifact = output_directory / f"{result.output_sha256}.txt"
    try:
        artifact.symlink_to(victim)
    except OSError as exc:
        pytest.skip(f"host does not permit symbolic links: {exc}")

    with (
        AuditLog(path, "run-001", fsync=False) as audit,
        pytest.raises(AuditIntegrityError, match="not a regular file"),
    ):
        audit.tool_completed(result)

    assert victim.read_text(encoding="utf-8") == "unchanged"
    assert artifact.is_symlink()
    assert [entry["event_type"] for entry in AuditLog.verify(path)] == [
        "tool.output_persistence_failed"
    ]
    assert not any(candidate.name.endswith(".tmp") for candidate in output_directory.iterdir())


def test_tool_output_excerpt_never_splits_utf8_code_point(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    output = "€" * 1_000

    with AuditLog(path, "run-001", fsync=False) as audit:
        audit.tool_completed(completed_tool(output))

    payload = AuditLog.verify(path)[0]["payload"]
    excerpt = payload["output_excerpt"]
    assert excerpt == "€" * 682
    assert "�" not in excerpt
    assert payload["output_excerpt_bytes"] == len(excerpt.encode("utf-8")) == 2_046
    assert payload["output_excerpt_limit_bytes"] == 2_048


def test_canonical_json_rejects_nonstandard_nan() -> None:
    with pytest.raises(ValueError, match="Out of range float values"):
        canonical_json({"invalid": float("nan")})


def test_audit_verifier_detects_post_run_tampering(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    with AuditLog(path, "run-001", fsync=False) as audit:
        audit.append("run.started", {"status": "running"})

    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace("running", "tampered"), encoding="utf-8")

    with pytest.raises(AuditIntegrityError, match="entry hash mismatch"):
        AuditLog.verify(path)
