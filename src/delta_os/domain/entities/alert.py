"""Domain alert model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class MarketAlert:
    """Explainable market intelligence alert."""

    symbol: str
    alert_type: str
    message: str
    confidence: float
    created_at: datetime
    reasoning: tuple[str, ...]
    risk_notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("Alert symbol is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Alert confidence must be between 0 and 1")
