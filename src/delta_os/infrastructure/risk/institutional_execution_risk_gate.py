"""Institutional execution risk gate."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from delta_os.application.dto.execution import OrderDecisionDTO, OrderIntentDTO
from delta_os.application.dto.live_market import ProviderHealthDTO
from delta_os.application.dto.risk_events import KillSwitchEventDTO, RiskBreachEventDTO
from delta_os.application.ports.execution_risk_gate import ExecutionRiskGate


@dataclass(frozen=True, slots=True)
class ExecutionRiskLimits:
    max_order_notional: float = 1_000_000.0
    max_position_notional: float = 5_000_000.0
    max_daily_loss: float = 250_000.0
    max_slippage_bps: float = 50.0
    max_spread_bps: float = 35.0
    allow_out_of_hours: bool = False
    kill_switch_enabled: bool = True


class InstitutionalExecutionRiskGate(ExecutionRiskGate):
    """Hard-blocking risk gate for live execution."""

    def __init__(self, limits: ExecutionRiskLimits | None = None) -> None:
        self._limits = limits or ExecutionRiskLimits()
        self._kill_switch_active = False

    def evaluate_order(
        self,
        intent: OrderIntentDTO,
        *,
        latest_price: float | None,
        provider_health: ProviderHealthDTO,
    ) -> OrderDecisionDTO:
        now = datetime.now(tz=UTC)
        if self._kill_switch_active and self._limits.kill_switch_enabled:
            return OrderDecisionDTO(False, "kill-switch active", "kill_switch", False, now)
        if provider_health.status == "down":
            return OrderDecisionDTO(False, "provider is down", "provider_health", False, now)
        if latest_price is None or latest_price <= 0:
            return OrderDecisionDTO(False, "stale or unavailable price", "stale_price_guard", False, now)
        if intent.quantity <= 0:
            return OrderDecisionDTO(False, "quantity must be positive", "order_validation", False, now)

        notional = latest_price * intent.quantity
        if notional > self._limits.max_order_notional:
            return OrderDecisionDTO(False, "order notional exceeds limit", "max_order_notional", False, now)
        if intent.limit_price is not None and intent.limit_price > 0:
            slippage_bps = abs(intent.limit_price - latest_price) / latest_price * 10_000.0
            if slippage_bps > self._limits.max_slippage_bps:
                return OrderDecisionDTO(False, "slippage guard breached", "slippage_guard", False, now)
        return OrderDecisionDTO(True, "approved", "risk_gate", False, now)

    def evaluate_runtime(
        self,
        *,
        provider_health: ProviderHealthDTO,
        daily_realized_pnl: float,
    ) -> tuple[RiskBreachEventDTO | KillSwitchEventDTO, ...]:
        events: list[RiskBreachEventDTO | KillSwitchEventDTO] = []
        now = datetime.now(tz=UTC)
        if provider_health.status == "down":
            events.append(
                RiskBreachEventDTO(
                    breach_type="provider_down",
                    severity="critical",
                    message="market data provider is down",
                    symbol=None,
                    timestamp=now,
                )
            )
            if self._limits.kill_switch_enabled:
                self._kill_switch_active = True
                events.append(
                    KillSwitchEventDTO(
                        trigger="provider_down",
                        active=True,
                        reason="provider down fail-closed",
                        timestamp=now,
                    )
                )
        if daily_realized_pnl <= -abs(self._limits.max_daily_loss):
            events.append(
                RiskBreachEventDTO(
                    breach_type="daily_loss_limit",
                    severity="critical",
                    message="daily loss limit breached",
                    symbol=None,
                    timestamp=now,
                )
            )
            if self._limits.kill_switch_enabled:
                self._kill_switch_active = True
                events.append(
                    KillSwitchEventDTO(
                        trigger="daily_loss_limit",
                        active=True,
                        reason="daily loss limit fail-closed",
                        timestamp=now,
                    )
                )
        return tuple(events)

