from __future__ import annotations

from pathlib import Path

from delta_os.application.agents import DataAgent, LiquidityConceptsAgent, StructuralGeometryAgent
from delta_os.infrastructure.data import CsvCandleProvider

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "sample_candles.csv"


def test_structural_geometry_agent_returns_trendline_dto() -> None:
    bundle = DataAgent(CsvCandleProvider()).load(FIXTURE, "RELIANCE", ("1m",))
    series = bundle.get("1m")

    structure = StructuralGeometryAgent(swing_left=1, swing_right=1).run(series)

    assert structure.symbol == "RELIANCE"
    assert structure.timeframe == "1m"
    assert structure.touch_count >= 2
    assert structure.upper_trendline is not None
    assert structure.lower_trendline is not None
    assert 0.0 <= structure.wedge_score <= 1.0
    assert {swing.kind for swing in structure.swings} >= {"high", "low"}


def test_liquidity_concepts_agent_detects_fvg_sweep_and_bos() -> None:
    bundle = DataAgent(CsvCandleProvider()).load(FIXTURE, "RELIANCE", ("1m",))
    series = bundle.get("1m")
    structure = StructuralGeometryAgent(swing_left=1, swing_right=1).run(series)

    liquidity = LiquidityConceptsAgent(sweep_lookback=3).run(series, structure)

    event_types = {event.event_type for event in liquidity.events}
    assert "fair_value_gap" in event_types
    assert "liquidity_sweep" in event_types
    assert "bos" in event_types
    assert liquidity.event_count == len(liquidity.events)
