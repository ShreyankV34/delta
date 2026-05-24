"""Config loader port."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class ConfigLoader(Protocol):
    """Port for loading configuration documents."""

    def load(self, path: Path) -> dict[str, Any]:
        """Load a configuration file."""
