"""Risk Agent."""

from __future__ import annotations

from delta_os.application.dto.candles import CandleSeriesDTO
from delta_os.application.dto.probability import ProbabilityScoreDTO
from delta_os.application.dto.risk import RiskAssessmentDTO
from delta_os.application.dto.structure import StructuralGeometryDTO
from delta_os.domain.services.probability_engine import ProbabilityScores
from delta_os.domain.services.risk_engine import BaselineRiskEngine
from delta_os.domain.services.structure_detector import StructureDetection, StructureKind
from delta_os.domain.value_objects.trendline import Trendline


class RiskAgent:
    """Evaluate invalidation, risk/reward, and veto state."""

    def __init__(
        self,
        max_fakeout_probability: float = 0.7,
        min_breakout_probability: float = 0.25,
    ) -> None:
        self._engine = BaselineRiskEngine(max_fakeout_probability, min_breakout_probability)

    def run(
        self,
        series: CandleSeriesDTO,
        structure: StructuralGeometryDTO,
        probability: ProbabilityScoreDTO,
    ) -> RiskAssessmentDTO:
        """Return risk assessment DTO."""

        assessment = self._engine.assess(
            series.to_entity(),
            _structure_from_dto(structure),
            _probability_from_dto(probability),
        )
        return RiskAssessmentDTO.from_assessment(series.symbol, series.timeframe, assessment)


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
