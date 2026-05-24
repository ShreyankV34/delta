"""Trendline fitting service."""

from __future__ import annotations

from delta_os.domain.value_objects.swing import SwingPoint
from delta_os.domain.value_objects.trendline import Trendline


class TrendlineFitter:
    """Fit a least-squares linear trendline through swing points."""

    def fit(self, points: tuple[SwingPoint, ...]) -> Trendline | None:
        """Return a fitted trendline, or None when no points exist."""

        if not points:
            return None
        if len(points) == 1:
            return Trendline(0.0, points[0].price)

        count = float(len(points))
        sum_x = sum(point.index for point in points)
        sum_y = sum(point.price for point in points)
        sum_xx = sum(point.index * point.index for point in points)
        sum_xy = sum(point.index * point.price for point in points)
        denominator = count * sum_xx - sum_x * sum_x
        if denominator == 0:
            return Trendline(0.0, points[-1].price)
        slope = (count * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / count
        return Trendline(slope, intercept)
