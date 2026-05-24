"""Phase-1 text-command assistant agent."""

from __future__ import annotations

from datetime import timedelta

from delta_os.application.agents.voice_intent_router import VoiceIntentRouter
from delta_os.application.agents.voice_response_composer import VoiceResponseComposer
from delta_os.application.dto.alerts import AlertDTO
from delta_os.application.dto.ui import DashboardStateDTO
from delta_os.application.dto.voice import VoiceAuditDTO, VoiceCommandDTO, VoiceIntentDTO, VoiceResponseDTO
from delta_os.domain.services.voice_safety_policy import VoiceSafetyPolicy


class VoiceAssistantAgent:
    """Deterministic Phase-1 text-command assistant."""

    def __init__(
        self,
        router: VoiceIntentRouter | None = None,
        composer: VoiceResponseComposer | None = None,
        safety_policy: VoiceSafetyPolicy | None = None,
        *,
        execution_commands_allowed: bool = False,
        stale_context_max_age: timedelta = timedelta(hours=6),
    ) -> None:
        self._router = router or VoiceIntentRouter()
        self._composer = composer or VoiceResponseComposer()
        self._safety_policy = safety_policy or VoiceSafetyPolicy()
        self._execution_commands_allowed = execution_commands_allowed
        self._stale_context_max_age = stale_context_max_age

    def run(
        self,
        command: VoiceCommandDTO,
        *,
        dashboard_state: DashboardStateDTO | None = None,
        alert: AlertDTO | None = None,
        risk_veto: bool = False,
    ) -> tuple[VoiceResponseDTO, VoiceAuditDTO]:
        """Process one deterministic text command."""

        intent = self._router.parse(command)
        routes = self._router.routes(intent)
        decision = self._safety_policy.evaluate(
            intent,
            execution_commands_allowed=self._execution_commands_allowed,
            risk_veto=risk_veto,
        )
        veto_state = decision.veto_state
        action_taken = routes[0].use_case if routes and decision.allowed else decision.reason

        stale_reason = None
        if decision.allowed:
            stale_reason = self._stale_or_unavailable_reason(
                intent,
                command=command,
                dashboard_state=dashboard_state,
                alert=alert,
            )

        if stale_reason is not None:
            response = VoiceResponseDTO(
                "Data is stale or unavailable. Please run a fresh scan.",
                "Data Unavailable",
                stale_reason,
                intent.confidence,
                (),
                ("Run offline scan", "Show market briefing"),
            )
            action_taken = "stale_data_guard"
            veto_state = "data_unavailable"
        else:
            response = self._composer.compose(
                intent,
                decision,
                dashboard_state=dashboard_state,
                alert=alert,
            )

        audit = VoiceAuditDTO(
            transcript=command.raw_text,
            parsed_intent=intent,
            action_taken=action_taken,
            veto_state=veto_state,
            latency_ms=0,
            error_state=None,
            timestamp=command.timestamp,
        )
        return response, audit

    def _stale_or_unavailable_reason(
        self,
        intent: VoiceIntentDTO,
        *,
        command: VoiceCommandDTO,
        dashboard_state: DashboardStateDTO | None,
        alert: AlertDTO | None,
    ) -> str | None:
        if intent.intent_name not in {
            "market_briefing",
            "scanner_query",
            "symbol_analysis",
            "alert_explanation",
            "execution_quality_query",
        }:
            return None

        if dashboard_state is None:
            return "dashboard_state=missing"

        market_status = next(
            (item.value for item in dashboard_state.status_items if item.label == "market_status"),
            "unknown",
        ).lower()
        if market_status in {"stale", "stale_data", "data_unavailable"}:
            return f"market_status={market_status}"

        if intent.intent_name == "scanner_query" and not dashboard_state.ranking_rows:
            return "ranking_rows=missing"
        if intent.intent_name in {"symbol_analysis", "execution_quality_query"} and not dashboard_state.timeframe_rows:
            return "timeframe_rows=missing"
        if intent.intent_name == "alert_explanation":
            if alert is None or not alert.message.strip():
                return "alert=missing"
            if command.timestamp - alert.created_at > self._stale_context_max_age:
                return "alert_age=stale"
        if intent.intent_name == "market_briefing" and alert is not None:
            if command.timestamp - alert.created_at > self._stale_context_max_age:
                return "alert_age=stale"

        return None
