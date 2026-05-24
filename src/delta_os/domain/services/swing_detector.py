"""Swing high and swing low detector."""

from __future__ import annotations

from delta_os.domain.entities.candle import CandleSeries
from delta_os.domain.value_objects.swing import SwingKind, SwingPoint


class SwingDetector:
    """Detect local swing highs and lows with deterministic windows."""

    def __init__(self, left: int = 2, right: int = 2) -> None:
        if left < 1 or right < 1:
            raise ValueError("Swing windows must be positive")
        self._left = left
        self._right = right

    def detect(self, series: CandleSeries) -> tuple[SwingPoint, ...]:
        """Return detected swing points."""

        candles = series.candles
        if len(candles) < self._left + self._right + 1:
            return ()

        swings: list[SwingPoint] = []
        for index in range(self._left, len(candles) - self._right):
            window = candles[index - self._left : index + self._right + 1]
            candle = candles[index]
            other_highs = [item.high for offset, item in enumerate(window) if offset != self._left]
            other_lows = [item.low for offset, item in enumerate(window) if offset != self._left]

            if candle.high > max(other_highs):
                swings.append(SwingPoint(index, candle.timestamp, candle.high, SwingKind.HIGH))
            if candle.low < min(other_lows):
                swings.append(SwingPoint(index, candle.timestamp, candle.low, SwingKind.LOW))
        return tuple(swings)
