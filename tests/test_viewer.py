"""Static proof viewer is readable, self-contained, and hostile-data inert."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

from unchained.models import EvidenceItem, EvidenceProfile
from unchained.viewer import render_viewer_html


class ViewerAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []
        self.external_attributes: list[tuple[str, str]] = []
        self.csp = ""

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        self.tags.append(tag)
        values = dict(attrs)
        if tag == "meta" and values.get("http-equiv") == "Content-Security-Policy":
            self.csp = values.get("content") or ""
        for name in ("href", "src", "action", "formaction", "poster", "data"):
            if values.get(name):
                self.external_attributes.append((name, values[name] or ""))


def _profile(tmp_path: Path) -> EvidenceProfile:
    item = EvidenceItem(
        evidence_id="E001",
        path=tmp_path / "private.mem",
        kind="memory",
        size=4096,
        sha256="a" * 64,
        os_hint="windows",
        health="ready",
        symbols="ready",
    )
    return EvidenceProfile(
        root=tmp_path,
        os="windows",
        shape="memory-only",
        filesystems=(),
        sizes={"E001": item.size},
        health={"E001": item.health},
        symbols={"E001": item.symbols},
        hashes={"E001": item.sha256},
        available_tool_families=("volatility3.windows",),
        capability_label="Windows memory ready",
        items=(item,),
    )


def _viewer(tmp_path: Path) -> str:
    hashes = {"E001": "a" * 64}
    entries = [
        {"event_type": "profile.completed", "elapsed_ms": 100, "payload": {}},
        {
            "event_type": "tool.completed",
            "elapsed_ms": 500,
            "payload": {
                "tool_call_id": "t1",
                "tool_name": "windows.pslist",
                "status": "success",
                "duration_ms": 300,
                "evidence_refs": [{"evidence_id": "E001", "sha256": "a" * 64}],
            },
        },
        {
            "event_type": "custody.initial.completed",
            "elapsed_ms": 90,
            "payload": {"hashes": hashes},
        },
        {
            "event_type": "custody.final.completed",
            "elapsed_ms": 900,
            "payload": {"hashes": hashes, "match": True},
        },
    ]
    return render_viewer_html(
        run_id="run-viewer-001",
        status="COMPLETE",
        profile=_profile(tmp_path),
        summary={"exit_code": 0, "reason": "completed"},
        report_markdown=(
            "# Report\n<script>alert(1)</script>\n![pixel](https://attacker.invalid/x)\n"
        ),
        audit_entries=entries,
    )


def test_viewer_has_no_script_or_external_resource_authority(tmp_path: Path) -> None:
    rendered = _viewer(tmp_path)
    audit = ViewerAudit()
    audit.feed(rendered)

    assert "script" not in audit.tags
    assert "img" not in audit.tags
    assert "iframe" not in audit.tags
    assert "object" not in audit.tags
    assert audit.external_attributes == []
    assert "default-src 'none'" in audit.csp
    assert "connect-src 'none'" in audit.csp
    assert "script-src 'none'" in audit.csp
    assert "<script>alert" not in rendered
    assert "&lt;script&gt;alert" in rendered


def test_viewer_exposes_route_custody_and_evidence_binding(tmp_path: Path) -> None:
    rendered = _viewer(tmp_path)

    assert "windows / memory-only" in rendered
    assert "MATCH" in rendered
    assert "windows.pslist" in rendered
    assert "E001:aaaaaaaaaaaa" in rendered
    assert "RECORDED COMPLETE" in rendered
    assert "cannot verify itself" in rendered
    assert "sentinel view" in rendered


def test_write_viewer_for_browser_smoke(tmp_path: Path) -> None:
    target = tmp_path / "viewer.html"
    target.write_text(_viewer(tmp_path), encoding="utf-8")

    assert target.stat().st_size > 5_000
