from __future__ import annotations

from pathlib import Path

import pytest

from delta_os.application.agents import UniverseAgent
from delta_os.infrastructure.data import LocalUniverseProvider

WATCHLISTS = Path("data/sample/watchlists.yaml")


def test_universe_agent_loads_local_watchlist_catalog() -> None:
    universe = UniverseAgent(LocalUniverseProvider()).load(WATCHLISTS, "nifty_50")

    assert universe.name == "nifty_50"
    assert universe.total_members == 5
    assert universe.included_symbols == (
        "RELIANCE",
        "TCS",
        "INFY",
        "HDFCBANK",
        "ICICIBANK",
    )
    assert universe.excluded_symbols == ()


def test_universe_agent_filters_invalid_and_duplicate_members_deterministically() -> None:
    universe = UniverseAgent(LocalUniverseProvider()).load(WATCHLISTS, "custom_watchlist")

    assert universe.total_members == 2
    assert universe.included_symbols == ("RELIANCE", "INFY")
    assert universe.excluded_symbols == ("bad symbol", "RELIANCE")
    assert universe.members[0].display_name == "Reliance Industries"
    assert universe.members[1].sector == "it"


def test_universe_agent_rejects_missing_universe() -> None:
    with pytest.raises(ValueError, match="Universe 'missing' not found"):
        UniverseAgent(LocalUniverseProvider()).load(WATCHLISTS, "missing")
