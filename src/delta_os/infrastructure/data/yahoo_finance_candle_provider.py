"""Yahoo Finance HTTP candle provider."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import urlopen

from delta_os.domain.entities.candle import Candle, CandleSeries


class YahooFinanceCandleProvider:
    """Load OHLCV candles from Yahoo Finance chart API."""

    def __init__(
        self,
        *,
        source_timeframe: str = "1m",
        request_timeout_seconds: float = 10.0,
        default_range: str = "5d",
        default_interval: str | None = None,
        symbol_suffix: str = "",
        symbol_map: dict[str, str] | None = None,
        transport: Callable[[str, float], dict[str, Any]] | None = None,
    ) -> None:
        self._source_timeframe = source_timeframe
        self._request_timeout_seconds = request_timeout_seconds
        self._default_range = default_range
        self._default_interval = default_interval or source_timeframe
        self._symbol_suffix = symbol_suffix
        self._symbol_map = symbol_map or {}
        self._transport = transport or _http_get_json
        self._last_health = "ready"
        self._last_note = "ok"

    def load_candles(self, path: Path | None, symbol: str | None = None) -> CandleSeries:
        """Load candles from remote market data API."""

        del path
        if not symbol:
            self._last_health = "down"
            self._last_note = "symbol_missing"
            raise ValueError("Symbol is required when data.provider='yahoo_finance'")

        external_symbol = self._resolve_symbol(symbol)
        try:
            payload = self._fetch_payload(external_symbol)
            candles, dropped = _extract_candles(payload, requested_symbol=symbol)
        except Exception:
            self._last_health = "down"
            self._last_note = "remote_load_failed"
            raise
        if not candles:
            self._last_health = "down"
            self._last_note = "empty_series"
            raise ValueError(f"No candles returned for symbol: {external_symbol}")
        if dropped > 0:
            self._last_health = "degraded"
            self._last_note = f"dropped_rows={dropped}"
        else:
            self._last_health = "ready"
            self._last_note = "ok"
        return CandleSeries.from_iterable(candles, self._source_timeframe)

    def health_snapshot(self) -> tuple[str, str]:
        return self._last_health, self._last_note

    def _resolve_symbol(self, symbol: str) -> str:
        cleaned = symbol.strip()
        if cleaned in self._symbol_map:
            return self._symbol_map[cleaned]
        if self._symbol_suffix and "." not in cleaned:
            return f"{cleaned}{self._symbol_suffix}"
        return cleaned

    def _fetch_payload(self, symbol: str) -> dict[str, Any]:
        params = urlencode({"interval": self._default_interval, "range": self._default_range})
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?{params}"
        loaded = self._transport(url, self._request_timeout_seconds)
        if not isinstance(loaded, dict):
            raise ValueError("Yahoo Finance response must be a JSON object")
        return loaded


def _http_get_json(url: str, timeout_seconds: float) -> dict[str, Any]:
    with urlopen(url, timeout=timeout_seconds) as response:  # noqa: S310
        content = response.read()
    loaded = json.loads(content.decode("utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("HTTP JSON payload must decode to an object")
    return loaded


def _extract_candles(payload: dict[str, Any], requested_symbol: str) -> tuple[tuple[Candle, ...], int]:
    chart = payload.get("chart", {})
    if not isinstance(chart, dict):
        raise ValueError("Yahoo response is missing 'chart'")
    result = chart.get("result")
    if not isinstance(result, list) or not result:
        raise ValueError("Yahoo response has no chart.result entries")

    first = result[0]
    if not isinstance(first, dict):
        raise ValueError("Yahoo response chart.result[0] is invalid")

    timestamps = first.get("timestamp")
    indicators = first.get("indicators", {})
    quote = indicators.get("quote", []) if isinstance(indicators, dict) else []
    quote0 = quote[0] if isinstance(quote, list) and quote else {}

    opens = quote0.get("open") if isinstance(quote0, dict) else None
    highs = quote0.get("high") if isinstance(quote0, dict) else None
    lows = quote0.get("low") if isinstance(quote0, dict) else None
    closes = quote0.get("close") if isinstance(quote0, dict) else None
    volumes = quote0.get("volume") if isinstance(quote0, dict) else None

    arrays = (timestamps, opens, highs, lows, closes, volumes)
    if any(not isinstance(item, list) for item in arrays):
        raise ValueError("Yahoo response is missing OHLCV arrays")

    count = min(len(timestamps), len(opens), len(highs), len(lows), len(closes), len(volumes))
    candles: list[Candle] = []
    dropped = 0
    for index in range(count):
        if (
            timestamps[index] is None
            or opens[index] is None
            or highs[index] is None
            or lows[index] is None
            or closes[index] is None
            or volumes[index] is None
        ):
            dropped += 1
            continue

        timestamp = datetime.fromtimestamp(int(timestamps[index]), tz=UTC)
        candles.append(
            Candle(
                timestamp=timestamp,
                open=float(opens[index]),
                high=float(highs[index]),
                low=float(lows[index]),
                close=float(closes[index]),
                volume=float(volumes[index]),
                symbol=requested_symbol,
            )
        )
    return tuple(candles), dropped
