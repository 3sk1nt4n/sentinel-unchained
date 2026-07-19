"""Strict policy checks for viewer HTML accepted at the browser boundary."""

from __future__ import annotations

import pytest

from unchained.viewer import render_viewer_html
from unchained.viewer_policy import validate_inert_viewer_html

CSP = (
    "default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; "
    "font-src 'none'; media-src 'none'; connect-src 'none'; script-src 'none'; "
    "object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'"
)


def document(*, head: str = "", body: str = "<main><p>Proof</p></main>") -> str:
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        f'<meta http-equiv="Content-Security-Policy" content="{CSP}">'
        f"{head}<title>Proof</title></head><body>{body}</body></html>"
    )


def test_accepts_minimal_inert_document() -> None:
    assert validate_inert_viewer_html(document(head="<style>p { color: #fff; }</style>")) == ()


def test_accepts_the_deterministic_viewer_renderer() -> None:
    rendered = render_viewer_html(
        run_id="policy-test",
        status="COMPLETE",
        profile=None,
        summary={"exit_code": 0, "reason": "complete"},
        report_markdown="# Report\n\nHostile text: <script>alert(1)</script>\n",
        audit_entries=[],
    )

    assert validate_inert_viewer_html(rendered) == ()


@pytest.mark.parametrize(
    "active",
    [
        "<script>alert(1)</script>",
        "<iframe></iframe>",
        "<frame>",
        "<object></object>",
        "<embed>",
        "<link>",
        "<base>",
        "<form></form>",
        "<input>",
        "<button>send</button>",
        "<video></video>",
        "<audio></audio>",
        "<svg></svg>",
        "<math></math>",
        "<a>link</a>",
    ],
)
def test_rejects_active_elements(active: str) -> None:
    errors = validate_inert_viewer_html(document(body=active))

    assert errors
    assert any("not permitted" in error for error in errors)


@pytest.mark.parametrize(
    ("body", "fragment"),
    [
        ('<p onclick="alert(1)">x</p>', "event-handler"),
        ('<p href="https://attacker.invalid">x</p>', "URL-bearing"),
        ('<p srcset="https://attacker.invalid/a 1x">x</p>', "URL-bearing"),
        ('<p style="background:red">x</p>', "inline style"),
    ],
)
def test_rejects_active_attributes(body: str, fragment: str) -> None:
    errors = validate_inert_viewer_html(document(body=body))

    assert any(fragment in error for error in errors)


@pytest.mark.parametrize(
    "css",
    [
        "p { background: url(https://attacker.invalid/x); }",
        '@import "https://attacker.invalid/x.css";',
        "p { width: expression(alert(1)); }",
        'p { background: image-set("https://attacker.invalid/x" 1x); }',
        "p { background: u\\72l(https://attacker.invalid/x); }",
        "p { background: u/**/rl(https://attacker.invalid/x); }",
    ],
)
def test_rejects_active_css(css: str) -> None:
    errors = validate_inert_viewer_html(document(head=f"<style>{css}</style>"))

    assert any("CSS" in error for error in errors)


def test_rejects_meta_refresh() -> None:
    errors = validate_inert_viewer_html(
        document(head='<meta http-equiv="refresh" content="0; https://attacker.invalid">')
    )

    assert "meta refresh is forbidden" in errors


@pytest.mark.parametrize(
    "replacement",
    [
        "default-src 'self'",
        "script-src 'unsafe-inline'",
        "style-src 'self'",
        "connect-src https://attacker.invalid",
    ],
)
def test_rejects_weakened_csp(replacement: str) -> None:
    directive = replacement.split()[0]
    weakened = "; ".join(
        replacement if part.strip().startswith(directive) else part for part in CSP.split(";")
    )
    html = document().replace(CSP, weakened)

    assert "the CSP does not match the inert proof-viewer policy" in validate_inert_viewer_html(
        html
    )


def test_rejects_duplicate_or_reporting_csp() -> None:
    duplicate = document(head=f'<meta http-equiv="Content-Security-Policy" content="{CSP}">')
    reporting = document().replace(CSP, CSP + "; report-uri https://attacker.invalid/csp")

    assert "the document must contain exactly one CSP meta element" in validate_inert_viewer_html(
        duplicate
    )
    assert "the CSP does not match the inert proof-viewer policy" in validate_inert_viewer_html(
        reporting
    )


@pytest.mark.parametrize(
    "html",
    [
        "<html><head></head><body></body></html>",
        "<!doctype html><html><body></body></html>",
        "<!doctype html><html><head></head></html>",
        document(body="<main><p>broken</main></p>"),
        document(body="<custom-element>unknown</custom-element>"),
    ],
)
def test_rejects_malformed_or_unapproved_structure(html: str) -> None:
    assert validate_inert_viewer_html(html)
