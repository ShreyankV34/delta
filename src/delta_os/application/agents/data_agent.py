"""Data Agent."""

from __future__ import annotations

from pathlib import Path

from delta_os.application.dto.candles import CandleSeriesDTO, TimeframeCandleBundleDTO
from delta_os.application.ports.data_provider import CandleDataProvider
from delta_os.domain.services.timeframe_builder import TimeframeBuilder


class DataAgent:
    """Load and resample offline CSV candle data."""

    def __init__(
        self,
        provider: CandleDataProvider,
        timeframe_builder: TimeframeBuilder | None = None,
    ) -> None:
        self._provider = provider
        self._timeframe_builder = timeframe_builder or TimeframeBuilder()
        self._last_provider_health = "ready"
        self._last_provider_note = "ok"

    @property
    def last_provider_health(self) -> str:
        return self._last_provider_health

    @property
    def last_provider_note(self) -> str:
        return self._last_provider_note

    def load(
        self,
        path: Path | None,
        symbol: str | None,
        target_timeframes: tuple[str, ...],
    ) -> TimeframeCandleBundleDTO:
        """Load base candles and build requested timeframes."""
        try:
            base_series = self._provider.load_candles(path, symbol)
        except Exception:
            self._last_provider_health = "down"
            self._last_provider_note = "load_failed"
            raise

        self._last_provider_health, self._last_provider_note = _provider_health_snapshot(
            self._provider
        )
        series_by_timeframe = {base_series.timeframe: CandleSeriesDTO.from_entity(base_series)}
        for timeframe in target_timeframes:
            if timeframe == base_series.timeframe:
                continue
            built = self._timeframe_builder.build(base_series, timeframe)
            series_by_timeframe[built.timeframe] = CandleSeriesDTO.from_entity(built)

        ordered = tuple(series_by_timeframe[key] for key in sorted(series_by_timeframe))
        return TimeframeCandleBundleDTO(base_series.symbol, base_series.timeframe, ordered)


def _provider_health_snapshot(provider: CandleDataProvider) -> tuple[str, str]:
    snapshot = getattr(provider, "health_snapshot", None)
    if not callable(snapshot):
        return "ready", "ok"
    loaded = snapshot()
    if not isinstance(loaded, tuple) or len(loaded) != 2:
        return "ready", "ok"
    health, note = loaded
    if not isinstance(health, str) or not isinstance(note, str):
        return "ready", "ok"
    if health not in {"ready", "degraded", "down"}:
        return "ready", "ok"
    return health, note
