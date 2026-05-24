"""Liquidity Concepts Agent."""

from __future__ import annotations

from delta_os.application.dto.candles import CandleSeriesDTO
from delta_os.application.dto.liquidity import LiquidityConceptsDTO, LiquidityEventDTO
from delta_os.application.dto.structure import StructuralGeometryDTO
from delta_os.domain.services.liquidity_concepts import LiquidityConceptDetector
from delta_os.domain.value_objects.swing import SwingKind, SwingPoint


class LiquidityConceptsAgent:
    """Detect FVGs, liquidity sweeps, BOS, and CHOCH events."""

    def __init__(self, sweep_lookback: int = 3) -> None:
        self._detector = LiquidityConceptDetector(sweep_lookback)

    def run(
        self,
        series: CandleSeriesDTO,
        structure: StructuralGeometryDTO,
    ) -> LiquidityConceptsDTO:
        """Return liquidity concept DTOs."""

        swings = tuple(
            SwingPoint(swing.index, swing.timestamp, swing.price, SwingKind(swing.kind))
            for swing in structure.swings
        )
        events = self._detector.detect(series.to_entity(), swings)
        event_dtos = tuple(LiquidityEventDTO.from_event(event) for event in events)
        reasoning = (
            f"detected {len(event_dtos)} phase-1 liquidity/structure events",
            "events are generated from candles and structural swing DTOs",
        )
        return LiquidityConceptsDTO(
            series.symbol,
            series.timeframe,
            event_dtos,
            len(event_dtos),
            reasoning,
        )
