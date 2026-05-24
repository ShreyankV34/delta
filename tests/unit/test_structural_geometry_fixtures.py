from __future__ import annotations

from pathlib import Path

from delta_os.application.agents import (
    DataAgent,
    LiquidityConceptsAgent,
    ProbabilityAgent,
    StructuralGeometryAgent,
)
from delta_os.infrastructure.data import CsvCandleProvider

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _structure_for(filename: str, symbol: str):
    bundle = DataAgent(CsvCandleProvider()).load(FIXTURES / filename, symbol, ("1m",))
    series = bundle.get("1m")
    return series, StructuralGeometryAgent(swing_left=1, swing_right=1).run(series)


def _structure_for_with_agent(filename: str, symbol: str, agent: StructuralGeometryAgent):
    bundle = DataAgent(CsvCandleProvider()).load(FIXTURES / filename, symbol, ("1m",))
    series = bundle.get("1m")
    return series, agent.run(series)


def test_noisy_wedge_fixture_classifies_as_compressing_wedge() -> None:
    _series, structure = _structure_for("noisy_wedge.csv", "WEDGE")

    assert structure.kind == "wedge_like"
    assert structure.touch_count >= 6
    assert structure.compression_ratio < 0.85
    assert structure.wedge_score >= 0.75
    assert structure.upper_trendline is not None
    assert structure.lower_trendline is not None


def test_channel_fixture_preserves_parallel_boundary_signal() -> None:
    _series, structure = _structure_for("channel_like.csv", "CHANNEL")

    assert structure.kind == "channel_like"
    assert structure.touch_count >= 6
    assert 0.9 <= structure.compression_ratio <= 1.25
    assert structure.angular_difference < 0.1
    assert structure.channel_score >= 0.7
    assert structure.channel_score > structure.wedge_score


def test_false_breakout_fixture_feeds_fakeout_probability_inputs() -> None:
    series, structure = _structure_for("false_breakout_sweep.csv", "FAKEOUT")
    liquidity = LiquidityConceptsAgent(sweep_lookback=3).run(series, structure)
    probability = ProbabilityAgent().run(structure, liquidity)

    assert any(event.event_type == "liquidity_sweep" for event in liquidity.events)
    assert not any(event.event_type == "bos" for event in liquidity.events)
    assert probability.fakeout_probability > 0.25
    assert "liquidity sweep increased expansion and fakeout awareness" in (
        probability.contributing_factors
    )


def test_imperfect_respect_fixture_scores_noisy_but_usable_boundaries() -> None:
    _series, structure = _structure_for("imperfect_trendline_respect.csv", "RESPECT")

    assert structure.kind == "wedge_like"
    assert structure.touch_count >= 5
    assert 0.80 <= structure.respect_score < 0.95
    assert structure.wedge_score >= 0.65


def test_calibrated_channel_threshold_can_reject_borderline_channels() -> None:
    _series, structure = _structure_for_with_agent(
        "channel_like.csv",
        "CHANNEL",
        StructuralGeometryAgent(
            swing_left=1,
            swing_right=1,
            channel_score_threshold=0.90,
        ),
    )

    assert structure.kind == "unstable"
    assert structure.channel_score < 0.90


def test_calibrated_wedge_threshold_requires_maturity() -> None:
    _series, structure = _structure_for_with_agent(
        "noisy_wedge.csv",
        "WEDGE",
        StructuralGeometryAgent(
            swing_left=1,
            swing_right=1,
            min_mature_touch_count=7,
        ),
    )

    assert structure.kind == "compressing"
    assert structure.compression_ratio < 0.85
    assert structure.touch_count < 7


def test_structure_reasoning_exposes_classification_thresholds() -> None:
    _series, structure = _structure_for("noisy_wedge.csv", "WEDGE")

    assert any(item.startswith("wedge_score=") for item in structure.reasoning)
    assert any(item.startswith("channel_score=") for item in structure.reasoning)
    assert any(item.startswith("compression_threshold=") for item in structure.reasoning)
    assert any(item.startswith("channel_score_threshold=") for item in structure.reasoning)
