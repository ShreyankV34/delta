"""Liquidity concept DTOs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from delta_os.application.dto.common import SerializableDTO
from delta_os.domain.services.liquidity_concepts import LiquidityEvent


@dataclass(frozen=True, slots=True)
class LiquidityEventDTO(SerializableDTO):
    """Serializable liquidity concept event."""

    event_type: str
    index: int
    timestamp: datetime
    price: float
    direction: str
    confidence: float
    reason: str

    @classmethod
    def from_event(cls, event: LiquidityEvent) -> "LiquidityEventDTO":
        return cls(
            event.event_type,
            event.index,
            event.timestamp,
            event.price,
            event.direction,
            event.confidence,
            event.reason,
        )


@dataclass(frozen=True, slots=True)
class LiquidityConceptsDTO(SerializableDTO):
    """Liquidity Concepts Agent output."""

    symbol: str
    timeframe: str
    events: tuple[LiquidityEventDTO, ...]
    event_count: int
    reasoning: tuple[str, ...]
