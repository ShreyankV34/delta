Live Integration Spec (Phase-2)

Goal
----
Move the project from offline/replay CSV mode to a realistic, gated live-market integration while preserving deterministic testing and offline replay. Implement live data ingestion (streaming + REST), broker execution adapters (sandbox first), and a safety/risk layer.

Scope
-----
- Add live-data ingestion adapters (WebSocket primary, REST fallback).
- Add broker/execution adapter interface with a `SandboxBrokerAdapter` implementation.
- Keep existing CSV and polling providers as fallbacks and for deterministic replay.
- Provide config schema for providers and broker credentials using env secrets.
- Add Risk & Safety checks (pre-trade veto, kill-switch, throttles, audit logs).
- Add deterministic integration tests via mocked transports and a replay harness.

Constraints and Safety
----------------------
- Live execution must be opt-in via `mode: live` and explicit config flags.
- Sandbox mode must be the default for any execution adapter in the repo.
- Secrets must never be committed. Support environment variables or OS secret stores.
- All execution requests must pass a Risk & Safety gate that can veto or throttle orders.

High-level Architecture Changes
------------------------------
- New interfaces (Python ABCs) in `src/delta_os/application/ports`:
  - `LiveCandleProvider` (streaming API)
  - `BrokerAdapter` (place_order, cancel_order, order_status)
- New infrastructure adapters in `src/delta_os/infrastructure`:
  - `data/websocket_provider.py` (WS + reconnection/backpressure)
  - `broker/sandbox_adapter.py` (standalone, no real money)
  - optionally `broker/<provider>_adapter.py` for real brokers
- DataAgent update: support streaming updates, sequence numbers, provider health
- Replay harness: deterministic replay of streaming events into existing agent pipelines

Config Schema (example)
------------------------
```yaml
mode: live # live | replay | offline_csv
data:
  provider: websocket_nse
  websocket_nse:
    url: wss://example-feed
    symbol_subscribe: [NSE:RELIANCE]
    auth_env: NSE_WS_API_KEY
  rest_fallback:
    base_url: https://api.example.com
    api_key_env: EXAMPLE_API_KEY
broker:
  adapter: sandbox
  sandbox: {}
  zerodha:
    api_key_env: ZERODHA_API_KEY
    secret_env: ZERODHA_SECRET
safety:
  max_order_size: 100
  enabled: true
```

Interfaces (sketch)
-------------------
class LiveCandleProvider(ABC):
    def subscribe(self, symbols: Iterable[str]) -> None: ...
    def poll_snapshot(self, symbol: str, timeframe: str) -> list[Candle]: ...
    def stop(self) -> None: ...

class BrokerAdapter(ABC):
    def place_order(self, order: OrderDTO) -> OrderResponseDTO: ...
    def cancel_order(self, order_id: str) -> bool: ...
    def get_order_status(self, order_id: str) -> OrderStatusDTO: ...

Risk & Safety
-------------
- Implement a `RiskManager` with these capabilities:
  - `pre_trade_check(order) -> bool|VetoReason`
  - global kill-switch (boolean flag persisted)
  - rate limiting and per-symbol throttles
  - audit log for every order and veto decision

Testing and Determinism
-----------------------
- Provide a `MockWebSocketTransport` and `MockBroker` for integration tests.
- Add deterministic replay tests that play recorded streaming payloads into the DataAgent and assert DTO outputs equal offline fixtures.
- Keep existing CSV-based tests undisturbed.

Milestones & Acceptance Criteria
--------------------------------
1. Spec + config schema added. (Docs + example config) — Accept: `docs/LIVE_INTEGRATION_SPEC.md` exists.
2. Provider and broker interfaces added + sandbox broker implementation. — Accept: unit tests for interfaces and sandbox pass.
3. WebSocket provider scaffolding + REST fallback. — Accept: can run a sandbox stream locally and ingest events into DataAgent.
4. Risk & Safety layer wired into BrokerAdapter. — Accept: orders are vetoed when rules trigger in tests.
5. UI updates: live toggle + provider status visible. — Accept: UI projects `provider_health` and `mode` in status items.
6. Integration tests and replay harness. — Accept: recorded stream replays produce identical DTO output to fixture.

Next Steps (recommended order)
-----------------------------
1. Review and sign off this spec.
2. Add config schema changes to `configs/app.yaml` and validation.
3. Scaffold interfaces and a `SandboxBrokerAdapter`.
4. Implement `websocket_provider.py` with reconnection/backpressure.
5. Add risk manager and wire to sandbox broker.
6. Add tests, mock transports, and replay harness.
7. Update UI and docs, then run CI.

Implementation Notes
--------------------
- Keep the Clean Architecture boundary: adapters live in `infrastructure/`, ports (ABCs) in `application/ports`, domain and agents unchanged.
- Gate live behavior behind `mode: live` and explicit `enable_execution: true` flags.
- Favor a simple, well-tested sandbox first before wiring any real broker.

Files to create/modify
-----------------------
- Add: `src/delta_os/application/ports/live_data_provider.py`
- Add: `src/delta_os/application/ports/broker_adapter.py`
- Add: `src/delta_os/infrastructure/data/websocket_provider.py`
- Add: `src/delta_os/infrastructure/broker/sandbox_adapter.py`
- Update: `configs/app.yaml`, `docs/TASKS.md`, `docs/PROJECT_CONTEXT.md`

Contact & Rollout
------------------
Start with an internal feature branch and iterative PRs: spec → interfaces → sandbox → WS provider → tests → UI.

---
Generated by the roadmap audit; next action: scaffold interfaces/adapters on approval.
