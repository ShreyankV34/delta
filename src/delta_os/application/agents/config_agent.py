"""Config Agent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from delta_os.application.ports.config_loader import ConfigLoader


class ConfigAgent:
    """Load configuration through a replaceable loader port."""

    def __init__(self, loader: ConfigLoader) -> None:
        self._loader = loader

    def load(self, path: Path) -> dict[str, Any]:
        """Load and return config data."""

        return self._loader.load(path)
