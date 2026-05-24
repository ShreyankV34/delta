"""Normalized live event bus with sequencing and de-duplication."""

from __future__ import annotations

from collections import deque

from delta_os.application.dto.live_market import BarUpdateDTO, MarketTickDTO, OrderBookDTO

LiveMarketEvent = MarketTickDTO | OrderBookDTO | BarUpdateDTO


class NormalizedEventBus:
    """Bounded in-memory queue for normalized market events."""

    def __init__(self, max_size: int = 10_000) -> None:
        self._queue: deque[LiveMarketEvent] = deque(maxlen=max_size)
        self._last_sequence_by_symbol: dict[tuple[str, str], int] = {}

    def publish(self, event: LiveMarketEvent) -> bool:
        """Publish one event; reject out-of-order/duplicate sequences."""

        key = _event_key(event)
        last_sequence = self._last_sequence_by_symbol.get(key, -1)
        if event.sequence <= last_sequence:
            return False
        self._last_sequence_by_symbol[key] = event.sequence
        self._queue.append(event)
        return True

    def drain(self, max_events: int) -> tuple[LiveMarketEvent, ...]:
        """Drain up to max_events from queue."""

        items: list[LiveMarketEvent] = []
        for _ in range(max_events):
            if not self._queue:
                break
            items.append(self._queue.popleft())
        return tuple(items)


def _event_key(event: LiveMarketEvent) -> tuple[str, str]:
    if isinstance(event, BarUpdateDTO):
        return event.symbol, f"bar:{event.timeframe}"
    if isinstance(event, OrderBookDTO):
        return event.symbol, "book"
    return event.symbol, "tick"

