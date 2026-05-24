"""Risk DTOs."""

from __future__ import annotations

from dataclasses import dataclass

from delta_os.application.dto.common import SerializableDTO
from delta_os.domain.services.risk_engine import RiskAssessment


@dataclass(frozen=True, slots=True)
class RiskAssessmentDTO(SerializableDTO):
    """Risk Agent output."""

    symbol: str
    timeframe: str
    veto: bool
    risk_state: str
    invalidation_level: float | None
    risk_reward: float | None
    notes: tuple[str, ...]

    @classmethod
    def from_assessment(
        cls,
        symbol: str,
        timeframe: str,
        assessment: RiskAssessment,
    ) -> "RiskAssessmentDTO":
        return cls(
            symbol,
            timeframe,
            assessment.veto,
            assessment.risk_state,
            assessment.invalidation_level,
            assessment.risk_reward,
            assessment.notes,
        )
