"""Offline candle timeframe builder."""

from __future__ import annotations

from collections import defaultdict

from delta_os.domain.entities.candle import Candle, CandleSeries
from delta_os.domain.value_objects.timeframe import Timeframe, floor_timestamp


class TimeframeBuilder:
    """Aggregate lower-timeframe candles into higher timeframe candles."""

    def build(self, series: CandleSeries, target_timeframe: Timeframe | str) -> CandleSeries:
        """Build an aggregated candle series."""

        timeframe = (
            target_timeframe
            if isinstance(target_timeframe, Timeframe)
            else Timeframe.parse(target_timeframe)
        )
        if not series.candles:
            return CandleSeries((), timeframe.value)

        grouped: dict[object, list[Candle]] = defaultdict(list)
        for candle in series.candles:
            grouped[floor_timestamp(candle.timestamp, timeframe)].append(candle)

        aggregated: list[Candle] = []
        for bucket_start in sorted(grouped):
            bucket = sorted(grouped[bucket_start], key=lambda candle: candle.timestamp)
            aggregated.append(
                Candle(
                    timestamp=bucket_start,  # type: ignore[arg-type]
                    open=bucket[0].open,
                    high=max(candle.high for candle in bucket),
                    low=min(candle.low for candle in bucket),
                    close=bucket[-1].close,
                    volume=sum(candle.volume for candle in bucket),
                    symbol=bucket[0].symbol,
                )
            )
        return CandleSeries(tuple(aggregated), timeframe.value)
