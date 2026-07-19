"""User-facing command dispatch and fail-fast preflight tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import unchained.verify as verify_module
from unchained.cli import EXIT_COMPLETE, EXIT_FATAL, EXIT_INVALID, _view, main
from unchained.verify import VerificationResult


def test_root_help_lists_the_user_lifecycle(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--help"]) == EXIT_COMPLETE

    output = capsys.readouterr().out
    for command in ("doctor", "profile", "run", "verify", "view"):
        assert command in output
    assert "evidence" not in output.lower()


def test_view_requires_strict_lifecycle_when_bundle_claims_complete(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    calls: list[bool] = []

    def fake_verify(
        path: Path,
        require_complete: bool = False,
        require_live_gpt56: bool = False,
    ) -> VerificationResult:
        del require_live_gpt56
        calls.append(require_complete)
        return VerificationResult(
            passed=not require_complete,
            run_directory=str(path),
            run_id="run-test",
            terminal_status="COMPLETE",
            exit_code=0,
            errors=() if not require_complete else ("strict lifecycle mismatch",),
            warnings=(),
            verified_artifacts=6,
            verified_audit_entries=44,
        )

    monkeypatch.setattr(verify_module, "verify_run", fake_verify)

    assert _view(tmp_path, no_open=True) == EXIT_FATAL
    assert calls == [False, True]
    assert "failed strict lifecycle verification" in capsys.readouterr().err


def test_profile_is_offline_and_returns_public_custody_ids(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    (evidence / "system.log").write_text(
        "2026-01-01T00:00:00 systemd[1]: start\n"
        "2026-01-01T00:00:01 sshd[2]: login\n"
        "2026-01-01T00:00:02 kernel: audit\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("UNCHAINED_MODEL", raising=False)

    exit_code = main(["profile", str(evidence), "--json"])

    assert exit_code == EXIT_COMPLETE
    payload = json.loads(capsys.readouterr().out)
    assert payload["openai_called"] is False
    assert payload["profile"]["shape"] == "logs-only"
    assert set(payload["custody"]["hashes"]) == {"E001"}
    assert "system.log" not in json.dumps(payload["custody"])


def test_live_run_configuration_fails_before_evidence_or_output_io(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("UNCHAINED_MODEL", "gpt-5.6")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    exit_code = main(["run", str(tmp_path / "missing-evidence")])

    assert exit_code == EXIT_INVALID
    assert "OPENAI_API_KEY is required" in capsys.readouterr().err
    assert not (tmp_path / "unchained-runs").exists()


def test_doctor_never_prints_secret_value(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    secret = "sk-test-do-not-print"
    monkeypatch.setenv("UNCHAINED_MODEL", "gpt-5.6")
    monkeypatch.setenv("OPENAI_API_KEY", secret)

    exit_code = main(["doctor", "--json"])

    output = capsys.readouterr().out
    payload = json.loads(output)
    assert exit_code == EXIT_COMPLETE
    assert payload["ready_for_live_run"] is True
    assert payload["checks"]["openai_api_key_present"] is True
    assert payload["secrets_printed"] is False
    assert secret not in output
