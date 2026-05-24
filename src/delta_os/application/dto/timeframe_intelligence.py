"""Timeframe intelligence DTOs."""

from __future__ import annotations

from dataclasses import dataclass

from delta_os.application.dto.common import SerializableDTO


@dataclass(frozen=True, slots=True)
class TimeframeIntelligenceDTO(SerializableDTO):
    """Deterministic intelligence summary for one timeframe."""

    symbol: str
    timeframe: str
    bias: str
    trend_strength: float
    structure_state: str
    liquidity_state: str
    volatility_regime: str
    compression_state: str
    breakout_probability: float
    fakeout_probability: float
    reversal_probability: float
    continuation_probability: float
    structural_confidence: float
    htf_alignment: str
    invalidation_risk: float
    institutional_participation_probability: float
    market_regime: str
    execution_quality: str
    risk_state: str
    comment: str
