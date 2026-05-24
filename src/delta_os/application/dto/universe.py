"""Tradable universe DTOs."""

from __future__ import annotations

from dataclasses import dataclass

from delta_os.application.dto.common import SerializableDTO


@dataclass(frozen=True, slots=True)
class UniverseMemberDTO(SerializableDTO):
    """One tradable universe member."""

    symbol: str
    display_name: str
    sector: str
    theme: str
    source_universe: str


@dataclass(frozen=True, slots=True)
class TradableUniverseDTO(SerializableDTO):
    """Universe Agent output."""

    name: str
    source_path: str
    members: tuple[UniverseMemberDTO, ...]
    total_members: int
    included_symbols: tuple[str, ...]
    excluded_symbols: tuple[str, ...]
    reasoning: tuple[str, ...]
