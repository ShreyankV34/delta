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
    VoiceTranscriptEntryDTO,
)
from delta_os.application.use_cases import VoiceAuditHistoryProjection


def _result_with_transcript(entries: tuple[VoiceTranscriptEntryDTO, ...]) -> VoiceCommandResultDTO:
    timestamp = datetime.fromisoformat("2024-01-01T09:30:00+00:00")
    return VoiceCommandResultDTO(
        command=VoiceCommandDTO(
            raw_text="Show top compression candidates.",
            audio_source="text",
            timestamp=timestamp,
            user_context=("phase_1", "offline_csv"),
            active_symbol="RELIANCE",
            active_timeframe="1m",
        ),
        response=VoiceResponseDTO(
            spoken_text="I found 1 ranked opportunities in the current dashboard view.",
            display_title="Scanner Query",
            display_body="scan_focus=compression\nranking_rows=1",
            confidence=0.95,
            citations_to_agent_outputs=("dashboard.ranking_rows",),
            follow_up_options=("Open ranking dashboard", "Analyze active symbol"),
        ),
        audit=VoiceAuditDTO(
            transcript="Show top compression candidates.",
            parsed_intent=VoiceIntentDTO(
                intent_name="scanner_query",
                slots={"scan_focus": "compression"},
                confidence=0.95,
                required_agents=("ranking_agent", "ui_agent"),
                safety_level="medium",
                needs_confirmation=False,
            ),
            action_taken="scan_ranked_opportunities",
            veto_state="clear",
            latency_ms=0,
            error_state=None,
            timestamp=timestamp,
        ),
        context_symbol="RELIANCE",
        context_timeframe="1m",
        market_status="breakout_watch",
        dashboard=DashboardStateDTO(
            symbol="RELIANCE",
            status="CSV MODE ACTIVE",
            status_items=(),
            sidebar_sections=(),
            right_panel_sections=(),
            voice_status=VoiceStatusDTO("responding", "text_stub", False, "scanner_query", 0.95, "clear"),
            voice_transcript=entries,
            overlays=(),
            timeframe_rows=(),
            ranking_rows=(),
            alerts=(),
            alert_timeline=(),
            scanner_activity=(),
            diagnostics=(),
        ),
    )


def test_voice_audit_history_projection_returns_empty_message_when_no_entries() -> None:
    result = _result_with_transcript(())
    lines = VoiceAuditHistoryProjection().project(result)

    assert lines == ("(no audit history)",)


def test_voice_audit_history_projection_returns_compact_recent_rows() -> None:
    entries = (
        VoiceTranscriptEntryDTO("2024-01-01T09:30:00+00:00", "trader", "entry-1", "scanner_query", 0.95, "scan", "clear"),
        VoiceTranscriptEntryDTO("2024-01-01T09:30:00+00:00", "delta", "entry-2", "scanner_query", 0.95, "responded", "clear"),
        VoiceTranscriptEntryDTO("2024-01-01T09:31:00+00:00", "trader", "entry-3", "scanner_query", 0.95, "scan", "clear"),
        VoiceTranscriptEntryDTO("2024-01-01T09:31:00+00:00", "delta", "entry-4", "scanner_query", 0.95, "responded", "clear"),
        VoiceTranscriptEntryDTO("2024-01-01T09:32:00+00:00", "trader", "entry-5", "scanner_query", 0.95, "scan", "clear"),
    )
    result = _result_with_transcript(entries)
    lines = VoiceAuditHistoryProjection(max_rows=3).project(result)

    assert len(lines) == 3
    assert lines[0].startswith("09:31:00 | trader")
    assert lines[-1].startswith("09:32:00 | trader")


def test_voice_audit_history_projection_truncates_long_text() -> None:
    long_text = "x" * 120
    result = _result_with_transcript(
        (
            VoiceTranscriptEntryDTO(
                "2024-01-01T09:32:00+00:00",
                "delta",
                long_text,
                "scanner_query",
                0.95,
                "responded",
                "clear",
            ),
        )
    )
    line = VoiceAuditHistoryProjection(max_text_chars=32).project(result)[0]

    assert line.endswith("...")
