"""Private subprocess entry point for pinned forensic functions.

The parent runner supplies a sealed JSON invocation on standard input.  No
module, function, plugin, command, or evidence path in this protocol is ever
model-visible.  This module deliberately owns the complete callable allowlist
so invoking it directly cannot turn it into a general Python function runner.
"""

from __future__ import annotations

import contextlib
import importlib
import inspect
import json
import math
import os
import re
import shutil
import subprocess
import sys
import threading
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

# tool id -> (module, function, invocation kind).  Every target is an exact
# function below sift_sentinel.tools; arbitrary import targets are impossible.
DIRECT_TOOL_TARGETS: dict[str, tuple[str, str, str]] = {
    "vol_pstree": ("sift_sentinel.tools.memory", "vol_pstree", "memory"),
    "vol_psscan": ("sift_sentinel.tools.memory_extended", "vol_psscan", "memory"),
    "vol_netscan": ("sift_sentinel.tools.memory", "vol_netscan", "memory"),
    "vol_malfind": ("sift_sentinel.tools.memory", "vol_malfind", "memory"),
    "vol_cmdline": ("sift_sentinel.tools.memory", "vol_cmdline", "memory"),
    "vol_dlllist": ("sift_sentinel.tools.memory", "vol_dlllist", "memory"),
    "vol_handles": ("sift_sentinel.tools.memory_extended", "vol_handles", "memory"),
    "vol_envars": ("sift_sentinel.tools.memory_extended", "vol_envars", "memory"),
    "vol_getsids": ("sift_sentinel.tools.memory_extended", "vol_getsids", "memory"),
    "vol_privileges": (
        "sift_sentinel.tools.memory_extended",
        "vol_privileges",
        "memory",
    ),
    "vol_svcscan": ("sift_sentinel.tools.memory_extended2", "vol_svcscan", "memory"),
    "vol_filescan": ("sift_sentinel.tools.memory_extended2", "vol_filescan", "memory"),
    "vol_mftscan": ("sift_sentinel.tools.memory_extended2", "vol_mftscan", "memory"),
    "vol_reg_hivelist": (
        "sift_sentinel.tools.memory_extended2",
        "vol_reg_hivelist",
        "memory",
    ),
    "get_amcache": ("sift_sentinel.tools.disk", "get_amcache", "disk"),
    "extract_mft_timeline": (
        "sift_sentinel.tools.disk",
        "extract_mft_timeline",
        "disk",
    ),
    "parse_event_logs": (
        "sift_sentinel.tools.disk_extended",
        "parse_event_logs",
        "standalone",
    ),
    "parse_prefetch": (
        "sift_sentinel.tools.disk_extended",
        "parse_prefetch",
        "standalone",
    ),
    "parse_powershell_transcripts": (
        "sift_sentinel.tools.parse_powershell_transcripts",
        "parse_powershell_transcripts",
        "standalone",
    ),
    "parse_rdp_artifacts": (
        "sift_sentinel.tools.parse_rdp_artifacts",
        "parse_rdp_artifacts",
        "standalone",
    ),
    "parse_wmi_subscription": (
        "sift_sentinel.tools.parse_wmi_subscription",
        "parse_wmi_subscription",
        "standalone",
    ),
    "parse_registry_persistence": (
        "sift_sentinel.tools.parse_registry_persistence",
        "parse_registry_persistence",
        "standalone",
    ),
    "parse_usb_devices": (
        "sift_sentinel.tools.parse_usb_devices",
        "parse_usb_devices",
        "standalone",
    ),
    "parse_userassist": (
        "sift_sentinel.tools.parse_userassist",
        "parse_userassist",
        "standalone",
    ),
    "parse_scheduled_tasks_disk": (
        "sift_sentinel.tools.parse_scheduled_tasks_disk",
        "parse_scheduled_tasks_disk",
        "standalone",
    ),
}

