"""Application-level append-only, hash-chained JSONL audit writer."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import threading
import time
import uuid
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import JsonValue, ModelResponse, ToolResult

GENESIS_HASH = "0" * 64


class AuditIntegrityError(RuntimeError):
    """Raised when an existing JSONL chain cannot be verified."""


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _jsonable(value: Any) -> JsonValue:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value) and not isinstance(value, type):
        return _jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return _jsonable(model_dump(mode="json"))
    return str(value)


def canonical_json(value: Any) -> str:
    """Serialize consistently for hashing and one-record writes."""

    return json.dumps(_jsonable(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def first_2kb(value: str) -> str:
    raw = value.encode("utf-8", errors="replace")[:2048]
    return raw.decode("utf-8", errors="replace")


class AuditLog:
    """Serialize all writers through one lock and append records with a hash chain.

    The hash chain detects accidental or post-run local changes. It is not an
    external immutability guarantee against an administrator able to rewrite the
    complete run directory; that boundary is stated explicitly in DECISIONS.md.
    """

    def __init__(self, path: Path, run_id: str, *, fsync: bool = True) -> None:
        self.path = path
        self.run_id = run_id
        self._fsync = fsync
        self._lock = threading.Lock()
        self._started = time.monotonic()
        self._sequence = 0
        self._previous_hash = GENESIS_HASH
        path.parent.mkdir(parents=True, exist_ok=True)
        existed = path.exists()
        if existed and path.stat().st_size:
            entries = self.verify(path)
            self._sequence = int(entries[-1]["sequence"])
            self._previous_hash = str(entries[-1]["entry_hash"])
        flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)
        if not existed:
            flags |= os.O_EXCL
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        self._fd = os.open(path, flags, 0o600)
        if not stat.S_ISREG(os.fstat(self._fd).st_mode):
            os.close(self._fd)
            self._fd = -1
            raise AuditIntegrityError("audit target is not a regular file")

    def close(self) -> None:
        with self._lock:
            if self._fd >= 0:
                if self._fsync:
                    os.fsync(self._fd)
                os.close(self._fd)
                self._fd = -1

    def __enter__(self) -> AuditLog:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def append(
        self,
        event_type: str,
        payload: Any,
        *,
        actor: str = "runner",
    ) -> dict[str, JsonValue]:
        """Append exactly one canonical JSON record and return its in-memory form."""

        with self._lock:
            if self._fd < 0:
                raise RuntimeError("audit log is closed")
            sequence = self._sequence + 1
            base: dict[str, JsonValue] = {
                "schema_version": 1,
                "run_id": self.run_id,
                "sequence": sequence,
                "event_id": str(uuid.uuid4()),
                "event_type": event_type,
                "actor": actor,
                "timestamp_utc": utc_now(),
                "elapsed_ms": int((time.monotonic() - self._started) * 1000),
                "previous_hash": self._previous_hash,
                "payload": _jsonable(payload),
            }
            digest = sha256_text(canonical_json(base))
            record = {**base, "entry_hash": digest}
            encoded = (canonical_json(record) + "\n").encode("utf-8")
            offset = 0
            while offset < len(encoded):
                written = os.write(self._fd, encoded[offset:])
                if written <= 0:
                    raise OSError(f"short audit write: {offset}/{len(encoded)} bytes")
                offset += written
            if self._fsync:
                os.fsync(self._fd)
            self._sequence = sequence
            self._previous_hash = digest
            return record

    def model_request(
        self,
        *,
        phase: str,
        model: str,
        instructions: str,
        input_items: Any,
        tools: Any,
        previous_response_id: str | None,
    ) -> None:
        """Record the request with raw tool outputs reduced to bounded receipts."""

        self.append(
            "model.request",
            {
                "phase": phase,
                "model": model,
                "instructions": instructions,
                "input": input_items,
                "tools": tools,
                "previous_response_id": previous_response_id,
            },
            actor="model-client",
        )

    def model_response(
        self,
        *,
        phase: str,
        model: str,
        response: ModelResponse,
        call_cost_usd: float,
        running_cost_usd: float,
    ) -> None:
        """Record every normalized model message, function call, and usage counter."""

        self.append(
            "model.response",
            {
                "phase": phase,
                "model": model,
                "response_id": response.response_id,
                "request_id": response.request_id,
                "status": response.status,
                "incomplete_details": response.incomplete_details,
                "error": response.error,
                "message": response.text,
                "function_calls": [asdict(call) for call in response.function_calls],
                "output_items": list(response.output_items),
                "token_counts": asdict(response.usage),
                "usage_error": response.usage_error,
                "call_cost_usd_estimate": call_cost_usd,
                "running_cost_usd_estimate": running_cost_usd,
            },
            actor="model-client",
        )

    def tool_started(self, call_id: str, name: str, arguments: Any) -> None:
        self.append(
            "tool.started",
            {"tool_call_id": call_id, "tool_name": name, "arguments": arguments},
            actor="tool-runner",
        )

    def tool_completed(self, result: ToolResult) -> None:
        self.append(
            "tool.completed",
            {
                "tool_call_id": result.call_id,
                "tool_name": result.tool_name,
                "arguments": result.arguments,
                "status": result.status,
                "started_at": result.started_at,
                "ended_at": result.ended_at,
                "duration_ms": result.duration_ms,
                "output_sha256": result.output_sha256,
                "output_first_2kb": first_2kb(result.output),
                "error": result.error,
            },
            actor="tool-runner",
        )

    def tool_receipts(self) -> list[dict[str, JsonValue]]:
        """Return completed call receipts suitable for the fresh judge packet."""

        return [
            entry["payload"]
            for entry in self.verify(self.path)
            if entry.get("event_type") == "tool.completed"
            and isinstance(entry.get("payload"), dict)
        ]

    @staticmethod
    def verify(path: Path) -> list[dict[str, JsonValue]]:
        """Verify sequence, previous-hash links, and every entry digest."""

        entries: list[dict[str, JsonValue]] = []
        previous = GENESIS_HASH
        with path.open("r", encoding="utf-8") as handle:
            for expected, line in enumerate(handle, start=1):
                if not line.endswith("\n"):
                    raise AuditIntegrityError(f"incomplete JSONL record at line {expected}")
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise AuditIntegrityError(f"invalid JSON at line {expected}: {exc}") from exc
                if record.get("sequence") != expected:
                    raise AuditIntegrityError(f"sequence mismatch at line {expected}")
                if record.get("previous_hash") != previous:
                    raise AuditIntegrityError(f"hash-link mismatch at line {expected}")
                actual = record.get("entry_hash")
                unsigned = {key: value for key, value in record.items() if key != "entry_hash"}
                expected_hash = sha256_text(canonical_json(unsigned))
                if actual != expected_hash:
                    raise AuditIntegrityError(f"entry hash mismatch at line {expected}")
                previous = str(actual)
                entries.append(record)
        return entries
