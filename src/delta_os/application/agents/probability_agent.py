"""Probability Agent."""

from __future__ import annotations

from delta_os.application.dto.liquidity import LiquidityConceptsDTO
from delta_os.application.dto.probability import ProbabilityScoreDTO
from delta_os.application.dto.structure import StructuralGeometryDTO
from delta_os.domain.services.liquidity_concepts import LiquidityEvent
from delta_os.domain.services.probability_engine import BaselineProbabilityEngine
from delta_os.domain.services.structure_detector import StructureDetection, StructureKind
from delta_os.domain.value_objects.trendline import Trendline


class ProbabilityAgent:
    """Estimate baseline explainable probabilities."""

    def __init__(self, breakout_base: float = 0.35, fakeout_base: float = 0.25) -> None:
        self._engine = BaselineProbabilityEngine(breakout_base, fakeout_base)

    def run(
        self,
        structure: StructuralGeometryDTO,
        liquidity: LiquidityConceptsDTO,
    ) -> ProbabilityScoreDTO:
        """Return probability score DTO."""

        scores = self._engine.score(
            _structure_from_dto(structure),
            tuple(
                LiquidityEvent(
                    event.event_type,
                    event.index,
                    event.timestamp,
                    event.price,
                    event.direction,
                    event.confidence,
                    event.reason,
                )
                for event in liquidity.events
            ),
        )
        return ProbabilityScoreDTO.from_scores(structure.symbol, structure.timeframe, scores)


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
    slope = getattr(dto, "slope")
    intercept = getattr(dto, "intercept")
    return Trendline(slope, intercept)
