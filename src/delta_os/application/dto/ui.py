"""Presentation-only UI state DTOs."""

from __future__ import annotations

from dataclasses import dataclass

from delta_os.application.dto.common import SerializableDTO


@dataclass(frozen=True, slots=True)
class OverlayDTO(SerializableDTO):
    """Chart overlay description rendered by the UI."""

    overlay_type: str
    label: str
    points: tuple[tuple[float, float], ...]
    confidence: float


@dataclass(frozen=True, slots=True)
class SidebarSectionDTO(SerializableDTO):
    """Sidebar section rendered by the UI."""

    title: str
    items: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class StatusItemDTO(SerializableDTO):
    """Top status-bar item rendered by the UI."""

    label: str
    value: str


@dataclass(frozen=True, slots=True)
class PanelSectionDTO(SerializableDTO):
    """Right-panel section rendered by the UI."""

    title: str
    lines: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class VoiceStatusDTO(SerializableDTO):
    """Voice-assistant status rendered by the UI."""

    state: str
    mode: str
    muted: bool
    last_intent: str
    last_confidence: float
    last_veto_state: str


@dataclass(frozen=True, slots=True)
class VoiceTranscriptEntryDTO(SerializableDTO):
    """One voice transcript/audit row for UI rendering."""

    timestamp: str
    speaker: str
    text: str
    intent: str
    confidence: float
    action: str
    veto_state: str


@dataclass(frozen=True, slots=True)
class MultiTimeframeRowDTO(SerializableDTO):
    """Row for the multi-timeframe intelligence table."""

    timeframe: str
    bias: str
    structure: str
    liquidity: str
    volatility: str
    breakout_probability: float
    fakeout_risk: float
    execution_quality: str
    risk_state: str
    comment: str


@dataclass(frozen=True, slots=True)
class RankingRowDTO(SerializableDTO):
    """Row for the ranking table projection."""

    rank: int
    symbol: str
    timeframe: str
    score: float
    market_state: str
    breakout_probability: float
    fakeout_probability: float
    risk_state: str
    risk_veto: bool
    comment: str


@dataclass(frozen=True, slots=True)
class DashboardStateDTO(SerializableDTO):
    """GUI state for rendering only."""

    symbol: str
    status: str
    status_items: tuple[StatusItemDTO, ...]
    sidebar_sections: tuple[SidebarSectionDTO, ...]
    right_panel_sections: tuple[PanelSectionDTO, ...]
    voice_status: VoiceStatusDTO
    voice_transcript: tuple[VoiceTranscriptEntryDTO, ...]
    overlays: tuple[OverlayDTO, ...]
    timeframe_rows: tuple[MultiTimeframeRowDTO, ...]
    ranking_rows: tuple[RankingRowDTO, ...]
    alerts: tuple[str, ...]
    alert_timeline: tuple[str, ...]
    scanner_activity: tuple[str, ...]
    diagnostics: tuple[str, ...]
