"""The frozen flagship investigator prompt must not imply unsupported parity."""

from __future__ import annotations

from unchained.prompts import INVESTIGATOR_PROMPT


def test_investigator_prompt_is_consistently_windows_scoped() -> None:
    normalized = INVESTIGATOR_PROMPT.casefold()

    assert "windows evidence" in normalized
    assert "broad, high-value opening" in normalized
    assert "nonempty case-ledger update" in normalized
    assert "8,192 utf-8 bytes" in normalized
    assert "linux" not in normalized
    assert "macos" not in normalized
