from __future__ import annotations

from datetime import datetime

from delta_os.application.agents import VoiceAssistantAgent
from delta_os.application.dto import (
    AlertDTO,
    DashboardStateDTO,
    RankingRowDTO,
    SidebarSectionDTO,
    StatusItemDTO,
    VoiceCommandDTO,
    VoiceStatusDTO,
)


def _dashboard() -> DashboardStateDTO:
    return DashboardStateDTO(
        symbol="RELIANCE",
        status="CSV MODE ACTIVE",
        status_items=(StatusItemDTO("market_status", "breakout_watch"),),
        sidebar_sections=(SidebarSectionDTO("Watchlists", ("nifty_50",)),),
        right_panel_sections=(),
        voice_status=VoiceStatusDTO("idle", "text_stub", False, "none", 0.0, "clear"),
        voice_transcript=(),
        overlays=(),
        timeframe_rows=(),
        ranking_rows=(RankingRowDTO(1, "RELIANCE", "4h", 0.81, "breakout_watch", 0.78, 0.33, "caution", False, "Top compression candidate"),),
        alerts=("RELIANCE breakout probability rising on 4h.",),
        alert_timeline=("RELIANCE breakout probability rising on 4h.",),
        scanner_activity=("scan_symbol=RELIANCE",),
        diagnostics=("dashboard state generated from DTOs only",),
    )


def _alert() -> AlertDTO:
    return AlertDTO(
        symbol="RELIANCE",
        timeframe="4h",
        alert_type="breakout_probability_rising",
        message="RELIANCE breakout probability rising on 4h.",
        confidence=0.78,
        created_at=datetime.fromisoformat("2024-01-01T00:00:00+00:00"),
        reasoning=("touch_count=4",),
        risk_notes=("HTF resistance nearby",),
    )


def test_voice_assistant_agent_returns_grounded_scanner_response_and_audit() -> None:
    response, audit = VoiceAssistantAgent().run(
        VoiceCommandDTO(
            raw_text="Show top compression candidates.",
            audio_source="text",
            timestamp=datetime.fromisoformat("2024-01-01T09:30:00+00:00"),
            user_context=("phase_1",),
            active_symbol="RELIANCE",
            active_timeframe="4h",
        ),
        dashboard_state=_dashboard(),
        alert=_alert(),
    )

    assert response.display_title == "Scanner Query"
    assert audit.parsed_intent.intent_name == "scanner_query"
    assert audit.action_taken == "scan_ranked_opportunities"
    assert audit.veto_state == "clear"


def test_voice_assistant_agent_blocks_execution_requests() -> None:
    response, audit = VoiceAssistantAgent().run(
        VoiceCommandDTO(
            raw_text="Buy RELIANCE now.",
            audio_source="text",
            timestamp=datetime.fromisoformat("2024-01-01T09:31:00+00:00"),
            user_context=("phase_1",),
            active_symbol="RELIANCE",
            active_timeframe="4h",
        ),
        dashboard_state=_dashboard(),
        alert=_alert(),
    )

    assert response.display_title == "Voice Safety"
    assert audit.veto_state == "phase_1_execution_blocked"
    assert audit.action_taken == "execution commands are disabled in Phase 1"


def test_voice_assistant_agent_returns_stale_data_guard_for_old_alert_context() -> None:
    response, audit = VoiceAssistantAgent().run(
        VoiceCommandDTO(
            raw_text="Explain alert.",
            audio_source="text",
            timestamp=datetime.fromisoformat("2024-01-01T16:00:00+00:00"),
            user_context=("phase_1",),
            active_symbol="RELIANCE",
            active_timeframe="4h",
        ),
        dashboard_state=_dashboard(),
        alert=_alert(),
    )

    assert response.display_title == "Data Unavailable"
    assert "stale or unavailable" in response.spoken_text
    assert response.display_body == "alert_age=stale"
    assert audit.veto_state == "data_unavailable"
    assert audit.action_taken == "stale_data_guard"


def test_voice_assistant_agent_returns_data_unavailable_when_required_rows_missing() -> None:
    empty_dashboard = DashboardStateDTO(
        symbol="RELIANCE",
        status="CSV MODE ACTIVE",
        status_items=(StatusItemDTO("market_status", "breakout_watch"),),
        sidebar_sections=(SidebarSectionDTO("Watchlists", ("nifty_50",)),),
        right_panel_sections=(),
        voice_status=VoiceStatusDTO("idle", "text_stub", False, "none", 0.0, "clear"),
        voice_transcript=(),
        overlays=(),
        timeframe_rows=(),
        ranking_rows=(),
        alerts=(),
        alert_timeline=(),
        scanner_activity=(),
        diagnostics=(),
    )
    response, audit = VoiceAssistantAgent().run(
        VoiceCommandDTO(
            raw_text="Show top compression candidates.",
            audio_source="text",
            timestamp=datetime.fromisoformat("2024-01-01T09:30:00+00:00"),
            user_context=("phase_1",),
            active_symbol="RELIANCE",
            active_timeframe="4h",
        ),
        dashboard_state=empty_dashboard,
        alert=_alert(),
    )

    assert response.display_title == "Data Unavailable"
    assert response.display_body == "ranking_rows=missing"
    assert audit.veto_state == "data_unavailable"
