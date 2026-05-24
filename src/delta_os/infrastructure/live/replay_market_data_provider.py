"""Deterministic replay provider for live-session regression."""

from __future__ import annotations

from datetime import UTC, datetime

from delta_os.application.dto.live_market import (
    BarUpdateDTO,
    MarketTickDTO,
    OrderBookDTO,
    ProviderHealthDTO,
)
from delta_os.application.ports.market_data_provider import MarketDataStreamProvider
from delta_os.infrastructure.live.normalized_event_bus import NormalizedEventBus

LiveMarketEvent = MarketTickDTO | OrderBookDTO | BarUpdateDTO


class ReplayMarketDataProvider(MarketDataStreamProvider):
    """Replay recorded normalized events with deterministic ordering."""

    def __init__(
        self,
        provider_name: str,
        bootstrap_by_symbol: dict[str, tuple[MarketTickDTO, OrderBookDTO | None]],
        events: tuple[LiveMarketEvent, ...],
    ) -> None:
        self._provider_name = provider_name
        self._bootstrap_by_symbol = dict(bootstrap_by_symbol)
        self._subscribed_symbols: set[str] = set()
        self._bus = NormalizedEventBus(max_size=max(1024, len(events) + 8))
        self._health = ProviderHealthDTO(
            provider=provider_name,
            status="ready",
            detail="replay_loaded",
            heartbeat_age_ms=0,
            reconnect_attempt=0,
            timestamp=datetime.now(tz=UTC),
        )
        for event in events:
            self._bus.publish(event)

    def bootstrap_snapshot(self, symbol: str) -> tuple[MarketTickDTO, OrderBookDTO | None]:
        if symbol not in self._bootstrap_by_symbol:
            raise KeyError(f"No bootstrap snapshot for symbol: {symbol}")
        return self._bootstrap_by_symbol[symbol]

    def subscribe(self, symbols: tuple[str, ...]) -> None:
        self._subscribed_symbols.update(symbols)
        self._health = ProviderHealthDTO(
            provider=self._provider_name,
            status="ready",
            detail=f"subscribed={len(self._subscribed_symbols)}",
            heartbeat_age_ms=0,
            reconnect_attempt=0,
            timestamp=datetime.now(tz=UTC),
        )

    def unsubscribe(self, symbols: tuple[str, ...]) -> None:
        for symbol in symbols:
            self._subscribed_symbols.discard(symbol)
        self._health = ProviderHealthDTO(
            provider=self._provider_name,
            status="ready",
            detail=f"subscribed={len(self._subscribed_symbols)}",
            heartbeat_age_ms=0,
            reconnect_attempt=0,
            timestamp=datetime.now(tz=UTC),
        )

    def poll_events(self, max_events: int = 100) -> tuple[LiveMarketEvent, ...]:
        all_items = self._bus.drain(max_events=max_events)
        filtered = tuple(item for item in all_items if item.symbol in self._subscribed_symbols)
        if not filtered and all_items:
            self._health = ProviderHealthDTO(
                provider=self._provider_name,
                status="degraded",
                detail="events_for_unsubscribed_symbols",
                heartbeat_age_ms=0,
                reconnect_attempt=0,
                timestamp=datetime.now(tz=UTC),
            )
        return filtered

    def health(self) -> ProviderHealthDTO:
        return self._health

