from __future__ import annotations

from datetime import datetime

from delta_os.application.agents import VoiceResponseComposer
from delta_os.application.dto import (
    AlertDTO,
    DashboardStateDTO,
    RankingRowDTO,
    SidebarSectionDTO,
    StatusItemDTO,
    VoiceIntentDTO,
    VoiceStatusDTO,
)
from delta_os.domain.services import VoiceSafetyDecision


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
        ranking_rows=(
            RankingRowDTO(1, "RELIANCE", "4h", 0.81, "breakout_watch", 0.78, 0.33, "caution", False, "Top compression candidate"),
            RankingRowDTO(2, "INFY", "1d", 0.74, "monitor", 0.66, 0.22, "normal", False, "Higher-timeframe compression"),
        ),
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


def test_voice_response_composer_builds_grounded_market_briefing() -> None:
    response = VoiceResponseComposer().compose(
        VoiceIntentDTO("market_briefing", {}, 0.97, ("ranking_agent",), "low", False),
        VoiceSafetyDecision(True, "clear", "allowed", False),
        dashboard_state=_dashboard(),
        alert=_alert(),
    )

    assert response.display_title == "Market Briefing"
    assert "breakout_watch" in response.spoken_text
    assert response.citations_to_agent_outputs == ("dashboard.status_items", "alert.message")


def test_voice_response_composer_builds_scanner_query_response() -> None:
    response = VoiceResponseComposer().compose(
        VoiceIntentDTO("scanner_query", {"scan_focus": "compression"}, 0.95, ("ranking_agent",), "medium", False),
        VoiceSafetyDecision(True, "clear", "allowed", False),
        dashboard_state=_dashboard(),
    )

    assert response.display_title == "Scanner Query"
    assert "ranking_rows=2" in response.display_body
    assert response.follow_up_options[0] == "Open ranking dashboard"


def test_voice_response_composer_returns_blocked_safety_message() -> None:
    response = VoiceResponseComposer().compose(
        VoiceIntentDTO("execution_command", {"symbol": "RELIANCE"}, 0.99, ("risk_agent",), "forbidden", True),
        VoiceSafetyDecision(False, "phase_1_execution_blocked", "execution commands are disabled in Phase 1", True),
    )

    assert response.display_title == "Voice Safety"
    assert "Phase 1" in response.spoken_text
    assert response.citations_to_agent_outputs == ()


def test_voice_response_composer_builds_voice_mute_response() -> None:
    response = VoiceResponseComposer().compose(
        VoiceIntentDTO("voice_mute", {"muted": "true"}, 0.98, ("ui_agent",), "low", False),
        VoiceSafetyDecision(True, "clear", "allowed", False),
        dashboard_state=_dashboard(),
    )

    assert response.display_title == "Voice Controls"
    assert response.display_body == "muted=on"
