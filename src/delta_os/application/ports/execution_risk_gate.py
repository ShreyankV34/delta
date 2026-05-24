"""Execution risk gate port."""

from __future__ import annotations

from typing import Protocol

from delta_os.application.dto.execution import OrderDecisionDTO, OrderIntentDTO
from delta_os.application.dto.live_market import ProviderHealthDTO
from delta_os.application.dto.risk_events import KillSwitchEventDTO, RiskBreachEventDTO


class ExecutionRiskGate(Protocol):
    """Port for hard-blocking pre-trade/runtime risk checks."""

    def evaluate_order(
        self,
        intent: OrderIntentDTO,
        *,
        latest_price: float | None,
        provider_health: ProviderHealthDTO,
    ) -> OrderDecisionDTO:
        """Return allow/reject decision for one order intent."""

    def evaluate_runtime(
        self,
        *,
        provider_health: ProviderHealthDTO,
        daily_realized_pnl: float,
    ) -> tuple[RiskBreachEventDTO | KillSwitchEventDTO, ...]:
        """Return runtime risk/kill-switch events."""

