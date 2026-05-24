from __future__ import annotations

from pathlib import Path

from delta_os.application.agents import (
    AlertAgent,
    DataAgent,
    FusionAgent,
    LiquidityConceptsAgent,
    ProbabilityAgent,
    RankingAgent,
    RiskAgent,
    StructuralGeometryAgent,
    TimeframeIntelligenceAgent,
    UiAgent,
)
from delta_os.infrastructure.data import CsvCandleProvider

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "sample_candles.csv"


def _phase_one_dtos() -> tuple[object, ...]:
    bundle = DataAgent(CsvCandleProvider()).load(FIXTURE, "RELIANCE", ("1m",))
    series = bundle.get("1m")
    structure = StructuralGeometryAgent(swing_left=1, swing_right=1).run(series)
    liquidity = LiquidityConceptsAgent(sweep_lookback=3).run(series, structure)
    probability = ProbabilityAgent().run(structure, liquidity)
    return series, structure, liquidity, probability


def test_probability_ranking_alert_and_ui_state_are_dto_based() -> None:
    series, structure, liquidity, probability = _phase_one_dtos()
    risk = RiskAgent().run(series, structure, probability)  # type: ignore[arg-type]
    fusion = FusionAgent().run(probability, risk)  # type: ignore[arg-type]
    ranking = RankingAgent().run(structure, probability, risk, fusion)  # type: ignore[arg-type]
    alert = AlertAgent().run(structure, liquidity, probability, risk, fusion)  # type: ignore[arg-type]
    timeframe_summary = TimeframeIntelligenceAgent().run(
        structure,  # type: ignore[arg-type]
        liquidity,  # type: ignore[arg-type]
        probability,  # type: ignore[arg-type]
        risk,
        fusion,
    )
    dashboard = UiAgent().run(
        structure,
        alert,
        (timeframe_summary,),
        ranking,
        probability,
        risk,
        fusion,
        ("scan_symbol=RELIANCE", "analysis_timeframe=1m"),
    )  # type: ignore[arg-type]

    assert 0.0 <= probability.breakout_probability <= 1.0  # type: ignore[union-attr]
    assert 0.0 <= probability.fakeout_probability <= 1.0  # type: ignore[union-attr]
    assert risk.veto is False
    assert fusion.risk_veto is False
    assert 0.0 <= ranking.score <= 1.0
    assert alert.symbol == "RELIANCE"
    assert dashboard.status == "CSV MODE ACTIVE"
    assert dashboard.timeframe_rows[0].breakout_probability == probability.breakout_probability  # type: ignore[union-attr]
    assert dashboard.ranking_rows[0].symbol == ranking.symbol
    assert dashboard.right_panel_sections[0].title == "DELTA Intelligence Summary"


def test_risk_veto_forces_fusion_score_to_zero() -> None:
    series, structure, _liquidity, probability = _phase_one_dtos()
    risk = RiskAgent(max_fakeout_probability=0.01).run(
        series,  # type: ignore[arg-type]
        structure,  # type: ignore[arg-type]
        probability,  # type: ignore[arg-type]
    )
    fusion = FusionAgent().run(probability, risk)  # type: ignore[arg-type]

    assert risk.veto is True
    assert fusion.risk_veto is True
    assert fusion.final_signal_score == 0.0
