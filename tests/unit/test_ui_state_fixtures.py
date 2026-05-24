from __future__ import annotations

import json
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
from delta_os.application.dto.ui import DashboardStateDTO, MultiTimeframeRowDTO, OverlayDTO, RankingRowDTO
from delta_os.infrastructure.data import CsvCandleProvider
from delta_os.presentation.gui.main_window import (
    bottom_panel_lines,
    build_overlay_lines,
    panel_section_lines,
    ranking_table_lines,
    ranking_row_values,
    sidebar_section_lines,
    status_item_values,
    timeframe_row_values,
    voice_status_lines,
    voice_transcript_lines,
)
from delta_os.application.dto.ui import (
    PanelSectionDTO,
    SidebarSectionDTO,
    StatusItemDTO,
    VoiceStatusDTO,
    VoiceTranscriptEntryDTO,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _load_dashboard_fixture() -> DashboardStateDTO:
    raw = json.loads((FIXTURES / "ui_dashboard_state.json").read_text(encoding="utf-8"))
    overlays = tuple(
        OverlayDTO(
            overlay_type=item["overlay_type"],
            label=item["label"],
            points=tuple((float(point[0]), float(point[1])) for point in item["points"]),
            confidence=float(item["confidence"]),
        )
        for item in raw["overlays"]
    )
    rows = tuple(
        MultiTimeframeRowDTO(
            timeframe=item["timeframe"],
            bias=item["bias"],
            structure=item["structure"],
            liquidity=item["liquidity"],
            volatility=item["volatility"],
            breakout_probability=float(item["breakout_probability"]),
            fakeout_risk=float(item["fakeout_risk"]),
            execution_quality=item["execution_quality"],
            risk_state=item["risk_state"],
            comment=item["comment"],
        )
        for item in raw["timeframe_rows"]
    )
    ranking_rows = tuple(
        RankingRowDTO(
            rank=int(item["rank"]),
            symbol=item["symbol"],
            timeframe=item["timeframe"],
            score=float(item["score"]),
            market_state=item["market_state"],
            breakout_probability=float(item["breakout_probability"]),
            fakeout_probability=float(item["fakeout_probability"]),
            risk_state=item["risk_state"],
            risk_veto=bool(item["risk_veto"]),
            comment=item["comment"],
        )
        for item in raw["ranking_rows"]
    )
    return DashboardStateDTO(
        symbol=raw["symbol"],
        status=raw["status"],
        status_items=tuple(
            StatusItemDTO(label=item["label"], value=item["value"]) for item in raw["status_items"]
        ),
        sidebar_sections=tuple(
            SidebarSectionDTO(title=item["title"], items=tuple(item["items"]))
            for item in raw["sidebar_sections"]
        ),
        right_panel_sections=tuple(
            PanelSectionDTO(title=item["title"], lines=tuple(item["lines"]))
            for item in raw["right_panel_sections"]
        ),
        voice_status=VoiceStatusDTO(
            state=raw["voice_status"]["state"],
            mode=raw["voice_status"]["mode"],
            muted=bool(raw["voice_status"]["muted"]),
            last_intent=raw["voice_status"]["last_intent"],
            last_confidence=float(raw["voice_status"]["last_confidence"]),
            last_veto_state=raw["voice_status"]["last_veto_state"],
        ),
        voice_transcript=tuple(
            VoiceTranscriptEntryDTO(
                timestamp=item["timestamp"],
                speaker=item["speaker"],
                text=item["text"],
                intent=item["intent"],
                confidence=float(item["confidence"]),
                action=item["action"],
                veto_state=item["veto_state"],
            )
            for item in raw["voice_transcript"]
        ),
        overlays=overlays,
        timeframe_rows=rows,
        ranking_rows=ranking_rows,
        alerts=tuple(raw["alerts"]),
        alert_timeline=tuple(raw["alert_timeline"]),
        scanner_activity=tuple(raw["scanner_activity"]),
        diagnostics=tuple(raw["diagnostics"]),
    )


def test_ui_dashboard_fixture_covers_multiple_overlays_and_timeframes() -> None:
    state = _load_dashboard_fixture()

    assert state.symbol == "RELIANCE"
    assert len(state.overlays) >= 3
    assert {overlay.label for overlay in state.overlays} >= {
        "upper_trendline",
        "lower_trendline",
    }
    assert len(state.timeframe_rows) >= 2
    assert {row.timeframe for row in state.timeframe_rows} >= {"1d", "4h"}
    assert len(state.ranking_rows) == 3
    assert any(row.risk_veto for row in state.ranking_rows)


def test_presentation_render_helpers_consume_ui_dto_state_only() -> None:
    state = _load_dashboard_fixture()

    overlay_lines = build_overlay_lines(state)
    row_values = [timeframe_row_values(row) for row in state.timeframe_rows]
    ranking_values = [ranking_row_values(row) for row in state.ranking_rows]
    ranking_lines = ranking_table_lines(state.ranking_rows)
    sidebar_lines = sidebar_section_lines(state.sidebar_sections)
    status_values = status_item_values(state.status_items)
    right_panel = panel_section_lines(state.right_panel_sections)
    bottom_lines = bottom_panel_lines(state)
    voice_status = voice_status_lines(state)
    voice_transcript = voice_transcript_lines(state)

    assert overlay_lines[0].startswith("upper_trendline | confidence=")
    assert overlay_lines[1].startswith("lower_trendline | confidence=")
    assert row_values[0][0] == "1d"
    assert row_values[1][0] == "4h"
    assert row_values[0][5] == "0.71"
    assert row_values[1][6] == "0.33"
    assert ranking_values[0][0] == "1"
    assert ranking_values[0][3] == "0.81"
    assert ranking_values[1][1] == "INFY"
    assert ranking_values[2][8] == "veto"
    assert ranking_lines[2].startswith("3 | HDFCBANK | 1h | 0.58")
    assert sidebar_lines[0] == "Watchlists"
    assert sidebar_lines[1].startswith("  - nifty_50")
    assert status_values[0] == "market_status=breakout_watch"
    assert "provider_health=ready" in status_values
    assert "scan_latency=deterministic_offline" in status_values
    assert status_values[-1] == "app_mode=offline_csv"
    assert any(line.startswith("Universe Selection") for line in sidebar_lines)
    assert any("default_universe=nifty_50" in line for line in sidebar_lines)
    assert any("normal | fakeout<=0.70 | veto=on" in line for line in sidebar_lines)
    assert right_panel[0] == "DELTA Intelligence Summary"
    assert any("breakout=0.71" in line for line in right_panel)
    assert any("risk_state=caution" in line for line in right_panel)
    assert any("execution_quality=improving" in line for line in right_panel)
    assert any(line == "Voice Response Card" for line in right_panel)
    assert any("intent=scanner_query" in line for line in right_panel)
    assert voice_status[0] == "state=responding"
    assert voice_status[3] == "last_intent=scanner_query"
    assert voice_transcript[0].startswith("2024-01-01T09:31:00+00:00")
    assert "Show top compression candidates." in voice_transcript[0]
    assert bottom_lines[0] == "Voice Status"
    assert "HDFCBANK execution quality deteriorating on 1h." in bottom_lines
    assert "(no transcript entries)" not in bottom_lines
    assert "Alert Timeline" in bottom_lines
    assert "Scanner Activity" in bottom_lines
    assert "ranking_rows=3" in bottom_lines
    assert "Diagnostics" in bottom_lines
    assert "ranking table includes veto and non-veto rows" in bottom_lines
    assert "Voice Transcript" in bottom_lines


def test_ui_agent_outputs_overlay_fixture_shape_from_agent_dtos() -> None:
    bundle = DataAgent(CsvCandleProvider()).load(FIXTURES / "sample_candles.csv", "RELIANCE", ("1m",))
    series = bundle.get("1m")
    structure = StructuralGeometryAgent(swing_left=1, swing_right=1).run(series)
    liquidity = LiquidityConceptsAgent(sweep_lookback=3).run(series, structure)
    probability = ProbabilityAgent().run(structure, liquidity)
    risk = RiskAgent().run(series, structure, probability)
    fusion = FusionAgent().run(probability, risk)
    ranking = RankingAgent().run(structure, probability, risk, fusion)
    alert = AlertAgent().run(structure, liquidity, probability, risk, fusion)
    timeframe_summary = TimeframeIntelligenceAgent().run(
        structure,
        liquidity,
        probability,
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
    )

    assert dashboard.status_items[0].label == "market_status"
    assert dashboard.status_items[1].value == "csv"
    assert any(item.label == "provider_health" and item.value == "ready" for item in dashboard.status_items)
    assert any(item.label == "scan_latency" for item in dashboard.status_items)
    assert dashboard.sidebar_sections[0].title == "Watchlists"
    assert any(section.title == "Universe Selection" for section in dashboard.sidebar_sections)
    assert any(section.title == "Filters" for section in dashboard.sidebar_sections)
    assert dashboard.right_panel_sections[0].title == "DELTA Intelligence Summary"
    assert dashboard.right_panel_sections[-1].title == "Execution Quality Panel"
    assert len(dashboard.overlays) == 2
    assert {overlay.label for overlay in dashboard.overlays} == {
        "upper_trendline",
        "lower_trendline",
    }
    assert all(overlay.overlay_type == "trendline" for overlay in dashboard.overlays)
    assert len(dashboard.timeframe_rows) == 1
    assert len(dashboard.ranking_rows) == 1
    assert dashboard.alert_timeline[0] == alert.message
    assert dashboard.scanner_activity == ("scan_symbol=RELIANCE", "analysis_timeframe=1m")
    assert dashboard.voice_status.state == "idle"
    assert dashboard.voice_status.mode == "text_stub"
    assert dashboard.voice_transcript == ()
    assert dashboard.timeframe_rows[0].timeframe == structure.timeframe
    assert dashboard.diagnostics == (
        "dashboard state generated from DTOs only",
        "multi-timeframe table sourced from DTOs",
        "ranking table sourced from DTOs",
        "alert timeline sourced from DTOs",
    )
