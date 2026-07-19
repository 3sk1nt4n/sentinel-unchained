"""Structured report drafts cannot alter authoritative deterministic rows."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from unchained.models import (
    EvidenceItem,
    EvidenceProfile,
    EvidenceQuote,
    EvidenceSpan,
    Finding,
    FindingStatus,
    InvestigationState,
    JudgeVerdict,
)
from unchained.reporting import (
    ReportProtocolError,
    parse_report_draft,
    render_report_markdown,
)


def _case(tmp_path: Path) -> tuple[EvidenceProfile, InvestigationState, tuple[JudgeVerdict, ...]]:
    item = EvidenceItem(
        evidence_id="E001",
        path=tmp_path / "private.mem",
        kind="memory",
        size=100,
        sha256="a" * 64,
        os_hint="windows",
    )
    profile = EvidenceProfile(
        root=tmp_path,
        os="windows",
        shape="memory-only",
        filesystems=(),
        sizes={"E001": 100},
        health={"E001": "ready"},
        symbols={"E001": "ready"},
        hashes={"E001": "a" * 64},
        available_tool_families=("volatility3.windows",),
        capability_label="Windows memory ready",
        items=(item,),
    )
    span = EvidenceSpan(
        span_id="S0123456789abcdef01234567",
        tool_call_id="t1",
        artifact_sha256="b" * 64,
        byte_start=10,
        byte_end=23,
        text="malicious.exe",
        occurrence_count=1,
    )
    finding = Finding(
        finding_id="F001",
        title="Execution hypothesis",
        summary="Observed process [t1]",
        proposed_status=FindingStatus.CONFIRMED,
        severity="HIGH",
        tool_call_ids=("t1",),
        supporting_spans=(span,),
        iocs=("malicious.exe",),
    )
    state = InvestigationState(
        case_notes="Observed process [t1]",
        findings=[finding],
        limitations=["Single evidence domain."],
    )
    verdict = JudgeVerdict(
        finding_id="F001",
        status=FindingStatus.NEEDS_REVIEW,
        rationale="Execution is not independently corroborated.",
        cited_tool_call_ids=("t1",),
        quoted_spans=(
            EvidenceQuote(
                span_id=span.span_id,
                tool_call_id="t1",
                text="malicious.exe",
            ),
        ),
    )
    return profile, state, (verdict,)


def _draft() -> dict[str, object]:
    return {
        "executive_summary": "Model says CONFIRMED, but code owns the verdict row.",
        "investigative_narrative": "A bounded process observation was reviewed.",
        "ioc_commentary": "The submitted IOC remains subject to analyst review.",
        "limitations_commentary": "No second evidence domain was available.",
        "referenced_finding_ids": ["F001"],
        "referenced_span_ids": ["S0123456789abcdef01234567"],
    }


def test_renderer_uses_judge_status_even_when_draft_claims_confirmed(tmp_path: Path) -> None:
    profile, state, verdicts = _case(tmp_path)
    draft = parse_report_draft(_draft(), tuple(state.findings), verdicts)  # type: ignore[arg-type]

    report = render_report_markdown(profile, state, verdicts, draft)

    finding_row = next(line for line in report.splitlines() if line.startswith("| F001"))
    assert "CONFIRMED" in finding_row
    assert "NEEDS-REVIEW" in finding_row
    assert "[t1]" in finding_row
    assert "S0123456789abcdef01234567" in finding_row
    assert "no deterministic validator by design" in report
    assert "## Executive summary (model-authored, nonauthoritative)" in report
    assert "## Investigative narrative (model-authored, nonauthoritative)" in report


def test_report_draft_cannot_add_findings_or_span_references(tmp_path: Path) -> None:
    _profile, state, verdicts = _case(tmp_path)
    raw = {
        **_draft(),
        "referenced_finding_ids": ["F001", "F999"],
        "referenced_span_ids": ["S0123456789abcdef01234567", "Sinvented"],
    }

    with pytest.raises(ReportProtocolError, match="finding references"):
        parse_report_draft(raw, tuple(state.findings), verdicts)  # type: ignore[arg-type]


def test_renderer_defangs_active_content_in_model_and_evidence_text(tmp_path: Path) -> None:
    profile, state, verdicts = _case(tmp_path)
    raw = {
        **_draft(),
        "investigative_narrative": (
            "<script>alert(1)</script> https://attacker.invalid ![pixel](data:x)"
        ),
    }
    draft = parse_report_draft(raw, tuple(state.findings), verdicts)  # type: ignore[arg-type]

    report = render_report_markdown(profile, state, verdicts, draft)

    assert "<script>" not in report
    assert "https://attacker.invalid" not in report
    assert "![pixel]" not in report
    assert "attacker" in report


def test_renderer_escapes_table_delimiters_once(tmp_path: Path) -> None:
    profile, state, verdicts = _case(tmp_path)
    state.findings[0] = replace(state.findings[0], title="one | two")
    draft = parse_report_draft(_draft(), tuple(state.findings), verdicts)  # type: ignore[arg-type]

    report = render_report_markdown(profile, state, verdicts, draft)

    finding_row = next(line for line in report.splitlines() if line.startswith("| F001"))
    assert "one \\| two" in finding_row
    assert "one \\\\| two" not in finding_row
