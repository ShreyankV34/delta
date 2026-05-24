from __future__ import annotations

from datetime import datetime

from delta_os.application.agents import VoiceIntentRouter
from delta_os.application.dto import VoiceCommandDTO


def _command(raw_text: str, *, symbol: str | None = "RELIANCE", timeframe: str | None = "15m") -> VoiceCommandDTO:
    return VoiceCommandDTO(
        raw_text=raw_text,
        audio_source="text",
        timestamp=datetime.fromisoformat("2024-01-01T09:30:00+00:00"),
        user_context=("phase_1",),
        active_symbol=symbol,
        active_timeframe=timeframe,
    )


def test_voice_router_parses_scanner_query() -> None:
    intent = VoiceIntentRouter().parse(_command("Show top compression candidates on daily and four-hour."))

    assert intent.intent_name == "scanner_query"
    assert intent.slots["scan_focus"] == "compression"
    assert intent.required_agents == ("ranking_agent", "ui_agent")


def test_voice_router_parses_symbol_analysis() -> None:
    intent = VoiceIntentRouter().parse(_command("Analyze INFY across daily and four-hour.", symbol=None))
    routes = VoiceIntentRouter().routes(intent)

    assert intent.intent_name == "symbol_analysis"
    assert intent.slots["symbol"] == "INFY"
    assert routes[0].target_agent == "timeframe_agent"
    assert routes[1].use_case == "focus_symbol"


def test_voice_router_parses_ui_navigation() -> None:
    intent = VoiceIntentRouter().parse(_command("Open the risk panel."))

    assert intent.intent_name == "ui_navigation"
    assert intent.slots["panel"] == "risk"


def test_voice_router_parses_execution_command() -> None:
    intent = VoiceIntentRouter().parse(_command("Buy RELIANCE now."))
    routes = VoiceIntentRouter().routes(intent)

    assert intent.intent_name == "execution_command"
    assert intent.safety_level == "forbidden"
    assert routes[0].target_agent == "risk_agent"


def test_voice_router_parses_mute_and_unmute_commands() -> None:
    router = VoiceIntentRouter()
    mute_intent = router.parse(_command("Mute voice responses."))
    unmute_intent = router.parse(_command("Unmute voice responses."))
    mute_routes = router.routes(mute_intent)
    unmute_routes = router.routes(unmute_intent)

    assert mute_intent.intent_name == "voice_mute"
    assert mute_intent.slots["muted"] == "true"
    assert mute_routes[0].use_case == "set_voice_muted"

    assert unmute_intent.intent_name == "voice_unmute"
    assert unmute_intent.slots["muted"] == "false"
    assert unmute_routes[0].use_case == "set_voice_muted"


def test_voice_router_marks_unknown_commands_for_clarification() -> None:
    intent = VoiceIntentRouter().parse(_command("Do the thing from yesterday."))

    assert intent.intent_name == "unknown"
    assert intent.needs_confirmation is True
    assert intent.confidence == 0.0
