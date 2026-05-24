"""Ranking helper for offline opportunities."""

from __future__ import annotations

from delta_os.domain.services.probability_engine import ProbabilityScores
from delta_os.domain.services.risk_engine import RiskAssessment
from delta_os.domain.services.structure_detector import StructureDetection


class RankingEngine:
    """Compute a deterministic opportunity score."""

    def score(
        self,
        structure: StructureDetection,
        probabilities: ProbabilityScores,
        risk: RiskAssessment,
    ) -> float:
        """Return a rank score in [0, 1]."""

        veto_penalty = 0.35 if risk.veto else 0.0
        risk_reward_component = 0.0
        if risk.risk_reward is not None:
            risk_reward_component = min(risk.risk_reward / 3.0, 1.0) * 0.15
        score = (
            0.35 * structure.wedge_score
            + 0.35 * probabilities.breakout_probability
            + 0.15 * (1.0 - probabilities.fakeout_probability)
            + risk_reward_component
            - veto_penalty
        )
        return max(0.0, min(1.0, score))
