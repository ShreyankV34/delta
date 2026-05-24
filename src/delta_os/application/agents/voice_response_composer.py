"""Grounded response composer for the Phase-1 voice/text assistant."""

from __future__ import annotations

from delta_os.application.dto.alerts import AlertDTO
from delta_os.application.dto.ui import DashboardStateDTO
from delta_os.application.dto.voice import VoiceIntentDTO, VoiceResponseDTO
from delta_os.domain.services.voice_safety_policy import VoiceSafetyDecision


class VoiceResponseComposer:
    """Compose short grounded replies from DTO state."""

    def compose(
        self,
        intent: VoiceIntentDTO,
        decision: VoiceSafetyDecision,
        *,
        dashboard_state: DashboardStateDTO | None = None,
        alert: AlertDTO | None = None,
    ) -> VoiceResponseDTO:
        """Compose a deterministic response DTO."""

        if not decision.allowed:
            title = "Clarification Needed" if decision.veto_state == "clarification_required" else "Voice Safety"
            body = decision.reason
            spoken = (
                "I need clarification before acting."
                if decision.veto_state == "clarification_required"
                else "I can't do that in Phase 1."
            )
            return VoiceResponseDTO(
                spoken,
                title,
                body,
                intent.confidence,
                (),
                ("Show market briefing", "Explain current alert"),
            )

        if intent.intent_name == "market_briefing":
            market_status = _status_value(dashboard_state, "market_status")
            headline = alert.message if alert is not None else "No active alert loaded."
            body = f"market_status={market_status}\nheadline={headline}"
            return VoiceResponseDTO(
                f"Market status is {market_status}. {headline}",
                "Market Briefing",
                body,
                intent.confidence,
                ("dashboard.status_items", "alert.message"),
                ("Show top compression setups", "Explain current alert"),
            )
        if intent.intent_name == "scanner_query":
            row_count = len(dashboard_state.ranking_rows) if dashboard_state is not None else 0
            body = f"scan_focus={intent.slots.get('scan_focus', 'general')}\nranking_rows={row_count}"
            return VoiceResponseDTO(
                f"I found {row_count} ranked opportunities in the current dashboard view.",
                "Scanner Query",
                body,
                intent.confidence,
                ("dashboard.ranking_rows",),
                ("Open ranking dashboard", "Analyze active symbol"),
            )
        if intent.intent_name == "voice_mute":
            return VoiceResponseDTO(
                "Voice responses are now muted. Text cards stay visible.",
                "Voice Controls",
                "muted=on",
                intent.confidence,
                ("dashboard.voice_status",),
                ("Unmute voice responses", "Show market briefing"),
            )
        if intent.intent_name == "voice_unmute":
            return VoiceResponseDTO(
                "Voice responses are now unmuted.",
                "Voice Controls",
                "muted=off",
                intent.confidence,
                ("dashboard.voice_status",),
                ("Show market briefing", "Analyze active symbol"),
            )
        if intent.intent_name == "symbol_analysis":
            symbol = intent.slots.get("symbol", dashboard_state.symbol if dashboard_state is not None else "UNKNOWN")
            timeframe = intent.slots.get("timeframe", "multi")
            body = f"symbol={symbol}\ntimeframe={timeframe}"
            return VoiceResponseDTO(
                f"Analyzing {symbol} across {timeframe} context.",
                "Symbol Analysis",
                body,
                intent.confidence,
                ("dashboard.timeframe_rows",),
                ("Explain current alert", "Open the risk panel"),
            )
        if intent.intent_name == "ui_navigation":
            panel = intent.slots.get("panel", "dashboard")
            return VoiceResponseDTO(
                f"Opening the {panel} panel.",
                "UI Navigation",
                f"panel={panel}",
                intent.confidence,
                ("dashboard.right_panel_sections",),
                ("Show market briefing", "Analyze active symbol"),
            )
        if intent.intent_name == "alert_explanation":
            headline = alert.message if alert is not None else "No alert is available."
            detail = alert.reasoning[0] if alert is not None and alert.reasoning else "No grounded explanation is available."
            return VoiceResponseDTO(
                f"{headline} {detail}",
                "Alert Explanation",
                f"headline={headline}\ndetail={detail}",
                intent.confidence,
                ("alert.message", "alert.reasoning"),
                ("Show risk panel", "Analyze active symbol"),
            )
        if intent.intent_name == "execution_quality_query":
            timeframe = intent.slots.get("timeframe", "active")
            return VoiceResponseDTO(
                f"Execution quality is tied to the {timeframe} summary row in the dashboard.",
                "Execution Quality",
                f"timeframe={timeframe}",
                intent.confidence,
                ("dashboard.timeframe_rows",),
                ("Show risk panel", "Explain current alert"),
            )
        return VoiceResponseDTO(
            "I couldn't map that request to a supported Phase-1 command.",
            "Unsupported Command",
            "unsupported_intent",
            0.0,
            (),
            ("Show market briefing",),
        )


def _status_value(state: DashboardStateDTO | None, label: str) -> str:
    if state is None:
        return "unknown"
    for item in state.status_items:
        if item.label == label:
            return item.value
    return "unknown"
