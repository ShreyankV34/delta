"""Project voice command results into dashboard voice interaction state."""

from __future__ import annotations

from dataclasses import replace

from delta_os.application.dto.ui import DashboardStateDTO, VoiceStatusDTO, VoiceTranscriptEntryDTO
from delta_os.application.dto.voice import VoiceCommandResultDTO


class VoiceInteractionStateUpdater:
    """Update dashboard voice state using deterministic, DTO-only rules."""

    def __init__(self, *, max_transcript_entries: int = 20) -> None:
        self._max_transcript_entries = max(2, int(max_transcript_entries))

    def listening(self, dashboard: DashboardStateDTO) -> DashboardStateDTO:
        """Set dashboard voice state to listening."""

        return self._with_state(dashboard, "listening")

    def processing(self, dashboard: DashboardStateDTO) -> DashboardStateDTO:
        """Set dashboard voice state to processing."""

        return self._with_state(dashboard, "processing")

    def error(self, dashboard: DashboardStateDTO) -> DashboardStateDTO:
        """Set dashboard voice state to error."""

        return self._with_state(dashboard, "error")

    def apply(self, result: VoiceCommandResultDTO) -> VoiceCommandResultDTO:
        """Project one command result into dashboard voice fields."""

        dashboard = result.dashboard
        intent = result.audit.parsed_intent.intent_name
        muted = self._muted_from_intent(dashboard.voice_status.muted, intent)
        status_state = "error" if result.audit.veto_state != "clear" else "responding"
        if result.audit.error_state is not None:
            status_state = "error"

        voice_status = VoiceStatusDTO(
            state=status_state,
            mode=dashboard.voice_status.mode,
            muted=muted,
            last_intent=intent,
            last_confidence=result.audit.parsed_intent.confidence,
            last_veto_state=result.audit.veto_state,
        )

        timestamp = result.audit.timestamp.isoformat()
        transcript = list(dashboard.voice_transcript)
        transcript.append(
            VoiceTranscriptEntryDTO(
                timestamp=timestamp,
                speaker="trader",
                text=result.command.raw_text,
                intent=intent,
                confidence=result.audit.parsed_intent.confidence,
                action=result.audit.action_taken,
                veto_state=result.audit.veto_state,
            )
        )
        transcript.append(
            VoiceTranscriptEntryDTO(
                timestamp=timestamp,
                speaker="delta",
                text=result.response.spoken_text,
                intent=intent,
                confidence=result.response.confidence,
                action="responded",
                veto_state=result.audit.veto_state,
            )
        )
        bounded = tuple(transcript[-self._max_transcript_entries :])
        updated_dashboard = replace(dashboard, voice_status=voice_status, voice_transcript=bounded)
        return replace(result, dashboard=updated_dashboard)

    def _with_state(self, dashboard: DashboardStateDTO, state: str) -> DashboardStateDTO:
        return replace(
            dashboard,
            voice_status=replace(dashboard.voice_status, state=state),
        )

    @staticmethod
    def _muted_from_intent(current: bool, intent_name: str) -> bool:
        if intent_name == "voice_mute":
            return True
        if intent_name == "voice_unmute":
            return False
        return current

