"""Alert DTOs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from delta_os.application.dto.common import SerializableDTO


@dataclass(frozen=True, slots=True)
class AlertDTO(SerializableDTO):
    """Alert Agent output."""

    symbol: str
    timeframe: str
    alert_type: str
    message: str
    confidence: float
    created_at: datetime
    reasoning: tuple[str, ...]
    risk_notes: tuple[str, ...]
