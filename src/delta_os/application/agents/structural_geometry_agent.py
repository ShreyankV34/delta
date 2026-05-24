"""Structural Geometry Agent."""

from __future__ import annotations

from delta_os.application.dto.candles import CandleSeriesDTO
from delta_os.application.dto.structure import StructuralGeometryDTO
from delta_os.domain.services.structure_detector import StructureDetector, StructureScoringConfig
from delta_os.domain.services.swing_detector import SwingDetector


class StructuralGeometryAgent:
    """Detect swings, trendlines, wedge-like structures, and channels."""

    def __init__(
        self,
        swing_left: int = 2,
        swing_right: int = 2,
        compression_threshold: float = 0.85,
        channel_score_threshold: float = 0.70,
        expansion_threshold: float = 1.25,
        min_wedge_score: float = 0.55,
        min_mature_touch_count: int = 4,
    ) -> None:
        self._swing_detector = SwingDetector(swing_left, swing_right)
        scoring_config = StructureScoringConfig(
            compression_threshold=compression_threshold,
            channel_score_threshold=channel_score_threshold,
            expansion_threshold=expansion_threshold,
            min_wedge_score=min_wedge_score,
            min_mature_touch_count=min_mature_touch_count,
        )
        self._structure_detector = StructureDetector(scoring_config=scoring_config)

    def run(self, series: CandleSeriesDTO) -> StructuralGeometryDTO:
        """Return structural geometry DTO for a candle series."""

        entity = series.to_entity()
        swings = self._swing_detector.detect(entity)
        detection = self._structure_detector.detect(entity, swings)
        return StructuralGeometryDTO.from_detection(series.symbol, series.timeframe, swings, detection)
