from __future__ import annotations

from pathlib import Path

from delta_os.infrastructure.data import LocalUniverseProvider


def test_local_universe_provider_loads_yaml_catalog() -> None:
    catalog = LocalUniverseProvider().load_catalog(Path("data/sample/watchlists.yaml"))

    assert "universes" in catalog
    assert "nifty_50" in catalog["universes"]
    assert catalog["universes"]["fno_stocks"]["theme"] == "liquid_trading"
