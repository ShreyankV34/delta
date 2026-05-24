"""Live session orchestrator use case."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from delta_os.application.dto.execution import (
    FillEventDTO,
    OrderAckDTO,
    OrderDecisionDTO,
    OrderIntentDTO,
    RejectEventDTO,
)
from delta_os.application.dto.live_market import BarUpdateDTO, MarketTickDTO, OrderBookDTO
from delta_os.application.dto.risk_events import ConnectivityEventDTO, KillSwitchEventDTO, RiskBreachEventDTO
from delta_os.application.ports.broker_execution_provider import BrokerExecutionProvider
from delta_os.application.ports.execution_risk_gate import ExecutionRiskGate
from delta_os.application.ports.market_data_provider import MarketDataStreamProvider


LiveMarketEvent = MarketTickDTO | OrderBookDTO | BarUpdateDTO
OrderLifecycleEvent = OrderAckDTO | FillEventDTO | RejectEventDTO
RiskRuntimeEvent = RiskBreachEventDTO | KillSwitchEventDTO


@dataclass(frozen=True, slots=True)
class LiveSessionConfig:
    mode: str
    provider: str
    broker: str
    live_armed: bool
    require_runtime_arming: bool
    kill_switch_enabled: bool
    heartbeat_max_age_ms: int
    max_events_per_poll: int = 100


@dataclass(frozen=True, slots=True)
class LiveSessionSnapshot:
    mode: str
    provider_health: str
    provider_detail: str
    market_events: tuple[LiveMarketEvent, ...]
    order_events: tuple[OrderLifecycleEvent, ...]
    risk_events: tuple[RiskRuntimeEvent, ...]
    connectivity_events: tuple[ConnectivityEventDTO, ...]
    last_updated_at: datetime


class LiveSessionOrchestrator:
    """Coordinate live market data, execution, and risk checks."""

    def __init__(
        self,
        market_data: MarketDataStreamProvider,
        broker: BrokerExecutionProvider,
        risk_gate: ExecutionRiskGate,
    ) -> None:
        self._market_data = market_data
        self._broker = broker
        self._risk_gate = risk_gate
        self._last_price_by_symbol: dict[str, float] = {}
        self._kill_switch_active = False

    def start(self, symbols: tuple[str, ...]) -> tuple[ConnectivityEventDTO, ...]:
        self._market_data.subscribe(symbols)
        events: list[ConnectivityEventDTO] = []
        now = datetime.now(tz=UTC)
        for symbol in symbols:
            snapshot = self._market_data.bootstrap_snapshot(symbol)
            tick = snapshot[0]
            self._last_price_by_symbol[symbol] = tick.last
            events.append(
                ConnectivityEventDTO(
                    component="market_data",
                    status="snapshot_ready",
                    detail=f"{symbol} bootstrap received",
                    timestamp=now,
                )
            )
        return tuple(events)

    def stop(self, symbols: tuple[str, ...]) -> ConnectivityEventDTO:
        self._market_data.unsubscribe(symbols)
        return ConnectivityEventDTO(
            component="market_data",
            status="stopped",
            detail="subscriptions removed",
            timestamp=datetime.now(tz=UTC),
        )

    def poll(self, config: LiveSessionConfig, daily_realized_pnl: float) -> LiveSessionSnapshot:
        health = self._market_data.health()
        market_events = self._market_data.poll_events(max_events=config.max_events_per_poll)
        for item in market_events:
            if isinstance(item, (MarketTickDTO,)):
                self._last_price_by_symbol[item.symbol] = item.last
            elif isinstance(item, OrderBookDTO):
                self._last_price_by_symbol[item.symbol] = (item.best_bid + item.best_ask) / 2.0
            elif isinstance(item, BarUpdateDTO):
                self._last_price_by_symbol[item.symbol] = item.close

        risk_events = list(
            self._risk_gate.evaluate_runtime(
                provider_health=health,
                daily_realized_pnl=daily_realized_pnl,
            )
        )
        if any(isinstance(item, KillSwitchEventDTO) and item.active for item in risk_events):
            self._kill_switch_active = True

        connectivity_events: list[ConnectivityEventDTO] = []
        if health.heartbeat_age_ms > config.heartbeat_max_age_ms:
            connectivity_events.append(
                ConnectivityEventDTO(
                    component="market_data",
                    status="degraded",
                    detail="heartbeat stale",
                    timestamp=health.timestamp,
                )
            )

        order_events = self._broker.poll_order_events(max_events=config.max_events_per_poll)
        return LiveSessionSnapshot(
            mode=config.mode,
            provider_health=health.status,
            provider_detail=health.detail,
            market_events=market_events,
            order_events=order_events,
            risk_events=tuple(risk_events),
            connectivity_events=tuple(connectivity_events),
            last_updated_at=datetime.now(tz=UTC),
        )

    def submit_order(
        self,
        config: LiveSessionConfig,
        intent: OrderIntentDTO,
    ) -> OrderDecisionDTO | OrderAckDTO | RejectEventDTO:
        now = datetime.now(tz=UTC)
        if self._kill_switch_active and config.kill_switch_enabled:
            return OrderDecisionDTO(
                allowed=False,
                reason="kill-switch active",
                veto_source="runtime_kill_switch",
                requires_confirmation=False,
                timestamp=now,
            )
        if config.mode == "live" and config.require_runtime_arming and not config.live_armed:
            return OrderDecisionDTO(
                allowed=False,
                reason="live mode is not armed",
                veto_source="arming_guard",
                requires_confirmation=False,
                timestamp=now,
            )

        health = self._market_data.health()
        decision = self._risk_gate.evaluate_order(
            intent,
            latest_price=self._last_price_by_symbol.get(intent.symbol),
            provider_health=health,
        )
        if not decision.allowed:
            return decision
        return self._broker.place_order(intent)