SAFE_VOLATILITY_PLUGINS = frozenset(
    {
        "linux.bash.bash",
        "linux.check_syscall.check_syscall",
        "linux.malfind.malfind",
        "linux.psaux.psaux",
        "linux.pslist.pslist",
        "linux.pstree.pstree",
        "linux.sockstat.sockstat",
        "mac.malfind.malfind",
        "mac.netstat.netstat",
        "mac.psaux.psaux",
        "mac.pslist.pslist",
        "mac.pstree.pstree",
    }
)
SAFE_TSK_TOOLS = frozenset({"fsstat", "img_stat", "mmls"})


class WorkerProtocolError(ValueError):
    """Raised when the parent-to-worker invocation is malformed or unapproved."""


def _absolute_path(spec: dict[str, Any], field: str) -> str:
    value = spec.get(field)
    if not isinstance(value, str) or not value or not Path(value).is_absolute():
        raise WorkerProtocolError(f"{field} must be a nonempty absolute path")
    return value


def _arguments(spec: dict[str, Any]) -> dict[str, Any]:
    value = spec.get("arguments", {})
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise WorkerProtocolError("arguments must be a JSON object with string keys")
    return value


def _configure_timeout(spec: dict[str, Any]) -> None:
    value = spec.get("timeout_seconds")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise WorkerProtocolError("timeout_seconds must be numeric")
    timeout = float(value)
    if not math.isfinite(timeout) or timeout <= 0:
        raise WorkerProtocolError("timeout_seconds must be finite and positive")
    os.environ["SIFT_REACT_TOOL_TIMEOUT"] = str(max(1, int(timeout)))


def _run_direct(spec: dict[str, Any]) -> Any:
    name = spec.get("tool")
    if not isinstance(name, str) or name not in DIRECT_TOOL_TARGETS:
        raise WorkerProtocolError("direct tool is not allowlisted")
    module_name, function_name, invocation_kind = DIRECT_TOOL_TARGETS[name]
    if not module_name.startswith("sift_sentinel.tools."):
        raise WorkerProtocolError("direct tool target escaped the allowed package")

    _configure_timeout(spec)
    arguments = _arguments(spec)
    image_path = ""
    mount_path = ""
    if invocation_kind == "memory":
        image_path = _absolute_path(spec, "evidence_path")
    else:
        mount_path = _absolute_path(spec, "mount_path")
        os.environ["SIFT_ACTIVE_DISK_MOUNT"] = mount_path

    module = importlib.import_module(module_name)
    function = getattr(module, function_name)
    if not callable(function):
        raise WorkerProtocolError("allowlisted target is not callable")

    if invocation_kind == "memory":
        unexpected = set(arguments) - {"pid"}
        if unexpected:
            raise WorkerProtocolError(f"unsupported memory arguments: {sorted(unexpected)}")
        if "pid" in arguments:
            pid = arguments["pid"]
            if pid is not None and (not isinstance(pid, int) or isinstance(pid, bool)):
                raise WorkerProtocolError("pid must be an integer or null")
            return function(image_path, pid=pid)
        return function(image_path)

    if arguments:
        raise WorkerProtocolError("disk tools do not accept model arguments")

    # These exact forensic functions have heterogeneous, trusted signatures.  The
    # invocation strategy mirrors their typed adapter without accepting a
    # parameter name from the caller.
    try:
        signature = inspect.signature(function)
    except (TypeError, ValueError):
        signature = None
    if signature and "mount_path" in signature.parameters:
        return function(mount_path=mount_path)
    if signature and "disk_mount" in signature.parameters:
        return function(disk_mount=mount_path)
    return function(mount_path)


