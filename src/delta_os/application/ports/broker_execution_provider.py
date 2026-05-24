"""Broker execution provider port."""

from __future__ import annotations

from typing import Protocol

from delta_os.application.dto.execution import (
    FillEventDTO,
    OrderAckDTO,
    OrderIntentDTO,
    RejectEventDTO,
)


class BrokerExecutionProvider(Protocol):
    """Port for broker order lifecycle actions."""

    def place_order(self, intent: OrderIntentDTO) -> OrderAckDTO | RejectEventDTO:
        """Submit order intent."""

    def cancel_order(self, broker_order_id: str, reason: str) -> OrderAckDTO | RejectEventDTO:
        """Cancel existing order."""

    def replace_order(
        self,
        broker_order_id: str,
        replacement: OrderIntentDTO,
    ) -> OrderAckDTO | RejectEventDTO:
        """Replace an existing order."""

    def poll_order_events(self, max_events: int = 100) -> tuple[OrderAckDTO | FillEventDTO | RejectEventDTO, ...]:
        """Fetch latest order lifecycle events."""

    def open_positions(self) -> dict[str, float]:
        """Return symbol -> quantity map."""

