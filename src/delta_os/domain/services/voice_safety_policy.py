"""Voice safety policy for the Phase-1 text-command assistant."""

from __future__ import annotations

from dataclasses import dataclass

from delta_os.application.dto.voice import VoiceIntentDTO


@dataclass(frozen=True, slots=True)
class VoiceSafetyDecision:
    """Deterministic safety decision for a parsed intent."""

    allowed: bool
    veto_state: str
    reason: str
    needs_confirmation: bool


class VoiceSafetyPolicy:
    """Apply Phase-1 safety constraints to parsed voice intents."""

    def evaluate(
        self,
        intent: VoiceIntentDTO,
        *,
        execution_commands_allowed: bool = False,
        risk_veto: bool = False,
    ) -> VoiceSafetyDecision:
        """Return the safety decision for one parsed intent."""

        if intent.intent_name == "unknown":
            return VoiceSafetyDecision(False, "clarification_required", "intent not recognized", True)
        if intent.intent_name == "execution_command":
            if not execution_commands_allowed:
                return VoiceSafetyDecision(False, "phase_1_execution_blocked", "execution commands are disabled in Phase 1", True)
            if risk_veto:
                return VoiceSafetyDecision(False, "risk_veto", "risk agent vetoed the requested execution flow", True)
        return VoiceSafetyDecision(True, "clear", "allowed", intent.needs_confirmation)
