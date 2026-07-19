"""Application-level append-only, hash-chained JSONL audit writer."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import threading
import time
import uuid
from contextlib import suppress
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import JsonValue, ModelResponse, ToolResult

GENESIS_HASH = "0" * 64
TOOL_OUTPUT_DIRECTORY = "tool-outputs"
OUTPUT_EXCERPT_LIMIT_BYTES = 2048


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

    return json.dumps(
        _jsonable(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def first_2kb(value: str) -> str:
    """Return the longest valid UTF-8 text prefix within the byte limit."""

    raw = value.encode("utf-8", errors="replace")[:OUTPUT_EXCERPT_LIMIT_BYTES]
    return raw.decode("utf-8", errors="ignore")


def _output_format(output: str) -> tuple[str, str]:
    """Return a deterministic, safe suffix and media type for exact output bytes."""

    try:
        json.loads(output)
    except (json.JSONDecodeError, RecursionError):
        return ".txt", "text/plain"
    return ".json", "application/json"


def _write_all(fd: int, content: bytes) -> None:
    """Write all bytes to an already secured file descriptor."""

    offset = 0
    while offset < len(content):
        written = os.write(fd, content[offset:])
        if written <= 0:
            raise OSError(f"short artifact write: {offset}/{len(content)} bytes")
        offset += written


def _best_effort_chmod(path: Path, mode: int) -> None:
    """Restrict a receipt artifact where the host filesystem supports modes."""

    with suppress(NotImplementedError, OSError):
        path.chmod(mode, follow_symlinks=False)


def _fsync_directory(path: Path) -> None:
    """Best-effort durability barrier for a newly linked directory entry."""

    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


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
        requested_model: str,
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
                "requested_model": requested_model,
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
        requested_model: str,
        response: ModelResponse,
        call_cost_usd: float,
        running_cost_usd: float,
    ) -> None:
        """Record canonical controller-visible response fields and observed usage.

        Raw provider ``output_items`` are intentionally excluded. They are an SDK
        transport representation from which the adapter derives canonical
        ``message`` and parsed ``function_calls`` fields. Retaining both as proof
        authorities would create an avoidable contradiction surface.
        """

        self.append(
            "model.response",
            {
                "phase": phase,
                "requested_model": requested_model,
                "provider_model": response.provider_model,
                "response_id": response.response_id,
                "request_id": response.request_id,
                "status": response.status,
                "incomplete_details": response.incomplete_details,
                "error": response.error,
                "message": response.text,
                "function_calls": [asdict(call) for call in response.function_calls],
                "token_counts": asdict(response.usage),
                "usage_error": response.usage_error,
                "call_cost_usd_estimate": call_cost_usd,
                "running_cost_usd_estimate": running_cost_usd,
            },
            actor="model-client",
        )

    def tool_started(
        self,
        call_id: str,
        name: str,
        arguments: Any,
        *,
        evidence_refs: Any = (),
    ) -> None:
        self.append(
            "tool.started",
            {
                "tool_call_id": call_id,
                "tool_name": name,
                "arguments": arguments,
                "evidence_refs": evidence_refs,
            },
            actor="tool-runner",
        )

    def tool_completed(self, result: ToolResult, *, evidence_refs: Any = ()) -> None:
        try:
            artifact = self._persist_tool_output(result)
        except Exception as exc:
            self._record_output_persistence_failure(result, exc, evidence_refs=evidence_refs)
            raise
        excerpt = first_2kb(result.output)
        artifact_receipt: dict[str, JsonValue] = {
            "path": artifact["path"],
            "sha256": artifact["sha256"],
            "bytes": artifact["byte_count"],
            "encoding": "utf-8",
            "media_type": artifact["media_type"],
            "complete": True,
        }
        self.append(
            "tool.completed",
            {
                "tool_call_id": result.call_id,
                "tool_name": result.tool_name,
                "arguments": result.arguments,
                "evidence_refs": evidence_refs,
                "status": result.status,
                "started_at": result.started_at,
                "ended_at": result.ended_at,
                "duration_ms": result.duration_ms,
                "output_sha256": artifact["sha256"],
                "output_first_2kb": excerpt,
                "output_excerpt": excerpt,
                "output_excerpt_bytes": len(excerpt.encode("utf-8")),
                "output_excerpt_limit_bytes": OUTPUT_EXCERPT_LIMIT_BYTES,
                "output_excerpt_kind": "utf-8-byte-prefix",
                "output_artifact": artifact_receipt,
                "output_artifact_path": artifact["path"],
                "output_bytes": artifact["byte_count"],
                "output_encoding": "utf-8",
                "output_media_type": artifact["media_type"],
                "accepted_output_complete": True,
                "error": result.error,
            },
            actor="tool-runner",
        )

    def _record_output_persistence_failure(
        self,
        result: ToolResult,
        error: Exception,
        *,
        evidence_refs: Any = (),
    ) -> None:
        """Record a bounded failure receipt without masking the persistence error."""

        actual_digest: str | None = None
        byte_count: int | None = None
        try:
            content = result.output.encode("utf-8")
            actual_digest = hashlib.sha256(content).hexdigest()
            byte_count = len(content)
        except UnicodeEncodeError:
            pass
        with suppress(Exception):
            self.append(
                "tool.output_persistence_failed",
                {
                    "tool_call_id": result.call_id,
                    "tool_name": result.tool_name,
                    "arguments": result.arguments,
                    "evidence_refs": evidence_refs,
                    "status": result.status,
                    "claimed_output_sha256": result.output_sha256,
                    "actual_output_sha256": actual_digest,
                    "output_bytes": byte_count,
                    "error_type": type(error).__name__,
                    "error": str(error),
                },
                actor="tool-runner",
            )

    def _persist_tool_output(self, result: ToolResult) -> dict[str, str | int]:
        """Persist exact tool output before its completion event can be accepted."""

        try:
            content = result.output.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise AuditIntegrityError("tool output is not valid UTF-8 text") from exc

        actual_digest = hashlib.sha256(content).hexdigest()
        expected_digest = result.output_sha256
        if (
            len(expected_digest) != 64
            or any(character not in "0123456789abcdefABCDEF" for character in expected_digest)
            or expected_digest.lower() != actual_digest
        ):
            raise AuditIntegrityError(
                "tool output SHA-256 mismatch: completion receipt was not appended"
            )

        suffix, media_type = _output_format(result.output)
        directory = self.path.parent / TOOL_OUTPUT_DIRECTORY
        self._ensure_artifact_directory(directory)
        filename = f"{actual_digest}{suffix}"
        destination = directory / filename
        self._install_content_addressed(destination, content)
        return {
            "path": f"{TOOL_OUTPUT_DIRECTORY}/{filename}",
            "sha256": actual_digest,
            "byte_count": len(content),
            "media_type": media_type,
        }

    @staticmethod
    def _ensure_artifact_directory(directory: Path) -> None:
        """Create the output directory, rejecting links and non-directories."""

        with suppress(FileExistsError):
            os.mkdir(directory, 0o700)
        try:
            info = directory.lstat()
        except FileNotFoundError as exc:
            raise AuditIntegrityError("tool-output directory disappeared") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise AuditIntegrityError("tool-output path is not a real directory")
        _best_effort_chmod(directory, 0o700)

    def _install_content_addressed(self, destination: Path, content: bytes) -> None:
        """Atomically install one immutable blob or validate an existing duplicate."""

        directory = destination.parent
        temporary = directory / f".{destination.name}.{uuid.uuid4().hex}.tmp"
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        fd = os.open(temporary, flags, 0o600)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise AuditIntegrityError("temporary tool output is not a regular file")
            _write_all(fd, content)
            if self._fsync:
                os.fsync(fd)
        except BaseException:
            os.close(fd)
            temporary.unlink(missing_ok=True)
            raise
        else:
            os.close(fd)

        _best_effort_chmod(temporary, 0o600)
        try:
            try:
                os.link(temporary, destination, follow_symlinks=False)
            except FileExistsError:
                self._verify_existing_artifact(destination, content)
            else:
                _best_effort_chmod(destination, 0o600)
                if self._fsync:
                    _fsync_directory(directory)
        finally:
            temporary.unlink(missing_ok=True)

    @staticmethod
    def _verify_existing_artifact(destination: Path, expected: bytes) -> None:
        """Accept a concurrent duplicate only when it is the same regular file bytes."""

        try:
            path_info = destination.lstat()
        except FileNotFoundError as exc:
            raise AuditIntegrityError("content-addressed tool output disappeared") from exc
        if stat.S_ISLNK(path_info.st_mode) or not stat.S_ISREG(path_info.st_mode):
            raise AuditIntegrityError("content-addressed tool output is not a regular file")

        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        fd = os.open(destination, flags)
        try:
            fd_info = os.fstat(fd)
            if not stat.S_ISREG(fd_info.st_mode):
                raise AuditIntegrityError("content-addressed tool output is not a regular file")
            if path_info.st_dev != fd_info.st_dev or path_info.st_ino != fd_info.st_ino:
                raise AuditIntegrityError("content-addressed tool output changed during validation")
            chunks: list[bytes] = []
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
        finally:
            os.close(fd)
        if b"".join(chunks) != expected:
            raise AuditIntegrityError("content-addressed tool output has conflicting bytes")

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
