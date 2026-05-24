from __future__ import annotations

from datetime import UTC, datetime

from delta_os.application.dto.execution import OrderIntentDTO
from delta_os.application.dto.live_market import ProviderHealthDTO
from delta_os.application.dto.risk_events import KillSwitchEventDTO
from delta_os.infrastructure.risk import InstitutionalExecutionRiskGate
from delta_os.infrastructure.risk.institutional_execution_risk_gate import ExecutionRiskLimits


def _intent(quantity: float = 10.0, limit_price: float | None = 100.0) -> OrderIntentDTO:
    return OrderIntentDTO(
        client_order_id="cid-1",
        symbol="RELIANCE",
        asset_class="equity",
        side="buy",
        order_type="limit",
        quantity=quantity,
        limit_price=limit_price,
        stop_price=None,
        tif="day",
        strategy_tag="test",
        created_at=datetime.now(tz=UTC),
        metadata={},
    )


def _health(status: str = "ready") -> ProviderHealthDTO:
    return ProviderHealthDTO(
        provider="replay",
        status=status,
        detail="ok",
        heartbeat_age_ms=10,
        reconnect_attempt=0,
        timestamp=datetime.now(tz=UTC),
    )


def test_risk_gate_allows_small_order_with_healthy_data() -> None:
    gate = InstitutionalExecutionRiskGate()
    decision = gate.evaluate_order(_intent(), latest_price=100.0, provider_health=_health())
    assert decision.allowed is True


def test_risk_gate_rejects_provider_down() -> None:
    gate = InstitutionalExecutionRiskGate()
    decision = gate.evaluate_order(_intent(), latest_price=100.0, provider_health=_health("down"))
    assert decision.allowed is False
    assert decision.veto_source == "provider_health"


def test_risk_gate_rejects_over_notional_limit() -> None:
    gate = InstitutionalExecutionRiskGate(ExecutionRiskLimits(max_order_notional=1000.0))
    decision = gate.evaluate_order(_intent(quantity=50.0), latest_price=100.0, provider_health=_health())
    assert decision.allowed is False
    assert decision.veto_source == "max_order_notional"


def test_runtime_breach_emits_kill_switch() -> None:
    gate = InstitutionalExecutionRiskGate(ExecutionRiskLimits(max_daily_loss=100.0))
    events = gate.evaluate_runtime(provider_health=_health(), daily_realized_pnl=-250.0)
    assert any(isinstance(item, KillSwitchEventDTO) and item.active for item in events)

