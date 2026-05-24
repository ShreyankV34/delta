"""Structural geometry detection."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import atan

from delta_os.domain.entities.candle import CandleSeries
from delta_os.domain.services.trendline_fitter import TrendlineFitter
from delta_os.domain.value_objects.swing import SwingKind, SwingPoint
from delta_os.domain.value_objects.trendline import Trendline


class StructureKind(str, Enum):
    """Supported structural geometry classifications."""

    INSUFFICIENT_DATA = "insufficient_data"
    WEDGE_LIKE = "wedge_like"
    CHANNEL_LIKE = "channel_like"
    COMPRESSING = "compressing"
    EXPANDING = "expanding"
    UNSTABLE = "unstable"


@dataclass(frozen=True, slots=True)
class StructureScoringConfig:
    """Configurable structural classification thresholds."""

    compression_threshold: float = 0.85
    channel_score_threshold: float = 0.70
    expansion_threshold: float = 1.25
    min_wedge_score: float = 0.55
    min_mature_touch_count: int = 4

    def __post_init__(self) -> None:
        if not 0.0 < self.compression_threshold < 1.0:
            raise ValueError("compression_threshold must be between 0 and 1")
        if not 0.0 <= self.channel_score_threshold <= 1.0:
            raise ValueError("channel_score_threshold must be between 0 and 1")
        if self.expansion_threshold <= 1.0:
            raise ValueError("expansion_threshold must be greater than 1")
        if not 0.0 <= self.min_wedge_score <= 1.0:
            raise ValueError("min_wedge_score must be between 0 and 1")
        if self.min_mature_touch_count < 2:
            raise ValueError("min_mature_touch_count must be at least 2")


@dataclass(frozen=True, slots=True)
class StructureDetection:
    """Detected structural geometry summary."""

    kind: StructureKind
    upper_trendline: Trendline | None
    lower_trendline: Trendline | None
    touch_count: int
    compression_ratio: float
    angular_difference: float
    wedge_score: float
    channel_score: float
    respect_score: float
    reasoning: tuple[str, ...]


class StructureDetector:
    """Detect baseline wedge/channel geometry from swing points."""

    def __init__(
        self,
        compression_threshold: float = 0.85,
        scoring_config: StructureScoringConfig | None = None,
    ) -> None:
        if scoring_config is None:
            scoring_config = StructureScoringConfig(compression_threshold=compression_threshold)
        self._scoring_config = scoring_config
        self._fitter = TrendlineFitter()

    def detect(
        self,
        series: CandleSeries,
        swings: tuple[SwingPoint, ...],
    ) -> StructureDetection:
        """Return a deterministic structural geometry summary."""

        if len(series.candles) < 3:
            return StructureDetection(
                StructureKind.INSUFFICIENT_DATA,
                None,
                None,
                0,
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                ("not enough candles for structural geometry",),
            )

        upper_points = tuple(point for point in swings if point.kind == SwingKind.HIGH)
        lower_points = tuple(point for point in swings if point.kind == SwingKind.LOW)
        upper_points = upper_points if len(upper_points) >= 2 else self._fallback_points(series, True)
        lower_points = lower_points if len(lower_points) >= 2 else self._fallback_points(series, False)

        upper = self._fitter.fit(upper_points)
        lower = self._fitter.fit(lower_points)
        if upper is None or lower is None:
            return StructureDetection(
                StructureKind.INSUFFICIENT_DATA,
                upper,
                lower,
                len(swings),
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                ("not enough swing points for upper and lower boundaries",),
            )

        start_index = 0
        end_index = len(series.candles) - 1
        start_distance = max(upper.value_at(start_index) - lower.value_at(start_index), 0.000001)
        end_distance = max(upper.value_at(end_index) - lower.value_at(end_index), 0.000001)
        compression_ratio = end_distance / start_distance
        angular_difference = abs(atan(upper.slope) - atan(lower.slope))
        touch_count = len(upper_points) + len(lower_points)
        respect_score = self._respect_score(series, upper, lower)

        channel_score = _clamp(1.0 - abs(compression_ratio - 1.0) - angular_difference)
        compression_strength = _clamp(1.0 - compression_ratio)
        wedge_score = _clamp(
            0.25 * min(touch_count / 4.0, 1.0)
            + 0.35 * compression_strength
            + 0.25 * respect_score
            + 0.15 * (1.0 - min(angular_difference, 1.0))
        )

        if self._is_mature_wedge(compression_ratio, wedge_score, touch_count):
            kind = StructureKind.WEDGE_LIKE
        elif channel_score >= self._scoring_config.channel_score_threshold:
            kind = StructureKind.CHANNEL_LIKE
        elif compression_ratio < 1.0:
            kind = StructureKind.COMPRESSING
        elif compression_ratio > self._scoring_config.expansion_threshold:
            kind = StructureKind.EXPANDING
        else:
            kind = StructureKind.UNSTABLE

        reasoning = (
            f"touch_count={touch_count}",
            f"compression_ratio={compression_ratio:.3f}",
            f"angular_difference={angular_difference:.3f}",
            f"respect_score={respect_score:.3f}",
            f"wedge_score={wedge_score:.3f}",
            f"channel_score={channel_score:.3f}",
            f"compression_threshold={self._scoring_config.compression_threshold:.3f}",
            f"channel_score_threshold={self._scoring_config.channel_score_threshold:.3f}",
        )
        return StructureDetection(
            kind,
            upper,
            lower,
            touch_count,
            compression_ratio,
            angular_difference,
            wedge_score,
            channel_score,
            respect_score,
            reasoning,
        )

    def _fallback_points(self, series: CandleSeries, high: bool) -> tuple[SwingPoint, ...]:
        candles = series.candles
        middle = max(1, len(candles) // 2)
        first_slice = candles[:middle]
        second_slice = candles[middle:]
        if not second_slice:
            second_slice = candles[-1:]

        def choose(offset: int, items: tuple[object, ...]) -> SwingPoint:
            if high:
                relative, candle = max(
                    enumerate(items),
                    key=lambda pair: pair[1].high,  # type: ignore[attr-defined]
                )
                return SwingPoint(offset + relative, candle.timestamp, candle.high, SwingKind.HIGH)
            relative, candle = min(
                enumerate(items),
                key=lambda pair: pair[1].low,  # type: ignore[attr-defined]
            )
            return SwingPoint(offset + relative, candle.timestamp, candle.low, SwingKind.LOW)

        return (choose(0, first_slice), choose(middle, second_slice))

    def _respect_score(self, series: CandleSeries, upper: Trendline, lower: Trendline) -> float:
        if not series.candles:
            return 0.0
        total_range = max(
            max(candle.high for candle in series.candles)
            - min(candle.low for candle in series.candles),
            0.000001,
        )
        distances = []
        for index, candle in enumerate(series.candles):
            upper_distance = abs(upper.value_at(index) - candle.high) / total_range
            lower_distance = abs(candle.low - lower.value_at(index)) / total_range
            distances.append(min(upper_distance, lower_distance))
        average_distance = sum(distances) / len(distances)
        return _clamp(1.0 - average_distance)

    def _is_mature_wedge(
        self,
        compression_ratio: float,
        wedge_score: float,
        touch_count: int,
    ) -> bool:
        return (
            compression_ratio < self._scoring_config.compression_threshold
            and wedge_score >= self._scoring_config.min_wedge_score
            and touch_count >= self._scoring_config.min_mature_touch_count
        )


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
