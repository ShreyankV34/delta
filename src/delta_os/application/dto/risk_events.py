"""Risk and kill-switch event DTO contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from delta_os.application.dto.common import SerializableDTO


@dataclass(frozen=True, slots=True)
class RiskBreachEventDTO(SerializableDTO):
    breach_type: str
    severity: str
    message: str
    symbol: str | None
    timestamp: datetime


@dataclass(frozen=True, slots=True)
class KillSwitchEventDTO(SerializableDTO):
    trigger: str
    active: bool
    reason: str
    timestamp: datetime


@dataclass(frozen=True, slots=True)
class ConnectivityEventDTO(SerializableDTO):
    component: str
    status: str
    detail: str
    timestamp: datetime

