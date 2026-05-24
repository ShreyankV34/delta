"""Structural geometry DTOs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from delta_os.application.dto.common import SerializableDTO
from delta_os.domain.services.structure_detector import StructureDetection
from delta_os.domain.value_objects.swing import SwingPoint
from delta_os.domain.value_objects.trendline import Trendline


@dataclass(frozen=True, slots=True)
class SwingPointDTO(SerializableDTO):
    """Serializable swing point."""

    index: int
    timestamp: datetime
    price: float
    kind: str

    @classmethod
    def from_value(cls, swing: SwingPoint) -> "SwingPointDTO":
        return cls(swing.index, swing.timestamp, swing.price, swing.kind.value)


@dataclass(frozen=True, slots=True)
class TrendlineDTO(SerializableDTO):
    """Serializable trendline."""

    slope: float
    intercept: float

    @classmethod
    def from_value(cls, trendline: Trendline | None) -> "TrendlineDTO | None":
        if trendline is None:
            return None
        return cls(trendline.slope, trendline.intercept)

    def to_value(self) -> Trendline:
        return Trendline(self.slope, self.intercept)


@dataclass(frozen=True, slots=True)
class StructuralGeometryDTO(SerializableDTO):
    """Structural Geometry Agent output."""

    symbol: str
    timeframe: str
    swings: tuple[SwingPointDTO, ...]
    kind: str
    upper_trendline: TrendlineDTO | None
    lower_trendline: TrendlineDTO | None
    touch_count: int
    compression_ratio: float
    angular_difference: float
    wedge_score: float
    channel_score: float
    respect_score: float
    reasoning: tuple[str, ...]

    @classmethod
    def from_detection(
        cls,
        symbol: str,
        timeframe: str,
        swings: tuple[SwingPoint, ...],
        detection: StructureDetection,
    ) -> "StructuralGeometryDTO":
        return cls(
            symbol,
            timeframe,
            tuple(SwingPointDTO.from_value(swing) for swing in swings),
            detection.kind.value,
            TrendlineDTO.from_value(detection.upper_trendline),
            TrendlineDTO.from_value(detection.lower_trendline),
            detection.touch_count,
            detection.compression_ratio,
            detection.angular_difference,
            detection.wedge_score,
            detection.channel_score,
            detection.respect_score,
            detection.reasoning,
        )
