"""UI Agent."""

from __future__ import annotations

from collections.abc import Sequence

from delta_os.application.dto.alerts import AlertDTO
from delta_os.application.dto.fusion import FusedMarketIntelligenceDTO
from delta_os.application.dto.probability import ProbabilityScoreDTO
from delta_os.application.dto.ranking import RankedOpportunityDTO
from delta_os.application.dto.risk import RiskAssessmentDTO
from delta_os.application.dto.structure import StructuralGeometryDTO, TrendlineDTO
from delta_os.application.dto.timeframe_intelligence import TimeframeIntelligenceDTO
from delta_os.application.dto.ui import (
    DashboardStateDTO,
    MultiTimeframeRowDTO,
    OverlayDTO,
    PanelSectionDTO,
    RankingRowDTO,
    SidebarSectionDTO,
    StatusItemDTO,
    VoiceStatusDTO,
)


class UiAgent:
    """Prepare GUI state from agent DTOs without computing intelligence."""

    def __init__(
        self,
        sidebar_sections: Sequence[SidebarSectionDTO] | None = None,
        app_mode: str = "offline_csv",
        data_provider: str = "csv",
        provider_health: str = "ready",
        provider_profile_summary: str | None = None,
    ) -> None:
        self._sidebar_sections = tuple(sidebar_sections) if sidebar_sections is not None else _default_sidebar_sections()
        self._app_mode = app_mode
        self._data_provider = data_provider
        self._provider_health = provider_health
        self._provider_profile_summary = provider_profile_summary or "default"

    def run(
        self,
        structure: StructuralGeometryDTO,
        alert: AlertDTO,
        timeframe_intelligence: tuple[TimeframeIntelligenceDTO, ...],
        ranking: RankedOpportunityDTO,
        probability: ProbabilityScoreDTO,
        risk: RiskAssessmentDTO,
        fusion: FusedMarketIntelligenceDTO,
        scanner_activity: tuple[str, ...],
        provider_health: str | None = None,
        provider_note: str | None = None,
    ) -> DashboardStateDTO:
        """Return presentation-only dashboard state."""

        overlays = tuple(
            overlay
            for overlay in (
                _trendline_overlay("upper_trendline", structure.upper_trendline, structure),
                _trendline_overlay("lower_trendline", structure.lower_trendline, structure),
            )
            if overlay is not None
        )
        rows = tuple(
            MultiTimeframeRowDTO(
                timeframe=item.timeframe,
                bias=item.bias,
                structure=item.structure_state,
                liquidity=item.liquidity_state,
                volatility=item.volatility_regime,
                breakout_probability=item.breakout_probability,
                fakeout_risk=item.fakeout_probability,
                execution_quality=item.execution_quality,
                risk_state=item.risk_state,
                comment=item.comment,
            )
            for item in timeframe_intelligence
        )
        ranking_rows = (
            RankingRowDTO(
                rank=ranking.rank,
                symbol=ranking.symbol,
                timeframe=ranking.timeframe,
                score=ranking.score,
                market_state=ranking.market_state,
                breakout_probability=ranking.breakout_probability,
                fakeout_probability=ranking.fakeout_probability,
                risk_state=ranking.risk_state,
                risk_veto=ranking.risk_veto,
                comment=ranking.reasoning[0] if ranking.reasoning else ranking.market_state,
            ),
        )
        alert_timeline = (
            alert.message,
            f"type={alert.alert_type} confidence={alert.confidence:.2f}",
            *tuple(f"risk_note={note}" for note in alert.risk_notes),
        )
        resolved_provider_health = provider_health or self._provider_health
        status_label = _dashboard_status_label(self._data_provider, resolved_provider_health)
        status_items = (
            StatusItemDTO("market_status", fusion_label(timeframe_intelligence)),
            StatusItemDTO("data_provider", self._data_provider),
            StatusItemDTO("provider_health", resolved_provider_health),
            StatusItemDTO("scan_latency", _scan_latency_label(scanner_activity)),
            StatusItemDTO("alert_engine", alert.alert_type),
            StatusItemDTO("risk_mode", ranking.risk_state),
            StatusItemDTO("app_mode", self._app_mode),
        )
        right_panel_sections = _right_panel_sections(
            structure,
            timeframe_intelligence,
            probability,
            risk,
            fusion,
            ranking,
        )
        diagnostics = [
            "dashboard state generated from DTOs only",
            "multi-timeframe table sourced from DTOs",
            "ranking table sourced from DTOs",
            "alert timeline sourced from DTOs",
        ]
        if self._provider_profile_summary != "default":
            diagnostics.append(f"provider_profile={self._provider_profile_summary}")

        return DashboardStateDTO(
            structure.symbol,
            status_label,
            status_items,
            self._sidebar_sections,
            right_panel_sections,
            VoiceStatusDTO(
                state="idle",
                mode="text_stub",
                muted=False,
                last_intent="none",
                last_confidence=0.0,
                last_veto_state="clear",
            ),
            (),
            overlays,
            rows,
            ranking_rows,
            (alert.message,),
            alert_timeline,
            scanner_activity,
            tuple(diagnostics),
        )


