from __future__ import annotations

from datetime import UTC, datetime

from delta_os.application.dto.execution import OrderIntentDTO
from delta_os.application.dto.live_market import MarketTickDTO
from delta_os.application.use_cases.run_live_session import LiveSessionConfig, LiveSessionOrchestrator
from delta_os.infrastructure.execution import IbkrReferenceBrokerAdapter
from delta_os.infrastructure.live import ReplayMarketDataProvider
from delta_os.infrastructure.risk import InstitutionalExecutionRiskGate


def _tick(symbol: str, sequence: int, last: float) -> MarketTickDTO:
    return MarketTickDTO(
        symbol=symbol,
        timestamp=datetime.now(tz=UTC),
        bid=last - 0.2,
        ask=last + 0.2,
        last=last,
        size=100.0,
        sequence=sequence,
        venue="NSE",
    )


def _intent() -> OrderIntentDTO:
    return OrderIntentDTO(
        client_order_id="cid-live-1",
        symbol="RELIANCE",
        asset_class="equity",
        side="buy",
        order_type="limit",
        quantity=2.0,
        limit_price=101.0,
        stop_price=None,
        tif="day",
        strategy_tag="live_test",
        created_at=datetime.now(tz=UTC),
        metadata={},
    )


def _config(mode: str = "paper", live_armed: bool = False) -> LiveSessionConfig:
    return LiveSessionConfig(
        mode=mode,
        provider="replay",
        broker="ibkr",
        live_armed=live_armed,
        require_runtime_arming=True,
        kill_switch_enabled=True,
        heartbeat_max_age_ms=5000,
    )


def test_live_orchestrator_polls_market_events() -> None:
    provider = ReplayMarketDataProvider(
        provider_name="replay",
        bootstrap_by_symbol={"RELIANCE": (_tick("RELIANCE", 1, 100.0), None)},
        events=(_tick("RELIANCE", 2, 101.0),),
    )
    orchestrator = LiveSessionOrchestrator(
        market_data=provider,
        broker=IbkrReferenceBrokerAdapter(mode="paper"),
        risk_gate=InstitutionalExecutionRiskGate(),
    )
    orchestrator.start(("RELIANCE",))
    snapshot = orchestrator.poll(_config(), daily_realized_pnl=0.0)

    assert snapshot.provider_health in {"ready", "degraded"}
    assert snapshot.market_events


def test_live_orchestrator_blocks_live_submit_when_not_armed() -> None:
    provider = ReplayMarketDataProvider(
        provider_name="replay",
        bootstrap_by_symbol={"RELIANCE": (_tick("RELIANCE", 1, 100.0), None)},
        events=(),
    )
    orchestrator = LiveSessionOrchestrator(
        market_data=provider,
        broker=IbkrReferenceBrokerAdapter(mode="live"),
        risk_gate=InstitutionalExecutionRiskGate(),
    )
    orchestrator.start(("RELIANCE",))
    decision_or_ack = orchestrator.submit_order(_config(mode="live", live_armed=False), _intent())
    assert hasattr(decision_or_ack, "to_dict")
    assert decision_or_ack.to_dict().get("allowed") is False

