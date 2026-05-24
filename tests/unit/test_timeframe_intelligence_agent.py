from __future__ import annotations

from pathlib import Path

from delta_os.application.agents import (
    DataAgent,
    FusionAgent,
    LiquidityConceptsAgent,
    ProbabilityAgent,
    RiskAgent,
    StructuralGeometryAgent,
    TimeframeIntelligenceAgent,
)
from delta_os.application.dto.fusion import FusedMarketIntelligenceDTO
from delta_os.application.dto.liquidity import LiquidityConceptsDTO, LiquidityEventDTO
from delta_os.application.dto.probability import ProbabilityScoreDTO
from delta_os.application.dto.risk import RiskAssessmentDTO
from delta_os.application.dto.structure import StructuralGeometryDTO
from delta_os.infrastructure.data import CsvCandleProvider

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "sample_candles.csv"


def test_timeframe_intelligence_agent_builds_deterministic_summary() -> None:
    bundle = DataAgent(CsvCandleProvider()).load(FIXTURE, "RELIANCE", ("1m",))
    series = bundle.get("1m")
    structure = StructuralGeometryAgent(swing_left=1, swing_right=1).run(series)
    liquidity = LiquidityConceptsAgent(sweep_lookback=3).run(series, structure)
    probability = ProbabilityAgent().run(structure, liquidity)
    risk = RiskAgent().run(series, structure, probability)
    fusion = FusionAgent().run(probability, risk)

    summary = TimeframeIntelligenceAgent().run(structure, liquidity, probability, risk, fusion)

    assert summary.symbol == "RELIANCE"
    assert summary.timeframe == "1m"
    assert 0.0 <= summary.trend_strength <= 1.0
    assert 0.0 <= summary.structural_confidence <= 1.0
    assert 0.0 <= summary.invalidation_risk <= 1.0
    assert summary.execution_quality in {"ready", "developing", "wait", "blocked"}
    assert summary.comment


def test_timeframe_intelligence_agent_aligns_rows_from_higher_to_lower_timeframes() -> None:
    agent = TimeframeIntelligenceAgent()
    summary_1m = agent.run(
        _structure("RELIANCE", "1m", "wedge_like", 5, 0.7, 0.85, 0.55),
        _liquidity("RELIANCE", "1m", 1, "liquidity_sweep"),
        _probability("RELIANCE", "1m", 0.7, 0.2),
        _risk("RELIANCE", "1m", False, "normal", 2.0),
        _fusion("RELIANCE", "1m", 0.5, "breakout_watch", False),
    )
    summary_1d = agent.run(
        _structure("RELIANCE", "1d", "channel_like", 4, 0.9, 0.65, 0.45),
        _liquidity("RELIANCE", "1d", 0, None),
        _probability("RELIANCE", "1d", 0.62, 0.25),
        _risk("RELIANCE", "1d", False, "normal", 1.8),
        _fusion("RELIANCE", "1d", 0.46, "breakout_watch", False),
    )
    summary_5m = agent.run(
        _structure("RELIANCE", "5m", "compressing", 3, 0.74, 0.52, 0.35),
        _liquidity("RELIANCE", "5m", 0, None),
        _probability("RELIANCE", "5m", 0.42, 0.28),
        _risk("RELIANCE", "5m", False, "normal", 1.4),
        _fusion("RELIANCE", "5m", 0.3, "monitor", False),
    )

    aligned = agent.align((summary_1m, summary_1d, summary_5m))

    assert [item.timeframe for item in aligned] == ["1d", "5m", "1m"]
    assert aligned[0].htf_alignment == "lead_context"
    assert aligned[1].htf_alignment in {"aligned_with_htf", "mixed"}
    assert aligned[2].htf_alignment in {"aligned_with_htf", "mixed"}


def _structure(
    symbol: str,
    timeframe: str,
    kind: str,
    touch_count: int,
    compression_ratio: float,
    respect_score: float,
    wedge_score: float,
) -> StructuralGeometryDTO:
    return StructuralGeometryDTO(
        symbol=symbol,
        timeframe=timeframe,
        swings=(),
        kind=kind,
        upper_trendline=None,
        lower_trendline=None,
        touch_count=touch_count,
        compression_ratio=compression_ratio,
        angular_difference=0.1,
        wedge_score=wedge_score,
        channel_score=0.4,
        respect_score=respect_score,
        reasoning=("structure fixture",),
    )


def _liquidity(
    symbol: str,
    timeframe: str,
    event_count: int,
    event_type: str | None,
) -> LiquidityConceptsDTO:
    events = (
        (
            LiquidityEventDTO(
                event_type=event_type,
                index=5,
                timestamp=bundle_timestamp(),
                price=100.0,
                direction="up",
                confidence=0.7,
                reason="fixture event",
            ),
        )
        if event_type is not None
        else ()
    )
    return LiquidityConceptsDTO(
        symbol=symbol,
        timeframe=timeframe,
        events=events,
        event_count=event_count,
        reasoning=("liquidity fixture",),
    )


def _probability(
    symbol: str,
    timeframe: str,
    breakout_probability: float,
    fakeout_probability: float,
) -> ProbabilityScoreDTO:
    return ProbabilityScoreDTO(
        symbol=symbol,
        timeframe=timeframe,
        breakout_probability=breakout_probability,
        fakeout_probability=fakeout_probability,
        reversal_probability=0.25,
        continuation_probability=0.55,
        volatility_expansion_probability=0.6,
        sweep_probability=0.35,
        confidence_tier="medium",
        contributing_factors=("fixture probability",),
    )


def _risk(
    symbol: str,
    timeframe: str,
    veto: bool,
    risk_state: str,
    risk_reward: float | None,
) -> RiskAssessmentDTO:
    return RiskAssessmentDTO(
        symbol=symbol,
        timeframe=timeframe,
        veto=veto,
        risk_state=risk_state,
        invalidation_level=95.0,
        risk_reward=risk_reward,
        notes=("fixture risk",),
    )


def _fusion(
    symbol: str,
    timeframe: str,
    final_signal_score: float,
    market_state: str,
    risk_veto: bool,
) -> FusedMarketIntelligenceDTO:
    return FusedMarketIntelligenceDTO(
        symbol=symbol,
        timeframe=timeframe,
        final_signal_score=final_signal_score,
        market_state=market_state,
        risk_veto=risk_veto,
        reasoning=("fixture fusion",),
    )


def bundle_timestamp():
    from datetime import UTC, datetime

    return datetime(2024, 1, 1, tzinfo=UTC)
