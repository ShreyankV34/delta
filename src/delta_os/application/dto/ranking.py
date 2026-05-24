"""Ranking DTOs."""

from __future__ import annotations

from dataclasses import dataclass

from delta_os.application.dto.common import SerializableDTO


@dataclass(frozen=True, slots=True)
class RankedOpportunityDTO(SerializableDTO):
    """Ranking Agent output."""

    rank: int
    symbol: str
    timeframe: str
    score: float
    market_state: str
    breakout_probability: float
    fakeout_probability: float
    risk_state: str
    risk_veto: bool
    reasoning: tuple[str, ...]
