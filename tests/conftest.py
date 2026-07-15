"""Shared test helpers for the entirely offline acceptance suite."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ManualClock:
    """A monotonic clock that advances without sleeping."""

    now: float = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds
