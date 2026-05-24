"""Probability DTOs."""

from __future__ import annotations

from dataclasses import dataclass

from delta_os.application.dto.common import SerializableDTO
from delta_os.domain.services.probability_engine import ProbabilityScores


@dataclass(frozen=True, slots=True)
class ProbabilityScoreDTO(SerializableDTO):
    """Probability Agent output."""

    symbol: str
    timeframe: str
    breakout_probability: float
    fakeout_probability: float
    reversal_probability: float
    continuation_probability: float
    volatility_expansion_probability: float
    sweep_probability: float
    confidence_tier: str
    contributing_factors: tuple[str, ...]

    @classmethod
    def from_scores(
        cls,
        symbol: str,
        timeframe: str,
        scores: ProbabilityScores,
    ) -> "ProbabilityScoreDTO":
        return cls(
            symbol,
            timeframe,
            scores.breakout_probability,
            scores.fakeout_probability,
            scores.reversal_probability,
            scores.continuation_probability,
            scores.volatility_expansion_probability,
            scores.sweep_probability,
            scores.confidence_tier,
            scores.contributing_factors,
        )
