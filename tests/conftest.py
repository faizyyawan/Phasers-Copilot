"""Shared pytest configuration."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def disable_fine_tuned_router(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep unit tests fast and deterministic unless a test opts in."""
    monkeypatch.setenv("ROUTER_USE_FINE_TUNED", "false")
