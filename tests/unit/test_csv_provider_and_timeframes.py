from __future__ import annotations

from pathlib import Path

import pytest

from delta_os.domain.services.timeframe_builder import TimeframeBuilder
from delta_os.infrastructure.data import CsvCandleProvider

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "sample_candles.csv"


def test_csv_provider_loads_valid_ohlcv_rows() -> None:
    series = CsvCandleProvider().load_candles(FIXTURE, "RELIANCE")

    assert series.symbol == "RELIANCE"
    assert series.timeframe == "1m"
    assert len(series) == 12
    assert series.candles[0].timestamp.isoformat() == "2024-01-01T09:15:00"
    assert series.candles[-1].close == 112.5


def test_csv_provider_rejects_missing_required_columns(tmp_path: Path) -> None:
    broken = tmp_path / "broken.csv"
    broken.write_text("timestamp,open,high\n2024-01-01 09:15:00,1,2\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required columns"):
        CsvCandleProvider().load_candles(broken, "RELIANCE")


def test_timeframe_builder_aggregates_1m_to_5m() -> None:
    series = CsvCandleProvider().load_candles(FIXTURE, "RELIANCE")
    five_minute = TimeframeBuilder().build(series, "5m")

    assert five_minute.timeframe == "5m"
    assert len(five_minute) == 3
    first = five_minute.candles[0]
    assert first.open == 100.0
    assert first.high == 105.0
    assert first.low == 99.0
    assert first.close == 104.0
    assert first.volume == 6000
