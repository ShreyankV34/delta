"""Process one deterministic Phase-1 voice/text command."""

from __future__ import annotations

from delta_os.application.agents.voice_assistant_agent import VoiceAssistantAgent
from delta_os.application.dto.scan import ScanResultDTO
from delta_os.application.dto.voice import VoiceCommandDTO, VoiceCommandResultDTO
from delta_os.application.use_cases.voice_interaction_state_updater import (
    VoiceInteractionStateUpdater,
)


class ProcessVoiceCommandUseCase:
    """Run the Phase-1 voice/text assistant against grounded scan state."""

    def __init__(
        self,
        voice_agent: VoiceAssistantAgent,
        state_updater: VoiceInteractionStateUpdater | None = None,
    ) -> None:
        self._voice_agent = voice_agent
        self._state_updater = state_updater or VoiceInteractionStateUpdater()

    def run(self, command: VoiceCommandDTO, context: ScanResultDTO) -> VoiceCommandResultDTO:
        """Return a grounded response and audit record for one command."""

        dashboard = self._state_updater.processing(self._state_updater.listening(context.dashboard))
        response, audit = self._voice_agent.run(
            command,
            dashboard_state=dashboard,
            alert=context.alert,
            risk_veto=context.risk.veto,
        )
        market_status = next(
            (item.value for item in dashboard.status_items if item.label == "market_status"),
            "unknown",
        )
        result = VoiceCommandResultDTO(
            command=command,
            response=response,
            audit=audit,
            context_symbol=context.candles.symbol,
            context_timeframe=context.structure.timeframe,
            market_status=market_status,
            dashboard=dashboard,
        )
        if audit.error_state is not None:
            return VoiceCommandResultDTO(
                command=result.command,
                response=result.response,
                audit=result.audit,
                context_symbol=result.context_symbol,
                context_timeframe=result.context_timeframe,
                market_status=result.market_status,
                dashboard=self._state_updater.error(result.dashboard),
            )
        return self._state_updater.apply(result)
