"""Fusion Agent."""

from __future__ import annotations

from delta_os.application.dto.fusion import FusedMarketIntelligenceDTO
from delta_os.application.dto.probability import ProbabilityScoreDTO
from delta_os.application.dto.risk import RiskAssessmentDTO


class FusionAgent:
    """Combine probability and risk state without bypassing vetoes."""

    def run(
        self,
        probability: ProbabilityScoreDTO,
        risk: RiskAssessmentDTO,
    ) -> FusedMarketIntelligenceDTO:
        """Return fused market intelligence DTO."""

        if risk.veto:
            return FusedMarketIntelligenceDTO(
                probability.symbol,
                probability.timeframe,
                0.0,
                "risk_veto",
                True,
                ("Risk Agent veto active; fusion score forced to zero", *risk.notes),
            )

        risk_filter_score = 1.0 if risk.risk_state == "normal" else 0.75
        final_score = (
            probability.breakout_probability
            * (1.0 - probability.fakeout_probability)
            * risk_filter_score
        )
        state = "breakout_watch" if final_score >= 0.45 else "monitor"
        return FusedMarketIntelligenceDTO(
            probability.symbol,
            probability.timeframe,
            final_score,
            state,
            False,
            (
                "final score uses breakout probability, fakeout risk, and risk filter",
                f"risk_state={risk.risk_state}",
            ),
        )
