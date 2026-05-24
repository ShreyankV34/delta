"""Baseline risk assessment and veto rules."""

from __future__ import annotations

from dataclasses import dataclass

from delta_os.domain.entities.candle import CandleSeries
from delta_os.domain.services.probability_engine import ProbabilityScores
from delta_os.domain.services.structure_detector import StructureDetection


@dataclass(frozen=True, slots=True)
class RiskAssessment:
    """Risk Agent output."""

    veto: bool
    risk_state: str
    invalidation_level: float | None
    risk_reward: float | None
    notes: tuple[str, ...]


class BaselineRiskEngine:
    """Deterministic Phase-1 risk gate."""

    def __init__(
        self,
        max_fakeout_probability: float = 0.7,
        min_breakout_probability: float = 0.25,
    ) -> None:
        self._max_fakeout_probability = max_fakeout_probability
        self._min_breakout_probability = min_breakout_probability

    def assess(
        self,
        series: CandleSeries,
        structure: StructureDetection,
        probabilities: ProbabilityScores,
    ) -> RiskAssessment:
        """Assess baseline risk and veto state."""

        notes: list[str] = []
        veto = False
        if probabilities.fakeout_probability > self._max_fakeout_probability:
            veto = True
            notes.append("fakeout probability exceeds risk profile")
        if probabilities.breakout_probability < self._min_breakout_probability:
            veto = True
            notes.append("breakout probability is below risk profile")

        invalidation = None
        risk_reward = None
        if series.candles and structure.lower_trendline is not None:
            last_index = len(series.candles) - 1
            last_close = series.candles[-1].close
            invalidation = structure.lower_trendline.value_at(last_index)
            risk = max(last_close - invalidation, 0.000001)
            reward = max(structure.upper_trendline.value_at(last_index) - last_close, 0.0) if structure.upper_trendline else 0.0
            risk_reward = reward / risk
            if risk_reward < 0.5:
                notes.append("risk/reward is weak on baseline structure")

        state = "veto" if veto else "caution" if notes else "normal"
        return RiskAssessment(veto, state, invalidation, risk_reward, tuple(notes))
