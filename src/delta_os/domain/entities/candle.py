"""Core candle entities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Iterable


@dataclass(frozen=True, slots=True)
class Candle:
    """Immutable OHLCV candle."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str

    def __post_init__(self) -> None:
        values = (self.open, self.high, self.low, self.close, self.volume)
        if any(not isfinite(value) for value in values):
            raise ValueError("Candle values must be finite")
        if not self.symbol:
            raise ValueError("Candle symbol is required")
        if self.volume < 0:
            raise ValueError("Candle volume cannot be negative")
        if self.high < max(self.open, self.low, self.close):
            raise ValueError("Candle high must be greater than or equal to open/low/close")
        if self.low > min(self.open, self.high, self.close):
            raise ValueError("Candle low must be less than or equal to open/high/close")

    @property
    def typical_price(self) -> float:
        """Return the candle's typical price."""

        return (self.high + self.low + self.close) / 3.0


@dataclass(frozen=True, slots=True)
class CandleSeries:
    """Chronologically ordered candles for one symbol and timeframe."""

    candles: tuple[Candle, ...]
    timeframe: str

    def __post_init__(self) -> None:
        ordered = tuple(sorted(self.candles, key=lambda candle: candle.timestamp))
        object.__setattr__(self, "candles", ordered)
        symbols = {candle.symbol for candle in ordered}
        if len(symbols) > 1:
            raise ValueError("CandleSeries must contain one symbol only")
        if not self.timeframe:
            raise ValueError("CandleSeries timeframe is required")

    @classmethod
    def from_iterable(cls, candles: Iterable[Candle], timeframe: str) -> "CandleSeries":
        """Build a sorted series from an iterable of candles."""

        return cls(tuple(candles), timeframe)

    @property
    def symbol(self) -> str:
        """Return the series symbol, or UNKNOWN for an empty series."""

        if not self.candles:
            return "UNKNOWN"
        return self.candles[0].symbol

    def __len__(self) -> int:
        return len(self.candles)

    def __iter__(self) -> Iterable[Candle]:
        return iter(self.candles)
