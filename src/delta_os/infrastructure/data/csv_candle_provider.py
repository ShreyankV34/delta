"""CSV candle provider."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from delta_os.domain.entities.candle import Candle, CandleSeries


class CsvCandleProvider:
    """Load OHLCV candles from a local CSV file."""

    REQUIRED_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume", "symbol")

    def __init__(self, source_timeframe: str = "1m") -> None:
        self._source_timeframe = source_timeframe
        self._last_health = "ready"
        self._last_note = "ok"

    def load_candles(self, path: Path | None, symbol: str | None = None) -> CandleSeries:
        """Load and validate candles from a CSV file."""

        if path is None:
            self._last_health = "down"
            self._last_note = "path_missing"
            raise ValueError("CSV path is required when data.provider='csv'")

        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or ())
            missing = [column for column in self.REQUIRED_COLUMNS if column not in columns]
            if missing:
                self._last_health = "down"
                self._last_note = "schema_invalid"
                raise ValueError(f"CSV missing required columns: {', '.join(missing)}")

            candles: list[Candle] = []
            for row in reader:
                row_symbol = str(row["symbol"]).strip()
                if symbol is not None and row_symbol != symbol:
                    continue
                candles.append(
                    Candle(
                        timestamp=_parse_timestamp(row["timestamp"]),
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=float(row["volume"]),
                        symbol=row_symbol,
                    )
                )
        self._last_health = "ready"
        self._last_note = "ok"
        return CandleSeries.from_iterable(candles, self._source_timeframe)

    def health_snapshot(self) -> tuple[str, str]:
        return self._last_health, self._last_note


def _parse_timestamp(raw: str) -> datetime:
    value = raw.strip()
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Invalid timestamp: {raw}") from exc
