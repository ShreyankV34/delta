"""Execution and order-lifecycle DTO contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from delta_os.application.dto.common import SerializableDTO


@dataclass(frozen=True, slots=True)
class OrderIntentDTO(SerializableDTO):
    client_order_id: str
    symbol: str
    asset_class: str
    side: str
    order_type: str
    quantity: float
    limit_price: float | None
    stop_price: float | None
    tif: str
    strategy_tag: str
    created_at: datetime
    metadata: dict[str, str]


@dataclass(frozen=True, slots=True)
class OrderDecisionDTO(SerializableDTO):
    allowed: bool
    reason: str
    veto_source: str
    requires_confirmation: bool
    timestamp: datetime


@dataclass(frozen=True, slots=True)
class OrderAckDTO(SerializableDTO):
    broker: str
    client_order_id: str
    broker_order_id: str
    state: str
    message: str
    timestamp: datetime


@dataclass(frozen=True, slots=True)
class FillEventDTO(SerializableDTO):
    broker: str
    broker_order_id: str
    client_order_id: str
    symbol: str
    side: str
    fill_qty: float
    fill_price: float
    cum_qty: float
    leaves_qty: float
    timestamp: datetime


@dataclass(frozen=True, slots=True)
class RejectEventDTO(SerializableDTO):
    broker: str
    client_order_id: str
    broker_order_id: str | None
    code: str
    message: str
    timestamp: datetime

