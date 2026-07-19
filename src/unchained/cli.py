"""Command-line lifecycle for one isolated Sentinel Unchained run."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import uuid
from collections.abc import Sequence
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from .agent import AgentRun, UnchainedAgent, defang_untrusted_inline
from .artifacts import (
    ArtifactError,
    ArtifactRef,
    ArtifactStore,
    artifact_ref_from_existing,
    build_manifest,
    build_summary,
    capture_environment,
    write_manifest_pair,
)
from .audit import AuditLog
from .caps import CapConfig, CapExceeded, RunBudget
from .evidence import CustodyError, EvidenceDiscoveryError, EvidenceError, EvidenceSession
from .model import OpenAIResponsesModel
from .models import EvidenceProfile, RunStatus
from .tools import ToolRegistry
from .viewer import render_viewer_html

EXIT_COMPLETE = 0
EXIT_FATAL = 1
EXIT_INVALID = 2
EXIT_PARTIAL = 3


def build_parser() -> argparse.ArgumentParser:
    """Create the user-facing run command and legacy no-subcommand parser."""

    parser = argparse.ArgumentParser(
        prog="sentinel run",
        description="Run a bounded GPT-5.6-driven DFIR investigation.",
    )
    parser.add_argument("evidence", type=Path, help="file or folder containing captured evidence")
    parser.add_argument(
        "--caps",
        choices=("default", "strict"),
        default="default",
        help="hard-limit profile (environment overrides still apply)",
    )
    return parser


def build_root_parser() -> argparse.ArgumentParser:
    """Create the compact command overview shown before any evidence I/O."""

    parser = argparse.ArgumentParser(
        prog="sentinel",
        description="Profile, investigate, verify, and view a bounded GPT-5.6 DFIR case.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=("doctor", "profile", "run", "verify", "view"),
        help="lifecycle command; run 'sentinel <command> --help' for details",
    )
    return parser


def build_verify_parser() -> argparse.ArgumentParser:
    """Create the dependency-free completed-bundle verification command."""

    parser = argparse.ArgumentParser(
        prog="sentinel verify",
        description="Verify a retained Sentinel Unchained proof bundle without rebuilding it.",
    )
    parser.add_argument("run_directory", type=Path, help="completed proof-bundle directory")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--require-live-gpt56", action="store_true")
    return parser


def build_doctor_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sentinel doctor",
        description="Check local runtime and live-run configuration without reading evidence.",
    )
    parser.add_argument("--json", action="store_true", dest="json_output")
    return parser


def build_profile_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sentinel profile",
        description="Inventory, classify, route, and hash evidence without an OpenAI call.",
    )
    parser.add_argument("evidence", type=Path)
    parser.add_argument(
        "--mount",
        action="store_true",
        help="attempt a read-only disk mount while computing capabilities",
    )
    parser.add_argument("--json", action="store_true", dest="json_output")
    return parser


def build_view_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sentinel view",
        description="Verify and open the retained offline proof viewer.",
    )
    parser.add_argument("run_directory", type=Path)
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="verify and print the viewer path without launching a browser",
    )
    return parser


def _doctor(*, json_output: bool) -> int:
    configured_model = os.getenv("UNCHAINED_MODEL")
    checks = {
        "python_3_11": sys.version_info[:2] == (3, 11),
        "openai_sdk": importlib.util.find_spec("openai") is not None,
        "volatility3": importlib.util.find_spec("volatility3") is not None,
        "qwen_tool_package": importlib.util.find_spec("sift_sentinel") is not None,
        "model_is_gpt56_sol": bool(
            configured_model
            and (configured_model == "gpt-5.6" or configured_model.startswith("gpt-5.6-sol"))
        ),
        "openai_api_key_present": bool(os.getenv("OPENAI_API_KEY")),
    }
    ready = all(checks.values())
    payload = {
        "ready_for_live_run": ready,
        "checks": checks,
        "configured_model": configured_model,
        "python": sys.version.split()[0],
        "secrets_printed": False,
    }
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("READY" if ready else "NOT READY")
        for name, passed in checks.items():
            print(f"{'PASS' if passed else 'FAIL':<4}  {name}")
        if not ready:
            print("Next: set UNCHAINED_MODEL=gpt-5.6 and OPENAI_API_KEY, then rerun doctor.")
    return EXIT_COMPLETE if ready else EXIT_INVALID


def _profile(evidence: Path, *, mount: bool, json_output: bool) -> int:
    stream = None if json_output else sys.stdout
    with EvidenceSession(evidence, mount=mount, case_card_stream=stream) as session:
        profile = session.profile()
        final_hashes = session.verify_custody()
    if final_hashes != profile.hashes:
        raise CustodyError("profile custody receipts changed namespace or content")
    if json_output:
        print(
            json.dumps(
                {
                    "profile": profile.public_dict(),
                    "custody": {"match": True, "hashes": final_hashes},
                    "openai_called": False,
                    "mount_requested": mount,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print("Custody recheck: PASS")
        print("OpenAI calls: 0")
        if not mount and profile.disk_items:
            print("Tip: rerun with --mount to include read-only mounted-disk capabilities.")
    return EXIT_COMPLETE


def _progress(message: str) -> None:
    print(f"[sentinel] {message}", file=sys.stderr, flush=True)


def _view(run_directory: Path, *, no_open: bool) -> int:
    from .verify import verify_run

    result = verify_run(run_directory)
    if not result.passed:
        print("Viewer refused: proof-bundle verification failed.", file=sys.stderr)
        for error in result.errors:
            print(f"- {error}", file=sys.stderr)
        return EXIT_FATAL
    if result.terminal_status == RunStatus.COMPLETE.value:
        result = verify_run(run_directory, require_complete=True)
        if not result.passed:
            print(
                "Viewer refused: COMPLETE bundle failed strict lifecycle verification.",
                file=sys.stderr,
            )
            for error in result.errors:
                print(f"- {error}", file=sys.stderr)
            return EXIT_FATAL
    viewer = run_directory.expanduser().resolve(strict=True) / "viewer.html"
    if not viewer.is_file() or viewer.is_symlink():
        print("Viewer refused: verified bundle has no regular viewer.html.", file=sys.stderr)
        return EXIT_INVALID
    print(f"Verified viewer: {viewer}")
    if not no_open:
        import webbrowser

        if not webbrowser.open(viewer.as_uri()):
            print("The browser did not accept the viewer URL; open the printed path manually.")
    return EXIT_COMPLETE


def _run_directory(evidence: Path) -> tuple[str, Path]:
    run_id = f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    base = Path.cwd().resolve()
    resolved = evidence.expanduser().resolve(strict=False)
    evidence_directory = resolved if resolved.is_dir() else resolved.parent
    if base == evidence_directory or base.is_relative_to(evidence_directory):
        base = evidence_directory.parent
    directory = base / "unchained-runs" / run_id
    directory.mkdir(parents=True, exist_ok=False)
    directory.chmod(0o700)
    return run_id, directory


def _fatal_report(reason: str, profile: EvidenceProfile | None = None) -> str:
    route = defang_untrusted_inline(
        "not established" if profile is None else f"{profile.os} / {profile.shape}"
    )
    safe_reason = defang_untrusted_inline(reason)
    return f"""# Sentinel Unchained DFIR Report - FATAL

