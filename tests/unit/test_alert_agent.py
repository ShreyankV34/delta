from __future__ import annotations

from datetime import UTC, datetime

from delta_os.application.agents import AlertAgent
from delta_os.application.dto.fusion import FusedMarketIntelligenceDTO
from delta_os.application.dto.liquidity import LiquidityConceptsDTO, LiquidityEventDTO
from delta_os.application.dto.probability import ProbabilityScoreDTO
from delta_os.application.dto.risk import RiskAssessmentDTO
from delta_os.application.dto.structure import StructuralGeometryDTO


FIXED_TIMESTAMP = datetime(2024, 1, 1, tzinfo=UTC)


def test_alert_agent_uses_risk_veto_branch_with_risk_notes_and_reasoning() -> None:
    alert = AlertAgent(lambda: FIXED_TIMESTAMP).run(
        structure=_structure(),
        liquidity=_liquidity(),
        probability=_probability(breakout=0.72, fakeout=0.22),
        risk=_risk(veto=True, notes=("fakeout too high", "risk gate blocked")),
        fusion=_fusion(final_signal_score=0.0, reasoning=("fusion vetoed",)),
    )

    assert alert.alert_type == "risk_veto"
    assert alert.message == "RELIANCE risk veto active on 1m."
    assert alert.confidence == 0.9
    assert alert.created_at == FIXED_TIMESTAMP
    assert alert.risk_notes == ("fakeout too high", "risk gate blocked")
    assert "structure fixture" in alert.reasoning
    assert "probability fixture" in alert.reasoning
    assert "fusion vetoed" in alert.reasoning


def test_alert_agent_uses_breakout_confidence_and_preserves_reasoning_order() -> None:
    alert = AlertAgent(lambda: FIXED_TIMESTAMP).run(
        structure=_structure(reasoning=("structure first", "touch_count=5")),
        liquidity=_liquidity(),
        probability=_probability(
            breakout=0.74,
            fakeout=0.21,
            contributing_factors=("probability second", "htf aligned"),
        ),
        risk=_risk(veto=False, notes=("normal risk",)),
        fusion=_fusion(final_signal_score=0.53, reasoning=("fusion third",)),
    )

    assert alert.alert_type == "breakout_probability_rising"
    assert alert.confidence == 0.74
    assert alert.reasoning == (
        "structure first",
        "touch_count=5",
        "probability second",
        "htf aligned",
        "fusion third",
    )
    assert alert.risk_notes == ("normal risk",)


def test_alert_agent_uses_max_liquidity_event_confidence_when_no_breakout_alert() -> None:
    alert = AlertAgent(lambda: FIXED_TIMESTAMP).run(
        structure=_structure(),
        liquidity=_liquidity(
            events=(
                _event("bos", 0.41, "bos detected"),
                _event("liquidity_sweep", 0.83, "sweep before breakout"),
            )
        ),
        probability=_probability(breakout=0.45, fakeout=0.31),
        risk=_risk(veto=False, notes=("monitor risk",)),
        fusion=_fusion(final_signal_score=0.29, reasoning=("fusion monitor",)),
    )

    assert alert.alert_type == "liquidity_event_detected"
    assert alert.message == "RELIANCE liquidity events detected on 1m."
    assert alert.confidence == 0.83
    assert alert.risk_notes == ("monitor risk",)


def test_alert_agent_falls_back_to_structure_monitor_confidence() -> None:
    alert = AlertAgent(lambda: FIXED_TIMESTAMP).run(
        structure=_structure(wedge_score=0.61),
        liquidity=_liquidity(events=()),
        probability=_probability(breakout=0.33, fakeout=0.27),
        risk=_risk(veto=False, notes=("watch only",)),
        fusion=_fusion(final_signal_score=0.42, reasoning=("fusion monitor",)),
    )

    assert alert.alert_type == "structure_monitor"
    assert alert.message == "RELIANCE structure is being monitored on 1m."
    assert alert.confidence == 0.61
    assert alert.risk_notes == ("watch only",)


def _structure(
    *,
    wedge_score: float = 0.58,
    reasoning: tuple[str, ...] = ("structure fixture",),
) -> StructuralGeometryDTO:
    return StructuralGeometryDTO(
        symbol="RELIANCE",
        timeframe="1m",
        swings=(),
        kind="wedge_like",
        upper_trendline=None,
        lower_trendline=None,
        touch_count=5,
        compression_ratio=0.72,
        angular_difference=0.1,
        wedge_score=wedge_score,
        channel_score=0.36,
        respect_score=0.81,
        reasoning=reasoning,
    )


def _liquidity(
    *,
    events: tuple[LiquidityEventDTO, ...] = (),
) -> LiquidityConceptsDTO:
    return LiquidityConceptsDTO(
        symbol="RELIANCE",
        timeframe="1m",
        events=events,
        event_count=len(events),
        reasoning=("liquidity fixture",),
    )


def _event(event_type: str, confidence: float, reason: str) -> LiquidityEventDTO:
    return LiquidityEventDTO(
        event_type=event_type,
        index=5,
        timestamp=FIXED_TIMESTAMP,
        price=100.0,
        direction="up",
        confidence=confidence,
        reason=reason,
    )


def _probability(
    *,
    breakout: float,
    fakeout: float,
    contributing_factors: tuple[str, ...] = ("probability fixture",),
) -> ProbabilityScoreDTO:
    return ProbabilityScoreDTO(
        symbol="RELIANCE",
        timeframe="1m",
        breakout_probability=breakout,
        fakeout_probability=fakeout,
        reversal_probability=0.24,
        continuation_probability=0.57,
        volatility_expansion_probability=0.66,
        sweep_probability=0.44,
        confidence_tier="medium",
        contributing_factors=contributing_factors,
    )


def _risk(*, veto: bool, notes: tuple[str, ...]) -> RiskAssessmentDTO:
    return RiskAssessmentDTO(
        symbol="RELIANCE",
        timeframe="1m",
        veto=veto,
        risk_state="elevated" if veto else "normal",
        invalidation_level=95.0,
        risk_reward=1.8,
        notes=notes,
    )


def _fusion(
    *,
    final_signal_score: float,
    reasoning: tuple[str, ...],
) -> FusedMarketIntelligenceDTO:
    return FusedMarketIntelligenceDTO(
        symbol="RELIANCE",
        timeframe="1m",
        final_signal_score=final_signal_score,
        market_state="monitor",
        risk_veto=False,
        reasoning=reasoning,
    )
