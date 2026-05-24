from __future__ import annotations

from datetime import UTC, datetime

from delta_os.application.dto.execution import OrderIntentDTO, RejectEventDTO
from delta_os.infrastructure.execution import IbkrReferenceBrokerAdapter


def _intent(client_order_id: str, quantity: float = 5.0) -> OrderIntentDTO:
    return OrderIntentDTO(
        client_order_id=client_order_id,
        symbol="RELIANCE",
        asset_class="equity",
        side="buy",
        order_type="limit",
        quantity=quantity,
        limit_price=100.0,
        stop_price=None,
        tif="day",
        strategy_tag="test",
        created_at=datetime.now(tz=UTC),
        metadata={},
    )


def test_ibkr_adapter_is_idempotent_by_client_order_id() -> None:
    broker = IbkrReferenceBrokerAdapter(mode="paper")
    first = broker.place_order(_intent("cid-1"))
    second = broker.place_order(_intent("cid-1"))
    assert first.to_dict() == second.to_dict()


def test_ibkr_adapter_rejects_non_positive_quantity() -> None:
    broker = IbkrReferenceBrokerAdapter(mode="paper")
    result = broker.place_order(_intent("cid-2", quantity=0.0))
    assert isinstance(result, RejectEventDTO)
    assert result.code == "INVALID_QTY"


def test_ibkr_adapter_cancel_unknown_order_returns_reject() -> None:
    broker = IbkrReferenceBrokerAdapter(mode="paper")
    result = broker.cancel_order("unknown", "test")
    assert isinstance(result, RejectEventDTO)
    assert result.code == "NOT_FOUND"

