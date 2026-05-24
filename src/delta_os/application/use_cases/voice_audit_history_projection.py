"""Compact projection helpers for voice audit history."""

from __future__ import annotations

from delta_os.application.dto.voice import VoiceCommandResultDTO


class VoiceAuditHistoryProjection:
    """Project dashboard voice transcript into compact CLI-ready lines."""

    def __init__(self, *, max_rows: int = 4, max_text_chars: int = 72) -> None:
        self._max_rows = max(1, int(max_rows))
        self._max_text_chars = max(16, int(max_text_chars))

    def project(self, result: VoiceCommandResultDTO) -> tuple[str, ...]:
        """Return compact history lines from the result transcript."""

        transcript = result.dashboard.voice_transcript
        if not transcript:
            return ("(no audit history)",)

        selected = transcript[-self._max_rows :]
        lines: list[str] = []
        for entry in selected:
            short_time = _short_timestamp(entry.timestamp)
            compact_text = _compact_text(entry.text, self._max_text_chars)
            lines.append(
                f"{short_time} | {entry.speaker:<6} | {entry.intent:<20} | "
                f"conf={entry.confidence:.2f} | veto={entry.veto_state:<22} | {compact_text}"
            )
        return tuple(lines)


def _short_timestamp(value: str) -> str:
    if "T" not in value:
        return value
    time_part = value.split("T", 1)[1]
    time_part = time_part.split("+", 1)[0]
    time_part = time_part.split("Z", 1)[0]
    return time_part[:8]


def _compact_text(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 1] + "..."
