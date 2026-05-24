from __future__ import annotations

import json
from pathlib import Path

from delta_os.application.agents import UniverseAgent
from delta_os.application.use_cases import LoadTradableUniverseUseCase
from delta_os.infrastructure.data import LocalUniverseProvider


def test_load_tradable_universe_use_case_returns_normalized_members() -> None:
    use_case = LoadTradableUniverseUseCase(UniverseAgent(LocalUniverseProvider()))

    result = use_case.run(Path("data/sample/watchlists.yaml"), "custom_watchlist")

    assert result.name == "custom_watchlist"
    assert result.total_members == 2
    assert result.included_symbols == ("RELIANCE", "INFY")
    assert "loaded universe=custom_watchlist" in result.reasoning


def test_load_tradable_universe_summary_matches_fixture() -> None:
    use_case = LoadTradableUniverseUseCase(UniverseAgent(LocalUniverseProvider()))

    result = use_case.run(Path("data/sample/watchlists.yaml"), "custom_watchlist")
    summary = {
        "name": result.name,
        "source_path": result.source_path,
        "total_members": result.total_members,
        "included_symbols": list(result.included_symbols),
        "excluded_symbols": list(result.excluded_symbols),
        "member_display_names": [member.display_name for member in result.members],
        "sectors": [member.sector for member in result.members],
    }
    expected = json.loads(
        (Path(__file__).resolve().parents[1] / "fixtures" / "universe_watchlist_summary.json").read_text(
            encoding="utf-8"
        )
    )

    assert summary == expected
