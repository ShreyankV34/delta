"""Swing point value objects."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SwingKind(str, Enum):
    """Supported swing point kinds."""

    HIGH = "high"
    LOW = "low"


@dataclass(frozen=True, slots=True)
class SwingPoint:
    """A detected local high or low."""

    index: int
    timestamp: datetime
    price: float
    kind: SwingKind
