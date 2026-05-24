"""Ranking Agent."""

from __future__ import annotations

from delta_os.application.dto.fusion import FusedMarketIntelligenceDTO
from delta_os.application.dto.probability import ProbabilityScoreDTO
from delta_os.application.dto.ranking import RankedOpportunityDTO
from delta_os.application.dto.risk import RiskAssessmentDTO
from delta_os.application.dto.structure import StructuralGeometryDTO
from delta_os.domain.services.probability_engine import ProbabilityScores
from delta_os.domain.services.ranking_engine import RankingEngine
from delta_os.domain.services.risk_engine import RiskAssessment
from delta_os.domain.services.structure_detector import StructureDetection, StructureKind
from delta_os.domain.value_objects.trendline import Trendline


class RankingAgent:
    """Rank market opportunities using DTO inputs."""

    def __init__(self) -> None:
        self._engine = RankingEngine()

    def run(
        self,
        structure: StructuralGeometryDTO,
        probability: ProbabilityScoreDTO,
        risk: RiskAssessmentDTO,
        fusion: FusedMarketIntelligenceDTO,
        rank: int = 1,
    ) -> RankedOpportunityDTO:
        """Return one ranked opportunity."""

        score = self._engine.score(
            _structure_from_dto(structure),
            _probability_from_dto(probability),
            _risk_from_dto(risk),
        )
        return RankedOpportunityDTO(
            rank,
            probability.symbol,
            probability.timeframe,
            score,
            fusion.market_state,
            probability.breakout_probability,
            probability.fakeout_probability,
            risk.risk_state,
            risk.veto,
            ("rank score combines structure, probability, fakeout risk, and risk veto",),
        )


def _structure_from_dto(dto: StructuralGeometryDTO) -> StructureDetection:
    return StructureDetection(
        StructureKind(dto.kind),
        _trendline(dto.upper_trendline),
        _trendline(dto.lower_trendline),
        dto.touch_count,
        dto.compression_ratio,
        dto.angular_difference,
        dto.wedge_score,
        dto.channel_score,
        dto.respect_score,
        dto.reasoning,
    )


def _trendline(dto: object) -> Trendline | None:
    if dto is None:
        return None
    return Trendline(getattr(dto, "slope"), getattr(dto, "intercept"))


def _probability_from_dto(dto: ProbabilityScoreDTO) -> ProbabilityScores:
    return ProbabilityScores(
        dto.breakout_probability,
        dto.fakeout_probability,
        dto.reversal_probability,
        dto.continuation_probability,
        dto.volatility_expansion_probability,
        dto.sweep_probability,
        dto.confidence_tier,
        dto.contributing_factors,
    )


def _risk_from_dto(dto: RiskAssessmentDTO) -> RiskAssessment:
    return RiskAssessment(dto.veto, dto.risk_state, dto.invalidation_level, dto.risk_reward, dto.notes)
