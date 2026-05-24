"""IBKR reference broker adapter (paper/live mode capable)."""

from __future__ import annotations

from datetime import UTC, datetime

from delta_os.application.dto.execution import (
    FillEventDTO,
    OrderAckDTO,
    OrderIntentDTO,
    RejectEventDTO,
)
from delta_os.application.ports.broker_execution_provider import BrokerExecutionProvider


class IbkrReferenceBrokerAdapter(BrokerExecutionProvider):
    """Deterministic IBKR reference adapter with idempotent order IDs."""

    def __init__(
        self,
        *,
        mode: str = "paper",
        account_id: str = "DU0000000",
        client_id: str = "delta-os",
    ) -> None:
        self._mode = mode
        self._account_id = account_id
        self._client_id = client_id
        self._events: list[OrderAckDTO | FillEventDTO | RejectEventDTO] = []
        self._by_client_order_id: dict[str, OrderAckDTO] = {}
        self._positions: dict[str, float] = {}
        self._sequence = 0

    def place_order(self, intent: OrderIntentDTO) -> OrderAckDTO | RejectEventDTO:
        existing = self._by_client_order_id.get(intent.client_order_id)
        if existing is not None:
            return existing
        if intent.quantity <= 0:
            reject = RejectEventDTO(
                broker="ibkr",
                client_order_id=intent.client_order_id,
                broker_order_id=None,
                code="INVALID_QTY",
                message="quantity must be positive",
                timestamp=datetime.now(tz=UTC),
            )
            self._events.append(reject)
            return reject

        self._sequence += 1
        broker_order_id = f"{self._account_id}-{self._client_id}-{self._sequence}"
        ack = OrderAckDTO(
            broker="ibkr",
            client_order_id=intent.client_order_id,
            broker_order_id=broker_order_id,
            state="accepted" if self._mode in {"paper", "live"} else "queued",
            message=f"mode={self._mode}",
            timestamp=datetime.now(tz=UTC),
        )
        self._by_client_order_id[intent.client_order_id] = ack
        self._events.append(ack)
        return ack

    def cancel_order(self, broker_order_id: str, reason: str) -> OrderAckDTO | RejectEventDTO:
        for ack in self._by_client_order_id.values():
            if ack.broker_order_id == broker_order_id:
                cancel_ack = OrderAckDTO(
                    broker="ibkr",
                    client_order_id=ack.client_order_id,
                    broker_order_id=broker_order_id,
                    state="cancelled",
                    message=reason,
                    timestamp=datetime.now(tz=UTC),
                )
                self._events.append(cancel_ack)
                return cancel_ack
        reject = RejectEventDTO(
            broker="ibkr",
            client_order_id="unknown",
            broker_order_id=broker_order_id,
            code="NOT_FOUND",
            message="order not found",
            timestamp=datetime.now(tz=UTC),
        )
        self._events.append(reject)
        return reject

    def replace_order(
        self,
        broker_order_id: str,
        replacement: OrderIntentDTO,
    ) -> OrderAckDTO | RejectEventDTO:
        cancel_result = self.cancel_order(broker_order_id, "replace requested")
        if isinstance(cancel_result, RejectEventDTO):
            return cancel_result
        return self.place_order(replacement)

    def poll_order_events(self, max_events: int = 100) -> tuple[OrderAckDTO | FillEventDTO | RejectEventDTO, ...]:
        if not self._events:
            return ()
        take = self._events[:max_events]
        self._events = self._events[max_events:]
        return tuple(take)

    def open_positions(self) -> dict[str, float]:
        return dict(self._positions)

