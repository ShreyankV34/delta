"""Load a local tradable universe."""

from __future__ import annotations

from pathlib import Path

from delta_os.application.agents.universe_agent import UniverseAgent
from delta_os.application.dto.universe import TradableUniverseDTO


class LoadTradableUniverseUseCase:
    """Load a tradable universe from a local watchlist file."""

    def __init__(self, universe_agent: UniverseAgent) -> None:
        self._universe_agent = universe_agent

    def run(self, catalog_path: Path, universe_name: str) -> TradableUniverseDTO:
        """Return one normalized local universe."""

        return self._universe_agent.load(catalog_path, universe_name)
