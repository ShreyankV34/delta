"""Alert Agent."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from delta_os.application.dto.alerts import AlertDTO
from delta_os.application.dto.fusion import FusedMarketIntelligenceDTO
from delta_os.application.dto.liquidity import LiquidityConceptsDTO
from delta_os.application.dto.probability import ProbabilityScoreDTO
from delta_os.application.dto.risk import RiskAssessmentDTO
from delta_os.application.dto.structure import StructuralGeometryDTO


class AlertAgent:
    """Create explainable intelligence alerts from DTOs."""

    def __init__(
        self,
        timestamp_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self._timestamp_provider = timestamp_provider or _utc_now

    def run(
        self,
        structure: StructuralGeometryDTO,
        liquidity: LiquidityConceptsDTO,
        probability: ProbabilityScoreDTO,
        risk: RiskAssessmentDTO,
        fusion: FusedMarketIntelligenceDTO,
    ) -> AlertDTO:
        """Return one deterministic alert for the current setup."""

        if risk.veto:
            alert_type = "risk_veto"
            message = f"{probability.symbol} risk veto active on {probability.timeframe}."
            confidence = 0.9
        elif probability.breakout_probability >= 0.6:
            alert_type = "breakout_probability_rising"
            message = f"{probability.symbol} breakout probability rising on {probability.timeframe}."
            confidence = probability.breakout_probability
        elif liquidity.event_count:
            alert_type = "liquidity_event_detected"
            message = f"{probability.symbol} liquidity events detected on {probability.timeframe}."
            confidence = max(event.confidence for event in liquidity.events)
        else:
            alert_type = "structure_monitor"
            message = f"{probability.symbol} structure is being monitored on {probability.timeframe}."
            confidence = max(structure.wedge_score, fusion.final_signal_score)

        reasoning = (
            *structure.reasoning,
            *probability.contributing_factors,
            *fusion.reasoning,
        )
        return AlertDTO(
            probability.symbol,
            probability.timeframe,
            alert_type,
            message,
            confidence,
            self._timestamp_provider(),
            reasoning,
            risk.notes,
        )


def _utc_now() -> datetime:
    return datetime.now(UTC)