The run aborted because a deterministic safety or runtime invariant failed.

- Evidence route: `{route}`
- Failure: {safe_reason}

## Limitations

No complete investigative result is asserted. This system has no deterministic
validator by design. Consult `audit.jsonl` and independently re-establish
evidence custody before relying on any preserved observations.
"""


def _invalid_report(reason: str) -> str:
    safe_reason = defang_untrusted_inline(reason)
    return f"""# Sentinel Unchained DFIR Report - INVALID

The input or configuration did not pass preflight: {safe_reason}

No investigation was claimed and no forensic finding was produced.
"""


def _cap_report(error: CapExceeded, profile: EvidenceProfile | None) -> str:
    route = defang_untrusted_inline(
        "not established" if profile is None else f"{profile.os} / {profile.shape}"
    )
    detail = defang_untrusted_inline(error.detail)
    return f"""# Sentinel Unchained DFIR Report - PARTIAL

The hard cap `{error.kind.value}` fired and the run stopped gracefully.

- Evidence route: `{route}`
- Stop detail: {detail}

## Limitations

Required investigation, judge, or report phases may not have run. This system
has no deterministic validator by design. Review `audit.jsonl` before relying
on any preserved result.
"""


def _terminal_exit(run: AgentRun) -> int:
    return EXIT_COMPLETE if run.status is RunStatus.COMPLETE else EXIT_PARTIAL


def _tool_output_artifacts(
    run_directory: Path,
    entries: list[dict[str, object]],
) -> list[ArtifactRef]:
    """Collect only blobs explicitly referenced by audited tool completions."""

    by_path: dict[str, ArtifactRef] = {}
    for entry in entries:
        if entry.get("event_type") != "tool.completed":
            continue
        payload = entry.get("payload")
        if not isinstance(payload, dict):
            raise ArtifactError("tool.completed payload is not an object")
        receipt = payload.get("output_artifact")
        if not isinstance(receipt, dict):
            raise ArtifactError("tool.completed omitted output_artifact")
        path = str(receipt.get("path") or "")
        media_type = str(receipt.get("media_type") or "application/octet-stream")
        encoding = receipt.get("encoding")
        if encoding is not None and not isinstance(encoding, str):
            raise ArtifactError("tool-output encoding is not a string or null")
        actual = artifact_ref_from_existing(
            run_directory,
            path,
            role="tool-output",
            media_type=media_type,
            encoding=encoding,
        )
        claimed_hash = receipt.get("sha256") or payload.get("output_sha256")
        claimed_bytes = receipt.get("bytes") or payload.get("output_bytes")
        if actual.sha256 != claimed_hash or actual.bytes != claimed_bytes:
            raise ArtifactError(f"audited tool artifact does not match retained bytes: {path}")
        existing = by_path.get(path)
        if existing is not None and existing != actual:
            raise ArtifactError(f"conflicting duplicate tool artifact receipt: {path}")
        by_path[path] = actual
    return [by_path[path] for path in sorted(by_path)]


def run_cli(evidence_path: Path, caps_profile: str) -> int:
    """Execute, close, manifest, and immediately verify one isolated run."""

    _progress("checking GPT-5.6 configuration before evidence I/O")
    model = OpenAIResponsesModel()
    run_id, run_directory = _run_directory(evidence_path)
    audit_path = run_directory / "audit.jsonl"
    store = ArtifactStore(run_directory)
    session: EvidenceSession | None = None
    profile: EvidenceProfile | None = None
    investigation: AgentRun | None = None
    registry: ToolRegistry | None = None
    cap_config: CapConfig | None = None
    terminal_status = RunStatus.FATAL
    exit_code = EXIT_FATAL
    report = _fatal_report("run did not start")
    terminal_reason: str | None = "run did not start"
    custody_required = False
    mount_released = True
    budget: RunBudget | None = None
    root_artifacts: list[ArtifactRef] = []

    with AuditLog(audit_path, run_id) as audit:
        audit.append(
            "run.created",
            {
                "run_directory": ".",
                "evidence_input_label": "CASE-A",
                "evidence_input_kind": "directory" if evidence_path.is_dir() else "file",
                "caps_profile": caps_profile,
                "absolute_paths_recorded": False,
            },
        )
        try:
            cap_config = CapConfig.from_env(caps_profile)
            budget = RunBudget(cap_config)
            _progress("profiling and hashing the evidence set")
            audit.append("caps.configured", asdict(cap_config))
            session = EvidenceSession(evidence_path, budget=budget)
            audit.append("custody.initial.started", {})
            profile = session.profile()
            custody_required = True
            audit.append(
                "custody.initial.completed",
                {
                    "hashes": profile.hashes,
                    "sizes": profile.sizes,
                    "file_count": len(profile.items),
                },
            )
            audit.append("profile.completed", profile.public_dict())
            _progress(
                f"route ready: {profile.os}/{profile.shape}; {len(profile.items)} evidence item(s)"
            )

            if profile.shape == "unknown":
                raise EvidenceDiscoveryError(
                    "no supported memory, disk, or log content was recognized"
                )
            if not any(item.available for item in profile.items):
                raise EvidenceDiscoveryError("all recognized evidence routes are unavailable")

            budget.check()
            _progress("loading route-valid typed forensic tools")
            try:
                registry = ToolRegistry.from_reference(profile, audit, budget)
            except RuntimeError as exc:
                raise ValueError(f"forensic tool readiness failed: {exc}") from exc
            agent = UnchainedAgent(model=model, tools=registry, audit=audit, budget=budget)
            _progress(
                "starting GPT-5.6 opening book; bounded profile and observations may be sent "
                "to OpenAI, original evidence bytes stay local"
            )
            investigation = agent.run(profile)
            _progress(f"model pipeline finished with status {investigation.status.value}")
            terminal_status = investigation.status
            exit_code = _terminal_exit(investigation)
            report = investigation.report_markdown
            terminal_reason = investigation.partial_reason
        except CapExceeded as exc:
            terminal_status = RunStatus.PARTIAL
            exit_code = EXIT_PARTIAL
            report = _cap_report(exc, profile)
            terminal_reason = str(exc)
            audit.append(
                "cap.fired",
                {
                    "kind": exc.kind.value,
                    "detail": exc.detail,
                    "budget": exc.snapshot.public_dict(),
                },
            )
        except CustodyError as exc:
            terminal_status = RunStatus.FATAL
            exit_code = EXIT_FATAL
            report = _fatal_report(str(exc), profile)
            terminal_reason = str(exc)
            audit.append(
                "custody.mismatch",
                {"match": False, "error": str(exc), "status": RunStatus.FATAL.value},
            )
        except (EvidenceDiscoveryError, ValueError) as exc:
            terminal_status = RunStatus.INVALID
            exit_code = EXIT_INVALID
            report = _invalid_report(str(exc))
            terminal_reason = f"{type(exc).__name__}: {exc}"
            audit.append(
                "run.preflight_failed",
                {"status": terminal_status.value, "error": terminal_reason},
            )
        except EvidenceError as exc:
            terminal_status = RunStatus.FATAL
            exit_code = EXIT_FATAL
            report = _fatal_report(str(exc), profile)
            terminal_reason = f"{type(exc).__name__}: {exc}"
            audit.append(
                "run.failed",
                {"status": terminal_status.value, "error": terminal_reason},
            )
        except KeyboardInterrupt:
            terminal_status = RunStatus.FATAL
            exit_code = EXIT_FATAL
            terminal_reason = "KeyboardInterrupt: run interrupted by operator"
            report = _fatal_report(terminal_reason, profile)
            audit.append(
                "run.interrupted",
                {"status": terminal_status.value, "error": terminal_reason},
            )
        except Exception as exc:  # noqa: BLE001 - preserve an auditable failed run
            terminal_status = RunStatus.FATAL
            exit_code = EXIT_FATAL
            terminal_reason = f"{type(exc).__name__}: {exc}"
            report = _fatal_report(terminal_reason, profile)
            audit.append(
                "run.failed",
                {"status": terminal_status.value, "error": terminal_reason},
            )
        finally:
            if session is not None:
                mount_released = session.close()

        if not mount_released:
            terminal_status = RunStatus.FATAL
            exit_code = EXIT_FATAL
            terminal_reason = "read-only evidence mount could not be released"
            report = _fatal_report(terminal_reason, profile)
            audit.append(
                "mount.release_failed",
                {"status": RunStatus.FATAL.value, "mount_released": False},
            )

        if custody_required and session is not None:
            _progress("performing final full SHA-256 custody verification")
            audit.append("custody.final.started", {})
            try:
                final_hashes = session.verify_custody()
                audit.append(
                    "custody.final.completed",
                    {
                        "hashes": final_hashes,
                        "match": True,
                        "mount_released": mount_released,
                    },
                )
            except CustodyError as exc:
                terminal_status = RunStatus.FATAL
                exit_code = EXIT_FATAL
                terminal_reason = str(exc)
                report = _fatal_report(terminal_reason, profile)
                audit.append(
                    "custody.mismatch",
                    {"match": False, "error": str(exc), "status": RunStatus.FATAL.value},
                )

        cap_name = (
            investigation.cap.kind.value
            if investigation is not None and investigation.cap is not None
            else None
        )
        try:
            report = report.rstrip() + "\n"
            report_ref = store.write_text(
                "report.md",
                report,
                role="report",
                media_type="text/markdown",
            )
            root_artifacts.append(report_ref)
            if profile is not None:
                root_artifacts.append(
                    store.write_json(
                        "profile.json",
                        profile.public_dict(),
                        role="evidence-profile",
                    )
                )
            caps_payload = asdict(cap_config) if cap_config is not None else {}
            environment = capture_environment(
                run_id=run_id,
                project_directory=Path(__file__).resolve().parents[2],
                requested_model=(
                    model.model_id if model is not None else os.getenv("UNCHAINED_MODEL")
                ),
                caps_profile=caps_profile,
                caps=caps_payload,
                tool_schemas=registry.schemas() if registry is not None else (),
            )
            root_artifacts.append(
                store.write_json("environment.json", environment, role="environment")
            )
            preterminal_entries = AuditLog.verify(audit_path)
            summary = build_summary(
                run_id=run_id,
                entries=preterminal_entries,
                status=terminal_status.value,
                exit_code=exit_code,
                profile=profile,
                cap=cap_name,
                reason=terminal_reason,
                mount_released=mount_released,
            )
            root_artifacts.append(store.write_json("summary.json", summary, role="summary"))
            viewer = render_viewer_html(
                run_id=run_id,
                status=terminal_status.value,
                profile=profile,
                summary=summary,
                report_markdown=report,
                audit_entries=preterminal_entries,
            )
            root_artifacts.append(
                store.write_text(
                    "viewer.html",
                    viewer,
                    role="proof-viewer",
                    media_type="text/html",
                )
            )
            for artifact in root_artifacts:
                audit.append("artifact.written", artifact.public_dict())
            audit.append(
                "run.completed",
                {
                    "status": terminal_status.value,
                    "exit_code": exit_code,
                    "report": "report.md",
                    "audit": "audit.jsonl",
                    "profile": "profile.json" if profile is not None else None,
                    "environment": "environment.json",
                    "summary": "summary.json",
                    "cap": cap_name,
                    "reason": terminal_reason,
                    "custody_baseline_established": custody_required,
                    "custody_final_check_performed": custody_required,
                    "mount_released": mount_released,
                },
            )
            AuditLog.verify(audit_path)
        except Exception as exc:
            audit.append(
                "bundle.finalization_failed",
                {"error_type": type(exc).__name__, "error": str(exc)[:2_000]},
            )
            raise

    entries = AuditLog.verify(audit_path)
    audit_ref = artifact_ref_from_existing(
        run_directory,
        "audit.jsonl",
        role="audit",
        media_type="application/x-ndjson",
    )
    tool_artifacts = _tool_output_artifacts(run_directory, entries)
    manifest = build_manifest(
        run_id=run_id,
        status=terminal_status.value,
        exit_code=exit_code,
        audit_ref=audit_ref,
        audit_entries=entries,
        artifacts=[*root_artifacts, *tool_artifacts],
    )
    write_manifest_pair(store, manifest)

    from .verify import verify_run

    verification = verify_run(
        run_directory,
        require_complete=terminal_status is RunStatus.COMPLETE,
        require_live_gpt56=terminal_status is RunStatus.COMPLETE,
    )
    if not verification.passed:
        print("Proof-bundle verification failed:", file=sys.stderr)
        for error in verification.errors:
            print(f"- {error}", file=sys.stderr)
        return EXIT_FATAL

    _progress("content-addressed proof bundle verified")
    print(f"Run status: {terminal_status.value}")
    print(f"Proof bundle: {run_directory}")
    print("Bundle verification: PASS")
    print(f'Verify again: sentinel verify "{run_directory}" --require-complete')
    print(f'Open viewer: sentinel view "{run_directory}"')
    return exit_code


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments and return a stable process exit code."""

    raw_arguments = list(sys.argv[1:] if argv is None else argv)
    if not raw_arguments or raw_arguments[:1] in (["-h"], ["--help"]):
        build_root_parser().print_help()
        return EXIT_COMPLETE
    if raw_arguments[:1] in (["verify-run"], ["verify"]):
        arguments = build_verify_parser().parse_args(raw_arguments[1:])
        from .verify import verify_run

        result = verify_run(
            arguments.run_directory,
            require_complete=arguments.require_complete,
            require_live_gpt56=arguments.require_live_gpt56,
        )
        if arguments.json_output:
            print(json.dumps(result.public_dict(), indent=2, sort_keys=True))
        else:
            print("VALID" if result.passed else "INVALID")
            print(f"Run: {result.run_id or 'unknown'}")
            print(f"Status: {result.terminal_status or 'unknown'}")
            print(f"Artifacts verified: {result.verified_artifacts}")
            print(f"Audit entries verified: {result.verified_audit_entries}")
            for warning in result.warnings:
                print(f"Warning: {warning}")
            for error in result.errors:
                print(f"Error: {error}", file=sys.stderr)
        return EXIT_COMPLETE if result.passed else EXIT_FATAL

    if raw_arguments[:1] == ["doctor"]:
        arguments = build_doctor_parser().parse_args(raw_arguments[1:])
        return _doctor(json_output=arguments.json_output)

    if raw_arguments[:1] == ["profile"]:
        arguments = build_profile_parser().parse_args(raw_arguments[1:])
        try:
            return _profile(
                arguments.evidence,
                mount=arguments.mount,
                json_output=arguments.json_output,
            )
        except (EvidenceError, OSError, ValueError) as exc:
            print(f"Sentinel profile failed: {type(exc).__name__}: {exc}", file=sys.stderr)
            return EXIT_INVALID

    if raw_arguments[:1] == ["view"]:
        arguments = build_view_parser().parse_args(raw_arguments[1:])
        try:
            return _view(arguments.run_directory, no_open=arguments.no_open)
        except (OSError, ValueError) as exc:
            print(f"Sentinel viewer failed: {exc}", file=sys.stderr)
            return EXIT_INVALID

    if raw_arguments[:1] == ["run"]:
        raw_arguments = raw_arguments[1:]

    arguments = build_parser().parse_args(raw_arguments)
    try:
        return run_cli(arguments.evidence, arguments.caps)
    except KeyboardInterrupt:
        print("Sentinel Unchained interrupted.", file=sys.stderr)
        return EXIT_FATAL
    except ValueError as exc:
        print(f"Sentinel Unchained configuration invalid: {exc}", file=sys.stderr)
        return EXIT_INVALID
    except Exception as exc:  # noqa: BLE001 - stable CLI code even if finalization fails
        print(f"Sentinel Unchained fatal error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_FATAL
