"""Fusion DTOs."""

from __future__ import annotations

from dataclasses import dataclass

from delta_os.application.dto.common import SerializableDTO


@dataclass(frozen=True, slots=True)
class FusedMarketIntelligenceDTO(SerializableDTO):
    """Fusion Agent output."""

    symbol: str
    timeframe: str
    final_signal_score: float
    market_state: str
    risk_veto: bool
    reasoning: tuple[str, ...]