def _trendline_overlay(
    label: str,
    trendline: TrendlineDTO | None,
    structure: StructuralGeometryDTO,
) -> OverlayDTO | None:
    if trendline is None:
        return None
    end_index = max((swing.index for swing in structure.swings), default=1)
    return OverlayDTO(
        "trendline",
        label,
        (
            (0.0, trendline.intercept),
            (float(end_index), trendline.slope * end_index + trendline.intercept),
        ),
        structure.respect_score,
    )


def _default_sidebar_sections() -> tuple[SidebarSectionDTO, ...]:
    return (
        SidebarSectionDTO("Watchlists", ("nifty_50", "fno_stocks", "custom_watchlist")),
        SidebarSectionDTO(
            "Universe Selection",
            ("NIFTY 50 | mixed | 5", "F&O Stocks | derivatives | 4", "Custom Watchlist | mixed | 4"),
        ),
        SidebarSectionDTO(
            "Filters",
            ("default_universe=nifty_50", "timeframes=1m,5m,15m,1h,4h,1d", "scan_profiles=3", "risk_profiles=2"),
        ),
        SidebarSectionDTO(
            "Scan Profiles",
            (
                "compression_scanner [1d,4h,1h]",
                "breakout_probability [4h,1h,15m]",
                "fakeout_detection [1d,4h,1h]",
            ),
        ),
        SidebarSectionDTO(
            "Trade Profiles",
            (
                "swing | ctx 1M/1W | exec 1h/15m",
                "intraday | ctx 1d/4h | exec 5m",
                "position | ctx 1M/1W | exec 4h/1h",
            ),
        ),
        SidebarSectionDTO(
            "Risk Profiles",
            ("normal | fakeout<=0.70 | veto=on", "conservative | fakeout<=0.55 | veto=on"),
        ),
    )


def fusion_label(timeframe_intelligence: tuple[TimeframeIntelligenceDTO, ...]) -> str:
    if not timeframe_intelligence:
        return "idle"
    return timeframe_intelligence[-1].market_regime


def _scan_latency_label(scanner_activity: tuple[str, ...]) -> str:
    if not scanner_activity:
        return "idle"
    return "deterministic_offline"


def _dashboard_status_label(data_provider: str, provider_health: str) -> str:
    if data_provider == "csv" and provider_health == "ready":
        return "CSV MODE ACTIVE"
    if provider_health == "down":
        return f"{data_provider.upper()} DOWN"
    if provider_health == "degraded":
        return f"{data_provider.upper()} DEGRADED"
    return f"{data_provider.upper()} READY"


def _right_panel_sections(
    structure: StructuralGeometryDTO,
    timeframe_intelligence: tuple[TimeframeIntelligenceDTO, ...],
    probability: ProbabilityScoreDTO,
    risk: RiskAssessmentDTO,
    fusion: FusedMarketIntelligenceDTO,
    ranking: RankedOpportunityDTO,
) -> tuple[PanelSectionDTO, ...]:
    execution_quality = timeframe_intelligence[-1].execution_quality if timeframe_intelligence else "wait"
    alignment = timeframe_intelligence[-1].htf_alignment if timeframe_intelligence else "lead_context"
    return (
        PanelSectionDTO(
            "DELTA Intelligence Summary",
            (
                f"structure={structure.kind}",
                f"market_state={fusion.market_state}",
                f"alignment={alignment}",
                f"ranking_score={ranking.score:.2f}",
            ),
        ),
        PanelSectionDTO(
            "Probability Panel",
            (
                f"breakout={probability.breakout_probability:.2f}",
                f"fakeout={probability.fakeout_probability:.2f}",
                f"reversal={probability.reversal_probability:.2f}",
                f"continuation={probability.continuation_probability:.2f}",
            ),
        ),
        PanelSectionDTO(
            "Risk Panel",
            (
                f"risk_state={risk.risk_state}",
                f"veto={'on' if risk.veto else 'off'}",
                f"invalidation={_format_optional_number(risk.invalidation_level)}",
                f"risk_reward={_format_optional_number(risk.risk_reward)}",
            ),
        ),
        PanelSectionDTO(
            "Execution Quality Panel",
            (
                f"execution_quality={execution_quality}",
                f"alert_state={fusion.market_state}",
                f"structure_confidence={structure.respect_score:.2f}",
                f"execution_mode={alignment}",
            ),
        ),
    )


def _format_optional_number(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}"