def _run_volatility(spec: dict[str, Any]) -> Any:
    name = spec.get("tool")
    if not isinstance(name, str) or not name:
        raise WorkerProtocolError("volatility tool must be a nonempty string")
    if _arguments(spec):
        raise WorkerProtocolError("dynamic volatility tools do not accept arguments")
    memory_path = _absolute_path(spec, "evidence_path")
    _configure_timeout(spec)

    # This is the one fixed wrapper path allowed by the worker.  The logical
    # name must also resolve to the reviewed Linux/macOS plugin set.
    from sift_sentinel.tools.common import VOLATILITY_PLUGINS, run_volatility

    plugin_path = VOLATILITY_PLUGINS.get(name)
    if not isinstance(plugin_path, str) or plugin_path.lower() not in SAFE_VOLATILITY_PLUGINS:
        raise WorkerProtocolError("volatility plugin is not allowlisted")
    return run_volatility(name, memory_path)


def _run_catalog() -> dict[str, Any]:
    """Discover trusted forensic metadata without importing the tool package in the parent."""

    from sift_sentinel.tools.capabilities import get_capability
    from sift_sentinel.tools.common import VOLATILITY_PLUGINS

    direct: dict[str, Any] = {}
    for name, (module_name, function_name, _invocation_kind) in DIRECT_TOOL_TARGETS.items():
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)
        if not callable(function):
            raise WorkerProtocolError(f"allowlisted catalog target is not callable: {name}")
        try:
            signature = inspect.signature(function)
        except (TypeError, ValueError):
            signature = None
        capability = get_capability(name) or {}
        direct[name] = {
            "has_pid": bool(signature and "pid" in signature.parameters),
            "required_args": capability.get("required_args", []),
            "produces": capability.get("produces", []),
            "runtime_class": capability.get("runtime_class", "unknown"),
        }

    volatility_plugins = {
        str(name): plugin_path
        for name, plugin_path in VOLATILITY_PLUGINS.items()
        if isinstance(plugin_path, str) and plugin_path.lower() in SAFE_VOLATILITY_PLUGINS
    }
    return {"direct": direct, "volatility_plugins": volatility_plugins}


