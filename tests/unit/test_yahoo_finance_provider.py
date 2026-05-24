from __future__ import annotations

from pathlib import Path

import pytest

from delta_os.infrastructure.data.yahoo_finance_candle_provider import YahooFinanceCandleProvider


def test_yahoo_finance_provider_loads_candles_from_transport() -> None:
    payload = {
        "chart": {
            "result": [
                {
                    "timestamp": [1704090600, 1704090660, 1704090720],
                    "indicators": {
                        "quote": [
                            {
                                "open": [100.0, 100.5, 101.0],
                                "high": [101.0, 101.5, 102.0],
                                "low": [99.5, 100.0, 100.8],
                                "close": [100.6, 101.0, 101.8],
                                "volume": [1200, 1400, 1500],
                            }
                        ]
                    },
                }
            ]
        }
    }

    def fake_transport(url: str, timeout: float) -> dict[str, object]:
        assert "RELIANCE.NS" in url
        assert "interval=1m" in url
        assert "range=5d" in url
        assert timeout == 12.0
        return payload

    provider = YahooFinanceCandleProvider(
        source_timeframe="1m",
        request_timeout_seconds=12.0,
        default_range="5d",
        default_interval="1m",
        symbol_suffix=".NS",
        transport=fake_transport,
    )
    series = provider.load_candles(path=None, symbol="RELIANCE")

    assert series.symbol == "RELIANCE"
    assert series.timeframe == "1m"
    assert len(series.candles) == 3
    assert series.candles[0].timestamp.isoformat() == "2024-01-01T06:30:00+00:00"


def test_yahoo_finance_provider_rejects_missing_symbol() -> None:
    provider = YahooFinanceCandleProvider(transport=lambda _url, _timeout: {})
    with pytest.raises(ValueError, match="Symbol is required"):
        provider.load_candles(path=None, symbol=None)


def test_yahoo_finance_provider_rejects_empty_remote_series() -> None:
    payload = {
        "chart": {
            "result": [
                {
                    "timestamp": [],
                    "indicators": {
                        "quote": [{"open": [], "high": [], "low": [], "close": [], "volume": []}]
                    },
                }
            ]
        }
    }
    provider = YahooFinanceCandleProvider(transport=lambda _url, _timeout: payload)

    with pytest.raises(ValueError, match="No candles returned"):
        provider.load_candles(path=Path("ignored.csv"), symbol="RELIANCE")


def test_yahoo_finance_provider_keeps_dotted_symbol_without_suffix_duplication() -> None:
    def fake_transport(url: str, _timeout: float) -> dict[str, object]:
        assert "RELIANCE.NS" in url
        return {
            "chart": {
                "result": [
                    {
                        "timestamp": [1704090600],
                        "indicators": {
                            "quote": [
                                {
                                    "open": [100.0],
                                    "high": [101.0],
                                    "low": [99.5],
                                    "close": [100.5],
                                    "volume": [1200],
                                }
                            ]
                        },
                    }
                ]
            }
        }

    provider = YahooFinanceCandleProvider(symbol_suffix=".NS", transport=fake_transport)
    series = provider.load_candles(path=None, symbol="RELIANCE.NS")
    assert series.symbol == "RELIANCE.NS"


def test_yahoo_finance_provider_prefers_symbol_map_override() -> None:
    def fake_transport(url: str, _timeout: float) -> dict[str, object]:
        assert "RIL.NS" in url
        return {
            "chart": {
                "result": [
                    {
                        "timestamp": [1704090600],
                        "indicators": {
                            "quote": [
                                {
                                    "open": [100.0],
                                    "high": [101.0],
                                    "low": [99.5],
                                    "close": [100.5],
                                    "volume": [1200],
                                }
                            ]
                        },
                    }
                ]
            }
        }

    provider = YahooFinanceCandleProvider(
        symbol_suffix=".NS",
        symbol_map={"RELIANCE": "RIL.NS"},
        transport=fake_transport,
    )
    series = provider.load_candles(path=None, symbol="RELIANCE")
    assert series.symbol == "RELIANCE"


def test_yahoo_finance_provider_reports_degraded_health_when_rows_dropped() -> None:
    payload = {
        "chart": {
            "result": [
                {
                    "timestamp": [1704090600, 1704090660],
                    "indicators": {
                        "quote": [
                            {
                                "open": [100.0, None],
                                "high": [101.0, None],
                                "low": [99.5, None],
                                "close": [100.5, None],
                                "volume": [1200, None],
                            }
                        ]
                    },
                }
            ]
        }
    }
    provider = YahooFinanceCandleProvider(transport=lambda _u, _t: payload)
    series = provider.load_candles(path=None, symbol="RELIANCE")

    assert len(series.candles) == 1
    health, note = provider.health_snapshot()
    assert health == "degraded"
    assert note == "dropped_rows=1"
