"""Retail structural concepts converted into deterministic feature events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from delta_os.domain.entities.candle import CandleSeries
from delta_os.domain.value_objects.swing import SwingKind, SwingPoint


@dataclass(frozen=True, slots=True)
class LiquidityEvent:
    """Detected liquidity or structural concept event."""

    event_type: str
    index: int
    timestamp: datetime
    price: float
    direction: str
    confidence: float
    reason: str


class LiquidityConceptDetector:
    """Detect Phase-1 FVG, sweeps, BOS, and CHOCH events."""

    def __init__(self, sweep_lookback: int = 3) -> None:
        if sweep_lookback < 1:
            raise ValueError("sweep_lookback must be positive")
        self._sweep_lookback = sweep_lookback

    def detect(
        self,
        series: CandleSeries,
        swings: tuple[SwingPoint, ...] = (),
    ) -> tuple[LiquidityEvent, ...]:
        """Return all supported liquidity concept events."""

        events: list[LiquidityEvent] = []
        events.extend(self._detect_fvg(series))
        events.extend(self._detect_sweeps(series))
        events.extend(self._detect_bos_choch(series, swings))
        return tuple(sorted(events, key=lambda event: (event.index, event.event_type)))

    def _detect_fvg(self, series: CandleSeries) -> list[LiquidityEvent]:
        events: list[LiquidityEvent] = []
        candles = series.candles
        for index in range(2, len(candles)):
            current = candles[index]
            anchor = candles[index - 2]
            if current.low > anchor.high:
                events.append(
                    LiquidityEvent(
                        "fair_value_gap",
                        index,
                        current.timestamp,
                        current.low,
                        "bullish",
                        0.7,
                        "current low is above the high from two candles back",
                    )
                )
            if current.high < anchor.low:
                events.append(
                    LiquidityEvent(
                        "fair_value_gap",
                        index,
                        current.timestamp,
                        current.high,
                        "bearish",
                        0.7,
                        "current high is below the low from two candles back",
                    )
                )
        return events

    def _detect_sweeps(self, series: CandleSeries) -> list[LiquidityEvent]:
        events: list[LiquidityEvent] = []
        candles = series.candles
        for index in range(self._sweep_lookback, len(candles)):
            current = candles[index]
            prior = candles[index - self._sweep_lookback : index]
            prior_high = max(candle.high for candle in prior)
            prior_low = min(candle.low for candle in prior)
            if current.high > prior_high and current.close < prior_high:
                events.append(
                    LiquidityEvent(
                        "liquidity_sweep",
                        index,
                        current.timestamp,
                        current.high,
                        "high_sweep",
                        0.75,
                        "high traded above prior range and closed back inside",
                    )
                )
            if current.low < prior_low and current.close > prior_low:
                events.append(
                    LiquidityEvent(
                        "liquidity_sweep",
                        index,
                        current.timestamp,
                        current.low,
                        "low_sweep",
                        0.75,
                        "low traded below prior range and closed back inside",
                    )
                )
        return events

    def _detect_bos_choch(
        self,
        series: CandleSeries,
        swings: tuple[SwingPoint, ...],
    ) -> list[LiquidityEvent]:
        events: list[LiquidityEvent] = []
        if not swings:
            return events

        last_direction: str | None = None
        for index, candle in enumerate(series.candles):
            previous_swings = tuple(point for point in swings if point.index < index)
            previous_highs = tuple(point for point in previous_swings if point.kind == SwingKind.HIGH)
            previous_lows = tuple(point for point in previous_swings if point.kind == SwingKind.LOW)

            if previous_highs and candle.close > previous_highs[-1].price:
                events.append(
                    LiquidityEvent(
                        "bos",
                        index,
                        candle.timestamp,
                        candle.close,
                        "bullish",
                        0.72,
                        "close broke above previous swing high",
                    )
                )
                if last_direction == "bearish":
                    events.append(
                        LiquidityEvent(
                            "choch",
                            index,
                            candle.timestamp,
                            candle.close,
                            "bullish",
                            0.68,
                            "bullish break followed bearish structure",
                        )
                    )
                last_direction = "bullish"

            if previous_lows and candle.close < previous_lows[-1].price:
                events.append(
                    LiquidityEvent(
                        "bos",
                        index,
                        candle.timestamp,
                        candle.close,
                        "bearish",
                        0.72,
                        "close broke below previous swing low",
                    )
                )
                if last_direction == "bullish":
                    events.append(
                        LiquidityEvent(
                            "choch",
                            index,
                            candle.timestamp,
                            candle.close,
                            "bearish",
                            0.68,
                            "bearish break followed bullish structure",
                        )
                    )
                last_direction = "bearish"
        return events