def _run_tsk(spec: dict[str, Any]) -> dict[str, Any]:
    """Run one exact read-only Sleuth Kit metadata inspector."""

    name = spec.get("tool")
    if not isinstance(name, str) or name not in SAFE_TSK_TOOLS:
        raise WorkerProtocolError("Sleuth Kit tool is not allowlisted")
    if _arguments(spec):
        raise WorkerProtocolError("Sleuth Kit tools do not accept arguments")
    disk_path = _absolute_path(spec, "evidence_path")
    _configure_timeout(spec)
    binary = shutil.which(name)
    if binary is None:
        raise WorkerProtocolError(f"allowlisted Sleuth Kit tool is unavailable: {name}")
    command = [binary]
    if name == "fsstat":
        sector_offset = spec.get("sector_offset")
        if isinstance(sector_offset, bool) or not isinstance(sector_offset, int):
            raise WorkerProtocolError("fsstat requires a sealed non-negative sector offset")
        if sector_offset < 0:
            raise WorkerProtocolError("fsstat sector offset cannot be negative")
        if sector_offset:
            command.extend(["-o", str(sector_offset)])
    elif "sector_offset" in spec:
        raise WorkerProtocolError("only fsstat accepts a sector offset")
    command.append(disk_path)
    timeout = max(1, int(float(spec["timeout_seconds"])))
    try:
        completed = subprocess.run(
            command,
            check=False,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": f"TSK probe exceeded {timeout}s"}
    return {
        "status": "ok" if completed.returncode == 0 else "error",
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _run_test(spec: dict[str, Any]) -> Any:
    """Small subprocess probe available only to the network-free test suite."""

    if os.getenv("UNCHAINED_TEST_TOOL_WORKER") != "1":
        raise WorkerProtocolError("test worker action is disabled")
    operation = spec.get("operation")
    if operation == "echo":
        return spec.get("value")
    if operation == "environment":
        keys = spec.get("keys")
        if not isinstance(keys, list) or not all(isinstance(key, str) for key in keys):
            raise WorkerProtocolError("test environment keys must be strings")
        return {key: os.getenv(key) for key in keys}
    if operation == "block":
        threading.Event().wait()
        raise AssertionError("unreachable")
    if operation == "error":
        raise WorkerProtocolError(str(spec.get("value", "test worker error")))
    raise WorkerProtocolError("unknown test worker operation")


def _run(spec: dict[str, Any]) -> Any:
    action = spec.get("action")
    if action == "direct":
        return _run_direct(spec)
    if action == "volatility":
        return _run_volatility(spec)
    if action == "catalog":
        return _run_catalog()
    if action == "tsk":
        return _run_tsk(spec)
    if action == "test":
        return _run_test(spec)
    raise WorkerProtocolError("worker action is not allowlisted")


def _json_normalize(value: Any) -> Any:
    """Convert trusted return values while preserving status/error dictionaries."""

    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else repr(value)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value) and not isinstance(value, type):
        return _json_normalize(asdict(value))
    if isinstance(value, dict):
        return {str(key): _json_normalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_normalize(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return [_json_normalize(item) for item in sorted(value, key=repr)]
    return repr(value)


def _public_result(value: Any, spec: dict[str, Any]) -> Any:
    """Remove runner-local evidence paths from the accepted public result."""

    requested_id = spec.get("evidence_id")
    evidence_id = (
        requested_id
        if isinstance(requested_id, str) and re.fullmatch(r"E[0-9]{3}", requested_id)
        else "EVIDENCE"
    )
    private_paths = tuple(
        path
        for field in ("evidence_path", "mount_path")
        if isinstance((path := spec.get(field)), str) and path
    )

    def scrub(item: Any) -> Any:
        if isinstance(item, str):
            result = item
            for private_path in private_paths:
                variants = {
                    private_path,
                    private_path.replace("\\", "/"),
                    private_path.replace("/", "\\"),
                }
                for variant in variants:
                    result = re.sub(
                        re.escape(variant),
                        lambda _match: f"[{evidence_id}]",
                        result,
                        flags=re.IGNORECASE,
                    )
            return result
        if isinstance(item, list):
            return [scrub(child) for child in item]
        if isinstance(item, dict):
            public: dict[str, Any] = {}
            local_path_removed = False
            for key, child in item.items():
                if key in {"evidence_path", "mount_path"} and isinstance(child, str):
                    local_path_removed = True
                    continue
                public[key] = scrub(child)
            if local_path_removed:
                public.setdefault("evidence_id", evidence_id)
            return public
        return item

    return scrub(value)


def main() -> int:
    """Read one sealed request and emit exactly one JSON protocol object."""

    spec: dict[str, Any] = {}
    try:
        payload = sys.stdin.readline()
        decoded = json.loads(payload)
        if not isinstance(decoded, dict):
            raise WorkerProtocolError("worker request must be a JSON object")
        spec = decoded
        # Imports and tool execution happen only after the parent has assigned
        # this process to its POSIX process group or Windows Job Object.
        with (
            open(os.devnull, "w", encoding="utf-8") as output_sink,
            contextlib.redirect_stdout(output_sink),
        ):
            result = _run(spec)
        response = {"ok": True, "result": _public_result(_json_normalize(result), spec)}
    except BaseException as exc:  # noqa: BLE001 - errors cross a JSON boundary
        public_error = _public_result(
            {
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
            spec,
        )
        assert isinstance(public_error, dict)
        response = {
            "ok": False,
            "error_type": public_error["error_type"],
            "error": public_error["error"],
        }
    sys.stdout.write(json.dumps(response, ensure_ascii=False, allow_nan=False))
    sys.stdout.write("\n")
    sys.stdout.flush()
    # The parent deliberately keeps stdin open until it has the complete
    # response, then kills this still-live process group / Job Object.  That
    # makes cleanup of ordinary background descendants race-free.
    sys.stdin.read(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
