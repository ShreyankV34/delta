from __future__ import annotations

from datetime import datetime

from delta_os.application.dto import (
    DashboardStateDTO,
    VoiceAuditDTO,
    VoiceCommandDTO,
    VoiceCommandResultDTO,
    VoiceIntentDTO,
    VoiceResponseDTO,
    VoiceStatusDTO,
)
from delta_os.application.use_cases import VoiceInteractionStateUpdater


def _dashboard(*, transcript_count: int = 0, muted: bool = False) -> DashboardStateDTO:
    transcript = tuple(
        [
            {
                "timestamp": f"2024-01-01T09:{index:02d}:00+00:00",
                "speaker": "trader",
                "text": f"entry-{index}",
                "intent": "scanner_query",
                "confidence": 0.9,
                "action": "scan_ranked_opportunities",
                "veto_state": "clear",
            }
            for index in range(transcript_count)
        ]
    )
    from delta_os.application.dto import VoiceTranscriptEntryDTO

    return DashboardStateDTO(
        symbol="RELIANCE",
        status="CSV MODE ACTIVE",
        status_items=(),
        sidebar_sections=(),
        right_panel_sections=(),
        voice_status=VoiceStatusDTO("idle", "text_stub", muted, "none", 0.0, "clear"),
        voice_transcript=tuple(VoiceTranscriptEntryDTO(**item) for item in transcript),
        overlays=(),
        timeframe_rows=(),
        ranking_rows=(),
        alerts=(),
        alert_timeline=(),
        scanner_activity=(),
        diagnostics=(),
    )


def _result(
    dashboard: DashboardStateDTO,
    *,
    raw_text: str = "Show top compression candidates.",
    intent_name: str = "scanner_query",
    response_text: str = "I found 1 ranked opportunities in the current dashboard view.",
    veto_state: str = "clear",
) -> VoiceCommandResultDTO:
    timestamp = datetime.fromisoformat("2024-01-01T09:30:00+00:00")
    return VoiceCommandResultDTO(
        command=VoiceCommandDTO(
            raw_text=raw_text,
            audio_source="text",
            timestamp=timestamp,
            user_context=("phase_1", "offline_csv"),
            active_symbol="RELIANCE",
            active_timeframe="1m",
        ),
        response=VoiceResponseDTO(
            spoken_text=response_text,
            display_title="Scanner Query",
            display_body="scan_focus=compression\nranking_rows=1",
            confidence=0.95,
            citations_to_agent_outputs=("dashboard.ranking_rows",),
            follow_up_options=("Open ranking dashboard", "Analyze active symbol"),
        ),
        audit=VoiceAuditDTO(
            transcript=raw_text,
            parsed_intent=VoiceIntentDTO(
                intent_name=intent_name,
                slots={},
                confidence=0.95,
                required_agents=("ui_agent",),
                safety_level="low",
                needs_confirmation=False,
            ),
            action_taken="scan_ranked_opportunities",
            veto_state=veto_state,
            latency_ms=0,
            error_state=None,
            timestamp=timestamp,
        ),
        context_symbol="RELIANCE",
        context_timeframe="1m",
        market_status="breakout_watch",
        dashboard=dashboard,
    )


def test_voice_interaction_state_updater_projects_result_into_dashboard_voice_fields() -> None:
    result = VoiceInteractionStateUpdater().apply(_result(_dashboard()))

    assert result.dashboard.voice_status.state == "responding"
    assert result.dashboard.voice_status.last_intent == "scanner_query"
    assert result.dashboard.voice_status.last_veto_state == "clear"
    assert len(result.dashboard.voice_transcript) == 2
    assert result.dashboard.voice_transcript[0].speaker == "trader"
    assert result.dashboard.voice_transcript[1].speaker == "delta"


def test_voice_interaction_state_updater_truncates_transcript_history() -> None:
    updater = VoiceInteractionStateUpdater(max_transcript_entries=3)
    result = updater.apply(_result(_dashboard(transcript_count=4)))

    assert len(result.dashboard.voice_transcript) == 3
    assert result.dashboard.voice_transcript[-1].speaker == "delta"


def test_voice_interaction_state_updater_exposes_listening_processing_and_error_states() -> None:
    updater = VoiceInteractionStateUpdater()
    dashboard = _dashboard()
    listening = updater.listening(dashboard)
    processing = updater.processing(listening)
    error_state = updater.error(processing)

    assert listening.voice_status.state == "listening"
    assert processing.voice_status.state == "processing"
    assert error_state.voice_status.state == "error"


def test_voice_interaction_state_updater_sets_error_state_for_vetoed_actions() -> None:
    result = VoiceInteractionStateUpdater().apply(
        _result(_dashboard(), raw_text="Buy RELIANCE now.", intent_name="execution_command", veto_state="phase_1_execution_blocked")
    )

    assert result.dashboard.voice_status.state == "error"
    assert result.dashboard.voice_status.last_veto_state == "phase_1_execution_blocked"


def test_voice_interaction_state_updater_handles_mute_and_unmute_intents() -> None:
    updater = VoiceInteractionStateUpdater()
    muted = updater.apply(
        _result(
            _dashboard(),
            raw_text="Mute voice responses.",
            intent_name="voice_mute",
            response_text="Voice responses are now muted. Text cards stay visible.",
        )
    )
    unmuted = updater.apply(
        _result(
            muted.dashboard,
            raw_text="Unmute voice responses.",
            intent_name="voice_unmute",
            response_text="Voice responses are now unmuted.",
        )
    )

    assert muted.dashboard.voice_status.muted is True
    assert unmuted.dashboard.voice_status.muted is False

