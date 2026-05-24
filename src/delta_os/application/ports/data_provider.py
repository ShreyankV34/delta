"""Data provider port."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from delta_os.domain.entities.candle import CandleSeries


class CandleDataProvider(Protocol):
    """Port for loading candle data."""

    def load_candles(self, path: Path | None, symbol: str | None = None) -> CandleSeries:
        """Load candles from a source."""
