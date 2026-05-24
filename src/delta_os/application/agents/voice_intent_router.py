"""Deterministic text-command parser and router for Phase 1."""

from __future__ import annotations

import re

from delta_os.application.dto.voice import VoiceCommandDTO, VoiceIntentDTO, VoiceRouteDTO


class VoiceIntentRouter:
    """Parse text commands into deterministic intents and routes."""

    def parse(self, command: VoiceCommandDTO) -> VoiceIntentDTO:
        """Parse one command into an intent DTO."""

        normalized = command.raw_text.strip().lower()
        symbol = command.active_symbol or _extract_symbol(command.raw_text)

        if any(phrase in normalized for phrase in ("buy ", "sell ", "place order", "execute trade")):
            return VoiceIntentDTO(
                "execution_command",
                {"symbol": symbol or "UNKNOWN"},
                0.99,
                ("risk_agent",),
                "forbidden",
                True,
            )
        if "market briefing" in normalized:
            return VoiceIntentDTO(
                "market_briefing",
                {},
                0.97,
                ("ranking_agent", "alert_agent", "ui_agent"),
                "low",
                False,
            )
        if any(phrase in normalized for phrase in ("top compression", "compression candidates")):
            return VoiceIntentDTO(
                "scanner_query",
                {"scan_focus": "compression"},
                0.95,
                ("ranking_agent", "ui_agent"),
                "medium",
                False,
            )
        if any(phrase in normalized for phrase in ("unmute voice", "unmute responses", "unmute delta")):
            return VoiceIntentDTO(
                "voice_unmute",
                {"muted": "false"},
                0.98,
                ("ui_agent",),
                "low",
                False,
            )
        if any(phrase in normalized for phrase in ("mute voice", "mute responses", "mute delta")):
            return VoiceIntentDTO(
                "voice_mute",
                {"muted": "true"},
                0.98,
                ("ui_agent",),
                "low",
                False,
            )
        if normalized.startswith("analyze "):
            return VoiceIntentDTO(
                "symbol_analysis",
                {"symbol": symbol or "UNKNOWN", "timeframe": command.active_timeframe or "multi"},
                0.94,
                ("timeframe_agent", "fusion_agent", "ui_agent"),
                "medium",
                False,
            )
        if "open the risk panel" in normalized or "show the risk panel" in normalized:
            return VoiceIntentDTO(
                "ui_navigation",
                {"panel": "risk"},
                0.96,
                ("ui_agent",),
                "low",
                False,
            )
        if "why is this alert" in normalized or "explain alert" in normalized:
            return VoiceIntentDTO(
                "alert_explanation",
                {"symbol": symbol or "UNKNOWN"},
                0.93,
                ("alert_agent", "ui_agent"),
                "low",
                False,
            )
        if "execution quality" in normalized:
            return VoiceIntentDTO(
                "execution_quality_query",
                {"symbol": symbol or "UNKNOWN", "timeframe": command.active_timeframe or "active"},
                0.92,
                ("timeframe_agent", "risk_agent", "ui_agent"),
                "medium",
                False,
            )
        return VoiceIntentDTO("unknown", {}, 0.0, (), "unknown", True)

    def routes(self, intent: VoiceIntentDTO) -> tuple[VoiceRouteDTO, ...]:
        """Return deterministic routes for an intent."""

        if intent.intent_name == "market_briefing":
            return (
                VoiceRouteDTO("ranking_agent", "summarize_market", {}, "normal", 1000),
                VoiceRouteDTO("alert_agent", "list_top_alerts", {}, "normal", 1000),
            )
        if intent.intent_name == "scanner_query":
            return (
                VoiceRouteDTO("ranking_agent", "scan_ranked_opportunities", intent.slots, "high", 1500),
            )
        if intent.intent_name == "voice_mute":
            return (VoiceRouteDTO("ui_agent", "set_voice_muted", intent.slots, "normal", 250),)
        if intent.intent_name == "voice_unmute":
            return (VoiceRouteDTO("ui_agent", "set_voice_muted", intent.slots, "normal", 250),)
        if intent.intent_name == "symbol_analysis":
            return (
                VoiceRouteDTO("timeframe_agent", "analyze_symbol", intent.slots, "high", 1500),
                VoiceRouteDTO("ui_agent", "focus_symbol", intent.slots, "normal", 500),
            )
        if intent.intent_name == "ui_navigation":
            return (VoiceRouteDTO("ui_agent", "navigate_panel", intent.slots, "normal", 250),)
        if intent.intent_name == "alert_explanation":
            return (VoiceRouteDTO("alert_agent", "explain_alert", intent.slots, "normal", 750),)
        if intent.intent_name == "execution_quality_query":
            return (VoiceRouteDTO("timeframe_agent", "query_execution_quality", intent.slots, "normal", 1000),)
        if intent.intent_name == "execution_command":
            return (VoiceRouteDTO("risk_agent", "evaluate_execution_request", intent.slots, "urgent", 1000),)
        return ()


def _extract_symbol(raw_text: str) -> str | None:
    match = re.search(r"\b([A-Z]{2,}(?:[A-Z0-9]+)?)\b", raw_text)
    if match is not None:
        return match.group(1)
    tokens = raw_text.strip().split()
    if len(tokens) >= 2 and tokens[0].lower() == "analyze":
        return tokens[1].strip(",.").upper()
    return None
