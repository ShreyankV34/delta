"""Timeframe intelligence agent."""

from __future__ import annotations

from delta_os.application.dto.fusion import FusedMarketIntelligenceDTO
from delta_os.application.dto.liquidity import LiquidityConceptsDTO
from delta_os.application.dto.probability import ProbabilityScoreDTO
from delta_os.application.dto.risk import RiskAssessmentDTO
from delta_os.application.dto.structure import StructuralGeometryDTO
from delta_os.application.dto.timeframe_intelligence import TimeframeIntelligenceDTO


_TIMEFRAME_PRIORITY = {
    "1mo": 0,
    "1M": 0,
    "1w": 1,
    "1W": 1,
    "1d": 2,
    "1D": 2,
    "4h": 3,
    "4H": 3,
    "1h": 4,
    "1H": 4,
    "15m": 5,
    "5m": 6,
    "1m": 7,
}


class TimeframeIntelligenceAgent:
    """Build deterministic timeframe summaries from existing agent DTOs."""

    def run(
        self,
        structure: StructuralGeometryDTO,
        liquidity: LiquidityConceptsDTO,
        probability: ProbabilityScoreDTO,
        risk: RiskAssessmentDTO,
        fusion: FusedMarketIntelligenceDTO,
    ) -> TimeframeIntelligenceDTO:
        """Return a summary DTO for one timeframe."""

        trend_strength = min(
            1.0,
            max(
                structure.wedge_score,
                structure.channel_score,
                structure.respect_score,
                min(structure.touch_count / 5.0, 1.0),
            ),
        )
        structural_confidence = min(
            1.0,
            max(
                trend_strength,
                (probability.breakout_probability + (1.0 - probability.fakeout_probability)) / 2.0,
            ),
        )
        invalidation_risk = min(
            1.0,
            max(
                probability.fakeout_probability,
                1.0 - (risk.risk_reward or 0.0) / 4.0 if risk.risk_reward else probability.fakeout_probability,
            ),
        )
        institutional_participation_probability = min(
            1.0,
            max(
                0.0,
                (
                    structure.respect_score
                    + min(structure.touch_count / 5.0, 1.0)
                    + probability.breakout_probability
                )
                / 3.0,
            ),
        )
        return TimeframeIntelligenceDTO(
            symbol=structure.symbol,
            timeframe=structure.timeframe,
            bias=_bias_label(probability, risk, fusion),
            trend_strength=trend_strength,
            structure_state=structure.kind,
            liquidity_state=_liquidity_state(liquidity),
            volatility_regime=_volatility_regime(structure),
            compression_state=_compression_state(structure),
            breakout_probability=probability.breakout_probability,
            fakeout_probability=probability.fakeout_probability,
            reversal_probability=probability.reversal_probability,
            continuation_probability=probability.continuation_probability,
            structural_confidence=structural_confidence,
            htf_alignment="standalone",
            invalidation_risk=invalidation_risk,
            institutional_participation_probability=institutional_participation_probability,
            market_regime=fusion.market_state,
            execution_quality=_execution_quality(probability, risk, fusion),
            risk_state=risk.risk_state,
            comment=_comment(structure, liquidity, fusion),
        )

    def align(self, summaries: tuple[TimeframeIntelligenceDTO, ...]) -> tuple[TimeframeIntelligenceDTO, ...]:
        """Annotate summaries with higher-timeframe alignment and stable ordering."""

        ordered = tuple(sorted(summaries, key=lambda item: (_priority(item.timeframe), item.timeframe)))
        aligned: list[TimeframeIntelligenceDTO] = []
        higher_biases: list[str] = []
        for summary in ordered:
            alignment = _alignment_label(summary.bias, higher_biases)
            aligned.append(
                TimeframeIntelligenceDTO(
                    symbol=summary.symbol,
                    timeframe=summary.timeframe,
                    bias=summary.bias,
                    trend_strength=summary.trend_strength,
                    structure_state=summary.structure_state,
                    liquidity_state=summary.liquidity_state,
                    volatility_regime=summary.volatility_regime,
                    compression_state=summary.compression_state,
                    breakout_probability=summary.breakout_probability,
                    fakeout_probability=summary.fakeout_probability,
                    reversal_probability=summary.reversal_probability,
                    continuation_probability=summary.continuation_probability,
                    structural_confidence=summary.structural_confidence,
                    htf_alignment=alignment,
                    invalidation_risk=summary.invalidation_risk,
                    institutional_participation_probability=summary.institutional_participation_probability,
                    market_regime=summary.market_regime,
                    execution_quality=summary.execution_quality,
                    risk_state=summary.risk_state,
                    comment=summary.comment,
                )
            )
            if summary.bias in {"bullish", "bearish"}:
                higher_biases.append(summary.bias)
        return tuple(aligned)


def _priority(timeframe: str) -> int:
    return _TIMEFRAME_PRIORITY.get(timeframe, 99)


def _bias_label(
    probability: ProbabilityScoreDTO,
    risk: RiskAssessmentDTO,
    fusion: FusedMarketIntelligenceDTO,
) -> str:
    if risk.veto:
        return "blocked"
    if probability.breakout_probability >= 0.55 and fusion.final_signal_score >= 0.35:
        return "bullish"
    if probability.fakeout_probability >= 0.55 or risk.risk_state != "normal":
        return "bearish"
    return "neutral"


def _liquidity_state(liquidity: LiquidityConceptsDTO) -> str:
    if not liquidity.events:
        return "quiet"
    event_types = {event.event_type for event in liquidity.events}
    if "liquidity_sweep" in event_types:
        return "sweep_detected"
    if "bos" in event_types or "choch" in event_types:
        return "structural_shift"
    return "active"


def _volatility_regime(structure: StructuralGeometryDTO) -> str:
    if structure.compression_ratio <= 0.75:
        return "compressed"
    if structure.compression_ratio >= 1.1:
        return "expanded"
    return "balanced"


def _compression_state(structure: StructuralGeometryDTO) -> str:
    if structure.kind in {"wedge_like", "compressing"}:
        return "building"
    if structure.kind == "expanding":
        return "released"
    return "neutral"


def _execution_quality(
    probability: ProbabilityScoreDTO,
    risk: RiskAssessmentDTO,
    fusion: FusedMarketIntelligenceDTO,
) -> str:
    if risk.veto:
        return "blocked"
    if fusion.final_signal_score >= 0.45 and probability.fakeout_probability <= 0.35:
        return "ready"
    if probability.breakout_probability >= 0.45:
        return "developing"
    return "wait"


def _comment(
    structure: StructuralGeometryDTO,
    liquidity: LiquidityConceptsDTO,
    fusion: FusedMarketIntelligenceDTO,
) -> str:
    liquidity_note = liquidity.reasoning[0] if liquidity.reasoning else "no major liquidity event"
    fusion_note = fusion.reasoning[0] if fusion.reasoning else fusion.market_state
    return f"{structure.kind}; {liquidity_note}; {fusion_note}"


def _alignment_label(bias: str, higher_biases: list[str]) -> str:
    directional_biases = [item for item in higher_biases if item in {"bullish", "bearish"}]
    if bias == "blocked":
        return "risk_blocked"
    if not directional_biases:
        return "lead_context"
    dominant = directional_biases[0]
    if bias == dominant:
        return "aligned_with_htf"
    if bias in {"bullish", "bearish"} and bias != dominant:
        return "counter_htf"
    return "mixed"
