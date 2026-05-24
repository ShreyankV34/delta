"""Voice/text-command DTOs for the Phase-1 assistant layer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from delta_os.application.dto.common import SerializableDTO
from delta_os.application.dto.ui import DashboardStateDTO


@dataclass(frozen=True, slots=True)
class VoiceCommandDTO(SerializableDTO):
    """Raw text or voice command normalized for deterministic processing."""

    raw_text: str
    audio_source: str
    timestamp: datetime
    user_context: tuple[str, ...]
    active_symbol: str | None
    active_timeframe: str | None


@dataclass(frozen=True, slots=True)
class VoiceIntentDTO(SerializableDTO):
    """Deterministic parsed intent."""

    intent_name: str
    slots: dict[str, str]
    confidence: float
    required_agents: tuple[str, ...]
    safety_level: str
    needs_confirmation: bool


@dataclass(frozen=True, slots=True)
class VoiceRouteDTO(SerializableDTO):
    """Route instruction for downstream application use cases or agents."""

    target_agent: str
    use_case: str
    payload: dict[str, str]
    priority: str
    timeout_ms: int


@dataclass(frozen=True, slots=True)
class VoiceResponseDTO(SerializableDTO):
    """Grounded voice/text response."""

    spoken_text: str
    display_title: str
    display_body: str
    confidence: float
    citations_to_agent_outputs: tuple[str, ...]
    follow_up_options: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class VoiceAuditDTO(SerializableDTO):
    """Audit record for one processed voice/text command."""

    transcript: str
    parsed_intent: VoiceIntentDTO
    action_taken: str
    veto_state: str
    latency_ms: int
    error_state: str | None
    timestamp: datetime


@dataclass(frozen=True, slots=True)
class VoiceCommandResultDTO(SerializableDTO):
    """Result of one processed voice/text command."""

    command: VoiceCommandDTO
    response: VoiceResponseDTO
    audit: VoiceAuditDTO
    context_symbol: str
    context_timeframe: str
    market_status: str
    dashboard: DashboardStateDTO
