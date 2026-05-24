"""Candle DTOs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from delta_os.application.dto.common import SerializableDTO
from delta_os.domain.entities.candle import Candle, CandleSeries


@dataclass(frozen=True, slots=True)
class CandleDTO(SerializableDTO):
    """Serializable candle DTO."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str

    @classmethod
    def from_entity(cls, candle: Candle) -> "CandleDTO":
        return cls(
            candle.timestamp,
            candle.open,
            candle.high,
            candle.low,
            candle.close,
            candle.volume,
            candle.symbol,
        )

    def to_entity(self) -> Candle:
        return Candle(
            self.timestamp,
            self.open,
            self.high,
            self.low,
            self.close,
            self.volume,
            self.symbol,
        )


@dataclass(frozen=True, slots=True)
class CandleSeriesDTO(SerializableDTO):
    """Serializable candle series DTO."""

    symbol: str
    timeframe: str
    candles: tuple[CandleDTO, ...]

    @classmethod
    def from_entity(cls, series: CandleSeries) -> "CandleSeriesDTO":
        return cls(
            series.symbol,
            series.timeframe,
            tuple(CandleDTO.from_entity(candle) for candle in series.candles),
        )

    def to_entity(self) -> CandleSeries:
        return CandleSeries(tuple(candle.to_entity() for candle in self.candles), self.timeframe)


@dataclass(frozen=True, slots=True)
class TimeframeCandleBundleDTO(SerializableDTO):
    """Bundle of candles across timeframes."""

    symbol: str
    source_timeframe: str
    series: tuple[CandleSeriesDTO, ...]

    def get(self, timeframe: str) -> CandleSeriesDTO:
        """Return a series by timeframe."""

        for item in self.series:
            if item.timeframe == timeframe:
                return item
        raise KeyError(f"Timeframe not found: {timeframe}")
