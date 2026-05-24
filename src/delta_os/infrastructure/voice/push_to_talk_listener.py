"""Push-to-talk listener placeholder for Phase-1 offline voice scaffolding."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PushToTalkEvent:
    """Deterministic push-to-talk event payload."""

    state: str
    transcript: str


class PushToTalkListener:
    """Local push-to-talk placeholder without microphone dependency."""

    def poll(self) -> PushToTalkEvent:
        """Return deterministic idle event in Phase 1."""

        return PushToTalkEvent(state="idle", transcript="")
