"""Timeframe value object and bucketing helpers."""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum


class Timeframe(str, Enum):
    """Supported Phase-1 timeframes."""

    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1W"
    MN1 = "1M"

    @classmethod
    def parse(cls, value: str) -> "Timeframe":
        """Parse a timeframe string."""

        normalized = value.strip()
        aliases = {
            "1min": "1m",
            "5min": "5m",
            "15min": "15m",
            "60m": "1h",
            "240m": "4h",
            "1d": "1d",
            "1D": "1d",
            "1w": "1W",
            "1W": "1W",
            "1mo": "1M",
            "1M": "1M",
        }
        candidate = aliases.get(normalized, aliases.get(normalized.lower(), normalized))
        for timeframe in cls:
            if timeframe.value == candidate:
                return timeframe
        raise ValueError(f"Unsupported timeframe: {value}")

    @property
    def duration_minutes(self) -> int | None:
        """Return fixed duration in minutes, or None for calendar buckets."""

        durations = {
            Timeframe.M1: 1,
            Timeframe.M5: 5,
            Timeframe.M15: 15,
            Timeframe.H1: 60,
            Timeframe.H4: 240,
        }
        return durations.get(self)


def floor_timestamp(timestamp: datetime, timeframe: Timeframe) -> datetime:
    """Floor a timestamp into the requested timeframe bucket."""

    if timeframe == Timeframe.MN1:
        return timestamp.replace(month=timestamp.month, day=1, hour=0, minute=0, second=0, microsecond=0)
    if timeframe == Timeframe.W1:
        day_floor = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        return day_floor - timedelta(days=day_floor.weekday())
    if timeframe == Timeframe.D1:
        return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)

    minutes = timeframe.duration_minutes
    if minutes is None:
        raise ValueError(f"Cannot floor timestamp for timeframe {timeframe.value}")
    total_minutes = timestamp.hour * 60 + timestamp.minute
    bucket_minutes = (total_minutes // minutes) * minutes
    return timestamp.replace(
        hour=bucket_minutes // 60,
        minute=bucket_minutes % 60,
        second=0,
        microsecond=0,
    )
