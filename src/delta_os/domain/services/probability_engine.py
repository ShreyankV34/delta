"""Baseline probability scoring."""

from __future__ import annotations

from dataclasses import dataclass

from delta_os.domain.services.liquidity_concepts import LiquidityEvent
from delta_os.domain.services.structure_detector import StructureDetection


@dataclass(frozen=True, slots=True)
class ProbabilityScores:
    """Explainable baseline probability output."""

    breakout_probability: float
    fakeout_probability: float
    reversal_probability: float
    continuation_probability: float
    volatility_expansion_probability: float
    sweep_probability: float
    confidence_tier: str
    contributing_factors: tuple[str, ...]


class BaselineProbabilityEngine:
    """Config-driven deterministic baseline probability model."""

    def __init__(self, breakout_base: float = 0.35, fakeout_base: float = 0.25) -> None:
        self._breakout_base = breakout_base
        self._fakeout_base = fakeout_base

    def score(
        self,
        structure: StructureDetection,
        liquidity_events: tuple[LiquidityEvent, ...],
    ) -> ProbabilityScores:
        """Score a setup from structural and liquidity features."""

        event_types = {event.event_type for event in liquidity_events}
        has_bos = "bos" in event_types
        has_sweep = "liquidity_sweep" in event_types
        has_fvg = "fair_value_gap" in event_types

        factors = [
            f"structure={structure.kind.value}",
            f"wedge_score={structure.wedge_score:.3f}",
            f"touch_count={structure.touch_count}",
        ]
        breakout = self._breakout_base + 0.35 * structure.wedge_score
        fakeout = self._fakeout_base + (0.18 if structure.touch_count < 4 else 0.0)

        if has_bos:
            breakout += 0.12
            fakeout -= 0.05
            factors.append("BOS confirmation increased breakout probability")
        if has_sweep:
            breakout += 0.08
            fakeout += 0.05
            factors.append("liquidity sweep increased expansion and fakeout awareness")
        if has_fvg:
            breakout += 0.05
            factors.append("fair value gap added displacement evidence")

        breakout = _clamp(breakout)
        fakeout = _clamp(fakeout)
        reversal = _clamp(0.2 + fakeout * 0.35)
        continuation = _clamp(0.25 + breakout * 0.55 - fakeout * 0.15)
        expansion = _clamp(0.3 + (1.0 - structure.compression_ratio) * 0.45 + (0.1 if has_fvg else 0.0))
        sweep_probability = _clamp(0.15 + (0.25 if has_sweep else 0.0) + fakeout * 0.2)

        tier = "high" if breakout >= 0.7 else "medium" if breakout >= 0.45 else "low"
        return ProbabilityScores(
            breakout,
            fakeout,
            reversal,
            continuation,
            expansion,
            sweep_probability,
            tier,
            tuple(factors),
        )


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
