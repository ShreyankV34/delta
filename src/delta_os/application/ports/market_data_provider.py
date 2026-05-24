"""Live market-data stream provider port."""

from __future__ import annotations

from typing import Protocol

from delta_os.application.dto.live_market import (
    BarUpdateDTO,
    MarketTickDTO,
    OrderBookDTO,
    ProviderHealthDTO,
)


class MarketDataStreamProvider(Protocol):
    """Port for normalized REST+stream market-data ingestion."""

    def bootstrap_snapshot(self, symbol: str) -> tuple[MarketTickDTO, OrderBookDTO | None]:
        """Fetch initial state before stream subscription."""

    def subscribe(self, symbols: tuple[str, ...]) -> None:
        """Subscribe to live symbols."""

    def unsubscribe(self, symbols: tuple[str, ...]) -> None:
        """Unsubscribe from live symbols."""

    def poll_events(self, max_events: int = 100) -> tuple[MarketTickDTO | OrderBookDTO | BarUpdateDTO, ...]:
        """Return normalized events in stream order."""

    def health(self) -> ProviderHealthDTO:
        """Return provider health state."""

