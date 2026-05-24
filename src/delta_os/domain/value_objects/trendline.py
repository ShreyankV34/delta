"""Trendline value object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Trendline:
    """Linear trendline represented as y = slope * x + intercept."""

    slope: float
    intercept: float

    def value_at(self, index: int | float) -> float:
        """Return trendline value at index."""

        return self.slope * float(index) + self.intercept

    @classmethod
    def from_points(
        cls,
        first_index: int,
        first_price: float,
        second_index: int,
        second_price: float,
    ) -> "Trendline":
        """Build a line through two points."""

        if first_index == second_index:
            return cls(0.0, first_price)
        slope = (second_price - first_price) / (second_index - first_index)
        intercept = first_price - slope * first_index
        return cls(slope, intercept)
