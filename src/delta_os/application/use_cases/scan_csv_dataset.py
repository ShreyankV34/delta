"""Market scanner use case."""

from __future__ import annotations

import logging
from pathlib import Path

from delta_os.application.agents.alert_agent import AlertAgent
from delta_os.application.agents.data_agent import DataAgent
from delta_os.application.agents.fusion_agent import FusionAgent
from delta_os.application.agents.liquidity_concepts_agent import LiquidityConceptsAgent
from delta_os.application.agents.probability_agent import ProbabilityAgent
from delta_os.application.agents.ranking_agent import RankingAgent
from delta_os.application.agents.risk_agent import RiskAgent
from delta_os.application.agents.structural_geometry_agent import StructuralGeometryAgent
from delta_os.application.agents.timeframe_intelligence_agent import TimeframeIntelligenceAgent
from delta_os.application.agents.ui_agent import UiAgent
from delta_os.application.dto.candles import CandleSeriesDTO
from delta_os.application.dto.fusion import FusedMarketIntelligenceDTO
from delta_os.application.dto.liquidity import LiquidityConceptsDTO
from delta_os.application.dto.probability import ProbabilityScoreDTO
from delta_os.application.dto.risk import RiskAssessmentDTO
from delta_os.application.dto.scan import ScanResultDTO
from delta_os.application.dto.structure import StructuralGeometryDTO

LOGGER = logging.getLogger(__name__)


class ScanCsvDatasetUseCase:
    """Run a deterministic scan over one configured market data source."""

    def __init__(
        self,
        data_agent: DataAgent,
        structural_agent: StructuralGeometryAgent,
        liquidity_agent: LiquidityConceptsAgent,
        probability_agent: ProbabilityAgent,
        risk_agent: RiskAgent,
        fusion_agent: FusionAgent,
        ranking_agent: RankingAgent,
        alert_agent: AlertAgent,
        timeframe_agent: TimeframeIntelligenceAgent,
        ui_agent: UiAgent,
    ) -> None:
        self._data_agent = data_agent
        self._structural_agent = structural_agent
        self._liquidity_agent = liquidity_agent
        self._probability_agent = probability_agent
        self._risk_agent = risk_agent
        self._fusion_agent = fusion_agent
        self._ranking_agent = ranking_agent
        self._alert_agent = alert_agent
        self._timeframe_agent = timeframe_agent
        self._ui_agent = ui_agent

    def run(
        self,
        csv_path: Path | None,
        symbol: str | None,
        target_timeframes: tuple[str, ...],
        analysis_timeframe: str | None = None,
    ) -> ScanResultDTO:
        """Run the pipeline and return DTO outputs."""

        LOGGER.info(
            "starting market scan",
            extra={
                "data_source_path": str(csv_path) if csv_path is not None else "REMOTE",
                "symbol": symbol or "ALL",
                "analysis_timeframe": analysis_timeframe or "source",
                "target_timeframes": ",".join(target_timeframes),
            },
        )
        try:
            candles = self._data_agent.load(csv_path, symbol, target_timeframes)
            selected_timeframe = analysis_timeframe or candles.source_timeframe
            selected_series: CandleSeriesDTO | None = None
            structure: StructuralGeometryDTO | None = None
            liquidity: LiquidityConceptsDTO | None = None
            probability: ProbabilityScoreDTO | None = None
            risk: RiskAssessmentDTO | None = None
            fusion: FusedMarketIntelligenceDTO | None = None
            timeframe_summaries = []

            for series in candles.series:
                structure_item = self._structural_agent.run(series)
                liquidity_item = self._liquidity_agent.run(series, structure_item)
                probability_item = self._probability_agent.run(structure_item, liquidity_item)
                risk_item = self._risk_agent.run(series, structure_item, probability_item)
                fusion_item = self._fusion_agent.run(probability_item, risk_item)
                timeframe_summaries.append(
                    self._timeframe_agent.run(
                        structure_item,
                        liquidity_item,
                        probability_item,
                        risk_item,
                        fusion_item,
                    )
                )
                if series.timeframe == selected_timeframe:
                    selected_series = series
                    structure = structure_item
                    liquidity = liquidity_item
                    probability = probability_item
                    risk = risk_item
                    fusion = fusion_item

            if selected_series is None or structure is None or liquidity is None:
                raise KeyError(f"Analysis timeframe not found: {selected_timeframe}")
            if probability is None or risk is None or fusion is None:
                raise RuntimeError("Selected timeframe analysis is incomplete")

            aligned_timeframes = self._timeframe_agent.align(tuple(timeframe_summaries))
            ranking = self._ranking_agent.run(structure, probability, risk, fusion)
            alert = self._alert_agent.run(structure, liquidity, probability, risk, fusion)
            scanner_activity = (
                f"scan_symbol={candles.symbol}",
                f"analysis_timeframe={selected_timeframe}",
                f"target_timeframes={','.join(item.timeframe for item in aligned_timeframes)}",
                f"liquidity_events={liquidity.event_count}",
                f"ranking_score={ranking.score:.3f}",
            )
            if self._data_agent.last_provider_health != "ready":
                scanner_activity = (
                    *scanner_activity,
                    f"provider_health={self._data_agent.last_provider_health}",
                    f"provider_note={self._data_agent.last_provider_note}",
                )
            dashboard = self._ui_agent.run(
                structure,
                alert,
                aligned_timeframes,
                ranking,
                probability,
                risk,
                fusion,
                scanner_activity,
                provider_health=self._data_agent.last_provider_health,
                provider_note=self._data_agent.last_provider_note,
            )
            result = ScanResultDTO(
                candles,
                structure,
                liquidity,
                probability,
                risk,
                fusion,
                ranking,
                alert,
                aligned_timeframes,
                dashboard,
            )
        except Exception:
            LOGGER.exception(
                "market scan failed",
                extra={
                    "data_source_path": str(csv_path) if csv_path is not None else "REMOTE",
                    "symbol": symbol or "ALL",
                    "analysis_timeframe": analysis_timeframe or "source",
                    "target_timeframes": ",".join(target_timeframes),
                },
            )
            raise

        LOGGER.info(
            "market scan completed",
            extra={
                "symbol": result.candles.symbol,
                "analysis_timeframe": result.structure.timeframe,
                "market_state": result.fusion.market_state,
                "risk_veto": str(result.risk.veto),
            },
        )
        return result
