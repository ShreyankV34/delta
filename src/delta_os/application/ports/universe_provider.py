"""Universe provider port."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class UniverseProvider(Protocol):
    """Port for loading local tradable universe definitions."""

    def load_catalog(self, path: Path) -> dict[str, Any]:
        """Load a universe catalog."""
