"""Universe Agent."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from delta_os.application.dto.universe import TradableUniverseDTO, UniverseMemberDTO
from delta_os.application.ports.universe_provider import UniverseProvider

VALID_SYMBOL = re.compile(r"^[A-Z0-9][A-Z0-9._-]*$")


class UniverseAgent:
    """Load and normalize local watchlist universes for offline Phase 1."""

    def __init__(self, provider: UniverseProvider) -> None:
        self._provider = provider

    def load(self, path: Path, universe_name: str) -> TradableUniverseDTO:
        """Load one universe from a local catalog file."""

        catalog = self._provider.load_catalog(path)
        universes = catalog.get("universes")
        if not isinstance(universes, dict):
            raise ValueError("Universe catalog must contain a 'universes' mapping")
        if universe_name not in universes:
            raise ValueError(f"Universe '{universe_name}' not found in catalog")

        raw_universe = universes[universe_name]
        if not isinstance(raw_universe, dict):
            raise ValueError(f"Universe '{universe_name}' must be a mapping")

        raw_members = raw_universe.get("symbols", ())
        if not isinstance(raw_members, list):
            raise ValueError(f"Universe '{universe_name}' symbols must be a list")

        sector = str(raw_universe.get("sector", "mixed"))
        theme = str(raw_universe.get("theme", "general"))
        members: list[UniverseMemberDTO] = []
        excluded: list[str] = []
        seen: set[str] = set()
        for raw_member in raw_members:
            normalized = _normalize_member(raw_member, universe_name, sector, theme)
            if normalized is None:
                excluded.append(str(raw_member))
                continue
            if normalized.symbol in seen:
                excluded.append(normalized.symbol)
                continue
            seen.add(normalized.symbol)
            members.append(normalized)

        included_symbols = tuple(member.symbol for member in members)
        reasoning = (
            f"loaded universe={universe_name}",
            f"included={len(included_symbols)}",
            f"excluded={len(excluded)}",
            "symbols are normalized, de-duplicated, and filtered for invalid local entries",
        )
        return TradableUniverseDTO(
            name=universe_name,
            source_path=path.as_posix(),
            members=tuple(members),
            total_members=len(members),
            included_symbols=included_symbols,
            excluded_symbols=tuple(excluded),
            reasoning=reasoning,
        )


def _normalize_member(
    raw_member: Any,
    universe_name: str,
    default_sector: str,
    default_theme: str,
) -> UniverseMemberDTO | None:
    if isinstance(raw_member, str):
        symbol = raw_member.strip().upper()
        display_name = symbol
        sector = default_sector
        theme = default_theme
    elif isinstance(raw_member, dict):
        raw_symbol = raw_member.get("symbol", "")
        symbol = str(raw_symbol).strip().upper()
        display_name = str(raw_member.get("display_name", symbol)).strip() or symbol
        sector = str(raw_member.get("sector", default_sector)).strip() or default_sector
        theme = str(raw_member.get("theme", default_theme)).strip() or default_theme
    else:
        return None

    if not symbol or not VALID_SYMBOL.fullmatch(symbol):
        return None
    return UniverseMemberDTO(
        symbol=symbol,
        display_name=display_name,
        sector=sector,
        theme=theme,
        source_universe=universe_name,
    )
