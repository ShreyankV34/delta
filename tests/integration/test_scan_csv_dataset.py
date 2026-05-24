from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

import pytest

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
from delta_os.application.use_cases import ScanCsvDatasetUseCase
from delta_os.infrastructure.config import YamlConfigLoader
from delta_os.infrastructure.data import CsvCandleProvider
from delta_os.presentation.cli.main import _build_use_case

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "sample_candles.csv"


def _build_scan_use_case(alert_agent: AlertAgent | None = None) -> ScanCsvDatasetUseCase:
    return ScanCsvDatasetUseCase(
        data_agent=DataAgent(CsvCandleProvider()),
        structural_agent=StructuralGeometryAgent(swing_left=1, swing_right=1),
        liquidity_agent=LiquidityConceptsAgent(sweep_lookback=3),
        probability_agent=ProbabilityAgent(),
        risk_agent=RiskAgent(),
        fusion_agent=FusionAgent(),
        ranking_agent=RankingAgent(),
        alert_agent=alert_agent or AlertAgent(),
        timeframe_agent=TimeframeIntelligenceAgent(),
        ui_agent=UiAgent(),
    )


def test_scan_csv_dataset_runs_full_phase_one_pipeline() -> None:
    use_case = _build_scan_use_case()

    result = use_case.run(FIXTURE, "RELIANCE", ("1m", "5m"), analysis_timeframe="1m")
    serialized = result.to_dict()

    assert result.candles.symbol == "RELIANCE"
    assert result.structure.kind in {
        "wedge_like",
        "channel_like",
        "compressing",
        "expanding",
        "unstable",
    }
    assert result.alert.message in serialized["dashboard"]["alerts"]
    assert isinstance(serialized["alert"]["created_at"], str)
    assert len(result.timeframe_intelligence) >= 2
    assert result.dashboard.timeframe_rows[0].timeframe == result.timeframe_intelligence[0].timeframe


def test_scan_csv_dataset_logs_successful_lifecycle(caplog: pytest.LogCaptureFixture) -> None:
    use_case = _build_scan_use_case()

    with caplog.at_level(logging.INFO):
        result = use_case.run(FIXTURE, "RELIANCE", ("1m", "5m"), analysis_timeframe="1m")

    messages = [record.getMessage() for record in caplog.records]
    assert "starting market scan" in messages
    assert "market scan completed" in messages
    assert result.candles.symbol == "RELIANCE"


def test_scan_csv_dataset_logs_failure_context_for_bad_csv(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    broken = tmp_path / "broken.csv"
    broken.write_text(
        "timestamp,open,high\n2024-01-01 09:15:00,100,101\n",
        encoding="utf-8",
    )
    use_case = _build_scan_use_case()

    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError, match="missing required columns"):
            use_case.run(broken, "RELIANCE", ("1m",), analysis_timeframe="1m")

    failure_records = [record for record in caplog.records if record.getMessage() == "market scan failed"]
    assert len(failure_records) == 1
    record = failure_records[0]
    assert getattr(record, "symbol") == "RELIANCE"
    assert getattr(record, "analysis_timeframe") == "1m"
    assert getattr(record, "data_source_path") == str(broken)


def test_scan_csv_dataset_replay_is_identical_with_fixed_alert_timestamp() -> None:
    fixed_timestamp = datetime(2024, 1, 1, tzinfo=UTC)
    use_case = _build_scan_use_case(AlertAgent(lambda: fixed_timestamp))

    first = use_case.run(FIXTURE, "RELIANCE", ("1m", "5m"), analysis_timeframe="1m")
    second = use_case.run(FIXTURE, "RELIANCE", ("1m", "5m"), analysis_timeframe="1m")

    assert first.to_dict() == second.to_dict()
    assert first.alert.created_at == fixed_timestamp


def test_config_driven_use_case_supports_deterministic_replay() -> None:
    config = YamlConfigLoader().load(Path("configs/app.yaml"))
    use_case = _build_use_case(config)
    source_timeframe = config["timeframes"]["source"]
    enabled = tuple(config["timeframes"]["enabled"])
    target_timeframes = tuple(dict.fromkeys((source_timeframe, *enabled)))

    first = use_case.run(FIXTURE, "RELIANCE", target_timeframes, analysis_timeframe=source_timeframe)
    second = use_case.run(FIXTURE, "RELIANCE", target_timeframes, analysis_timeframe=source_timeframe)

    assert first.to_dict() == second.to_dict()
    expected_timestamp = config["agents"]["deterministic_alert_timestamp_utc"]
    expected_iso = (
        expected_timestamp.isoformat()
        if hasattr(expected_timestamp, "isoformat")
        else str(expected_timestamp)
    )
    assert first.alert.created_at.isoformat() == expected_iso


def test_scan_csv_dataset_builds_ordered_multi_timeframe_intelligence_rows() -> None:
    use_case = _build_scan_use_case()

    result = use_case.run(
        FIXTURE,
        "RELIANCE",
        ("1m", "5m", "15m", "1h", "4h", "1d"),
        analysis_timeframe="1m",
    )

    ordered_timeframes = [item.timeframe for item in result.timeframe_intelligence]

    assert ordered_timeframes == ["1d", "4h", "1h", "15m", "5m", "1m"]
    assert result.dashboard.timeframe_rows[0].timeframe == "1d"
    assert result.dashboard.timeframe_rows[-1].timeframe == "1m"
    assert all(item.comment for item in result.timeframe_intelligence)
    assert all(item.htf_alignment for item in result.timeframe_intelligence)
