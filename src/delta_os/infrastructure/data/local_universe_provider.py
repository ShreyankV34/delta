"""Local universe catalog provider."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from delta_os.infrastructure.config import YamlConfigLoader


class LocalUniverseProvider:
    """Load local watchlist universes from YAML files."""

    def __init__(self, loader: YamlConfigLoader | None = None) -> None:
        self._loader = loader or YamlConfigLoader()

    def load_catalog(self, path: Path) -> dict[str, Any]:
        """Load a universe catalog from disk."""

        loaded = self._loader.load(path)
        if not isinstance(loaded, dict):
            raise ValueError("Universe catalog must deserialize to a mapping")
        return loaded
