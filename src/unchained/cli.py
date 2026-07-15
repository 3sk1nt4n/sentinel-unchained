"""Command-line lifecycle for one isolated Sentinel Unchained run."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from collections.abc import Sequence
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from .agent import AgentRun, UnchainedAgent, defang_untrusted_inline
from .audit import AuditLog
from .caps import CapConfig, CapExceeded, RunBudget
from .evidence import CustodyError, EvidenceDiscoveryError, EvidenceError, EvidenceSession
from .model import OpenAIResponsesModel
from .models import EvidenceProfile, RunStatus
from .tools import ToolRegistry

EXIT_COMPLETE = 0
EXIT_FATAL = 1
EXIT_INVALID = 2
EXIT_PARTIAL = 3


def build_parser() -> argparse.ArgumentParser:
    """Create the exact no-subcommand CLI requested by the project contract."""

    parser = argparse.ArgumentParser(
        prog="python -m unchained",
        description="Run a bounded GPT-5.6-driven DFIR investigation.",
    )
    parser.add_argument("evidence", type=Path, help="folder containing captured evidence")
    parser.add_argument(
        "--caps",
        choices=("default", "strict"),
        default="default",
        help="hard-limit profile (environment overrides still apply)",
    )
    return parser


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


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_report(path: Path, report: str) -> str:
    normalized = report.rstrip() + "\n"
    path.write_text(normalized, encoding="utf-8", newline="\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _fatal_report(reason: str, profile: EvidenceProfile | None = None) -> str:
    route = defang_untrusted_inline(
        "not established" if profile is None else f"{profile.os} / {profile.shape}"
    )
    safe_reason = defang_untrusted_inline(reason)
    return f"""# Sentinel Unchained DFIR Report — FATAL

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
    return f"""# Sentinel Unchained DFIR Report — INVALID

The input or configuration did not pass preflight: {safe_reason}

No investigation was claimed and no forensic finding was produced.
"""


def _cap_report(error: CapExceeded, profile: EvidenceProfile | None) -> str:
    route = defang_untrusted_inline(
        "not established" if profile is None else f"{profile.os} / {profile.shape}"
    )
    detail = defang_untrusted_inline(error.detail)
    return f"""# Sentinel Unchained DFIR Report — PARTIAL

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


def run_cli(evidence_path: Path, caps_profile: str) -> int:
    """Execute one run, always attempting final custody verification after profiling."""

    run_id, run_directory = _run_directory(evidence_path)
    audit_path = run_directory / "audit.jsonl"
    report_path = run_directory / "report.md"
    session: EvidenceSession | None = None
    profile: EvidenceProfile | None = None
    investigation: AgentRun | None = None
    terminal_status = RunStatus.FATAL
    exit_code = EXIT_FATAL
    report = _fatal_report("run did not start")
    custody_required = False
    mount_released = True
    budget: RunBudget | None = None

    with AuditLog(audit_path, run_id) as audit:
        audit.append(
            "run.created",
            {
                "run_directory": str(run_directory),
                "evidence_input": str(evidence_path.expanduser().resolve(strict=False)),
                "caps_profile": caps_profile,
            },
        )
        try:
            cap_config = CapConfig.from_env(caps_profile)
            budget = RunBudget(cap_config)
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
            _write_json(run_directory / "profile.json", profile.public_dict())

            if profile.shape == "unknown":
                raise EvidenceDiscoveryError(
                    "no supported memory, disk, or log content was recognized"
                )
            if not any(item.available for item in profile.items):
                raise EvidenceDiscoveryError("all recognized evidence routes are unavailable")

            budget.check()
            model = OpenAIResponsesModel()
            try:
                registry = ToolRegistry.from_reference(profile, audit, budget)
            except RuntimeError as exc:
                raise ValueError(f"forensic tool readiness failed: {exc}") from exc
            agent = UnchainedAgent(model=model, tools=registry, audit=audit, budget=budget)
            investigation = agent.run(profile)
            terminal_status = investigation.status
            exit_code = _terminal_exit(investigation)
            report = investigation.report_markdown
        except CapExceeded as exc:
            terminal_status = RunStatus.PARTIAL
            exit_code = EXIT_PARTIAL
            report = _cap_report(exc, profile)
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
            audit.append(
                "custody.mismatch",
                {"match": False, "error": str(exc), "status": RunStatus.FATAL.value},
            )
        except (EvidenceDiscoveryError, ValueError) as exc:
            terminal_status = RunStatus.INVALID
            exit_code = EXIT_INVALID
            report = _invalid_report(str(exc))
            audit.append(
                "run.preflight_failed",
                {"status": terminal_status.value, "error": f"{type(exc).__name__}: {exc}"},
            )
        except EvidenceError as exc:
            terminal_status = RunStatus.FATAL
            exit_code = EXIT_FATAL
            report = _fatal_report(str(exc), profile)
            audit.append(
                "run.failed",
                {"status": terminal_status.value, "error": f"{type(exc).__name__}: {exc}"},
            )
        except KeyboardInterrupt:
            terminal_status = RunStatus.FATAL
            exit_code = EXIT_FATAL
            report = _fatal_report("KeyboardInterrupt: run interrupted by operator", profile)
            audit.append(
                "run.interrupted",
                {
                    "status": terminal_status.value,
                    "error": "KeyboardInterrupt: run interrupted by operator",
                },
            )
        except Exception as exc:  # noqa: BLE001 - CLI must preserve an auditable artifact
            terminal_status = RunStatus.FATAL
            exit_code = EXIT_FATAL
            report = _fatal_report(f"{type(exc).__name__}: {exc}", profile)
            audit.append(
                "run.failed",
                {"status": terminal_status.value, "error": f"{type(exc).__name__}: {exc}"},
            )
        finally:
            if session is not None:
                mount_released = session.close()

        if not mount_released:
            terminal_status = RunStatus.FATAL
            exit_code = EXIT_FATAL
            report = _fatal_report("read-only evidence mount could not be released", profile)
            audit.append(
                "mount.release_failed",
                {"status": RunStatus.FATAL.value, "mount_released": False},
            )

        if custody_required and session is not None:
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
                report = _fatal_report(str(exc), profile)
                audit.append(
                    "custody.mismatch",
                    {"match": False, "error": str(exc), "status": RunStatus.FATAL.value},
                )

        report_sha256 = _write_report(report_path, report)
        audit.append(
            "artifact.written",
            {
                "name": "report.md",
                "sha256": report_sha256,
                "status": terminal_status.value,
            },
        )
        audit.append(
            "run.completed",
            {
                "status": terminal_status.value,
                "exit_code": exit_code,
                "report": str(report_path),
                "audit": str(audit_path),
                "cap": (
                    investigation.cap.kind.value
                    if investigation is not None and investigation.cap is not None
                    else None
                ),
            },
        )
        AuditLog.verify(audit_path)

    print(f"Run status: {terminal_status.value}")
    print(f"Report: {report_path}")
    print(f"Audit: {audit_path}")
    return exit_code


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments and return a stable process exit code."""

    arguments = build_parser().parse_args(argv)
    try:
        return run_cli(arguments.evidence, arguments.caps)
    except KeyboardInterrupt:
        print("Sentinel Unchained interrupted.", file=sys.stderr)
        return EXIT_FATAL
    except Exception as exc:  # noqa: BLE001 - stable CLI code even if finalization fails
        print(f"Sentinel Unchained fatal error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_FATAL
