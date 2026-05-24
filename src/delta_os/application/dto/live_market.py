"""Live market data DTO contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from delta_os.application.dto.common import SerializableDTO


@dataclass(frozen=True, slots=True)
class ProviderHealthDTO(SerializableDTO):
    provider: str
    status: str
    detail: str
    heartbeat_age_ms: int
    reconnect_attempt: int
    timestamp: datetime


@dataclass(frozen=True, slots=True)
class MarketTickDTO(SerializableDTO):
    symbol: str
    timestamp: datetime
    bid: float
    ask: float
    last: float
    size: float
    sequence: int
    venue: str


@dataclass(frozen=True, slots=True)
class OrderBookDTO(SerializableDTO):
    symbol: str
    timestamp: datetime
    best_bid: float
    best_ask: float
    bid_size: float
    ask_size: float
    sequence: int
    venue: str


@dataclass(frozen=True, slots=True)
class BarUpdateDTO(SerializableDTO):
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    sequence: int

