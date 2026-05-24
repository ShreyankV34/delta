"""Offline scan use-case DTO."""

from __future__ import annotations

from dataclasses import dataclass

from delta_os.application.dto.alerts import AlertDTO
from delta_os.application.dto.candles import TimeframeCandleBundleDTO
from delta_os.application.dto.fusion import FusedMarketIntelligenceDTO
from delta_os.application.dto.liquidity import LiquidityConceptsDTO
from delta_os.application.dto.probability import ProbabilityScoreDTO
from delta_os.application.dto.ranking import RankedOpportunityDTO
from delta_os.application.dto.risk import RiskAssessmentDTO
from delta_os.application.dto.structure import StructuralGeometryDTO
from delta_os.application.dto.timeframe_intelligence import TimeframeIntelligenceDTO
from delta_os.application.dto.ui import DashboardStateDTO
from delta_os.application.dto.common import SerializableDTO


@dataclass(frozen=True, slots=True)
class ScanResultDTO(SerializableDTO):
    """Result of one offline CSV scan."""

    candles: TimeframeCandleBundleDTO
    structure: StructuralGeometryDTO
    liquidity: LiquidityConceptsDTO
    probability: ProbabilityScoreDTO
    risk: RiskAssessmentDTO
    fusion: FusedMarketIntelligenceDTO
    ranking: RankedOpportunityDTO
    alert: AlertDTO
    timeframe_intelligence: tuple[TimeframeIntelligenceDTO, ...]
    dashboard: DashboardStateDTO
