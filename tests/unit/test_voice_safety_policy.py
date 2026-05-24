from __future__ import annotations

from delta_os.application.dto import VoiceIntentDTO
from delta_os.domain.services import VoiceSafetyPolicy


def test_voice_safety_blocks_execution_in_phase_one() -> None:
    decision = VoiceSafetyPolicy().evaluate(
        VoiceIntentDTO("execution_command", {"symbol": "RELIANCE"}, 0.99, ("risk_agent",), "forbidden", True),
        execution_commands_allowed=False,
    )

    assert decision.allowed is False
    assert decision.veto_state == "phase_1_execution_blocked"


def test_voice_safety_respects_risk_veto() -> None:
    decision = VoiceSafetyPolicy().evaluate(
        VoiceIntentDTO("execution_command", {"symbol": "RELIANCE"}, 0.99, ("risk_agent",), "forbidden", True),
        execution_commands_allowed=True,
        risk_veto=True,
    )

    assert decision.allowed is False
    assert decision.veto_state == "risk_veto"


def test_voice_safety_requests_clarification_for_unknown_intent() -> None:
    decision = VoiceSafetyPolicy().evaluate(
        VoiceIntentDTO("unknown", {}, 0.0, (), "unknown", True),
    )

    assert decision.allowed is False
    assert decision.needs_confirmation is True


def test_voice_safety_allows_grounded_market_briefing() -> None:
    decision = VoiceSafetyPolicy().evaluate(
        VoiceIntentDTO("market_briefing", {}, 0.97, ("ranking_agent", "alert_agent"), "low", False),
    )

    assert decision.allowed is True
    assert decision.veto_state == "clear"
