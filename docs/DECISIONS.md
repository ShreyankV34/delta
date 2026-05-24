# DELTA OS Decisions

## ADR-0001: Phase 1 Uses Live Market Ingestion (Opt-in Execution)

Phase 1 uses live market-data ingestion as the primary data path (configured
per `configs/app.yaml`). Offline CSV fixtures and deterministic replay remain
available for testing and validation, but CSV and toy/demo-only flows are no
longer considered primary. Broker execution and other high-risk execution
paths remain gated behind explicit sandbox configs and a Risk & Safety gate.

## ADR-0002: DTOs Define Agent Boundaries

Application agents accept and return immutable DTOs. Domain services remain
framework-free and do not depend on infrastructure or presentation code.

## ADR-0003: UI Is Rendering-Only

The PySide6 dashboard skeleton renders `DashboardStateDTO` and related DTOs. It
does not compute market intelligence, scores, trendlines, or alerts.

## ADR-0004: Core Package Has No Mandatory Heavy Runtime Dependencies

The Phase-1 testable core uses the Python standard library. GUI dependencies are
optional through the `gui` extra, and YAML loading can use PyYAML when available
with a minimal fallback for the checked-in example configs.

## ADR-0005: Risk Veto Is Preserved in Fusion

Risk Agent veto state is carried into fused intelligence and ranking. Fusion
must not override or discard a veto.

## ADR-0006: Structural Classification Thresholds Are Explicit

Baseline structural geometry classification uses `StructureScoringConfig` for
compression, channel score, expansion, wedge score, and wedge maturity
thresholds. The defaults are calibrated against deterministic Phase-1 CSV
fixtures and remain configurable through the Structural Geometry Agent.

## ADR-0007: Checked-In YAML Profiles Have Explicit Loader Validation

The checked-in Phase-1 YAML files are validated at config-load time according to
their filename-specific shape. This keeps schema validation close to the config
boundary, preserves lightweight offline operation, and avoids leaking config
rules into UI or unrelated domain services.

## ADR-0008: Offline Scan Logging Lives At The Orchestration Boundary

Offline scan lifecycle and failure logs are emitted from the scan use case
rather than presentation code. This keeps failure context close to agent
orchestration, preserves deterministic testing with `caplog`, and avoids UI
ownership of pipeline errors.

## ADR-0009: Deterministic Replay Uses Explicit Alert Timestamps

Replay determinism for offline scans is achieved by making alert timestamp
generation injectable and config-aware. In deterministic mode, the config
supplies a fixed alert timestamp so repeated runs can be compared across the
full serialized scan result.

## ADR-0010: Universe Loading Is Local And File-Based In Phase 1

The Universe Agent loads watchlists from local YAML catalog files, normalizes
symbols, and filters invalid or duplicate entries deterministically. This keeps
scanner context offline-first and compatible with the roadmap's later universe
and sector expansion work.

## ADR-0011: Multi-Timeframe Summaries Are Built In The Application Layer

The scanner builds one `TimeframeIntelligenceDTO` per available timeframe from
the existing structural, liquidity, probability, risk, and fusion DTOs.
Higher-timeframe ordering and alignment labels are handled in the application
agent layer, while the UI continues to render summary rows only. This preserves
the roadmap's Timeframe Agent direction without pushing intelligence logic into
presentation code.

## ADR-0012: Alert Explainability Is Verified At The Agent Boundary

Alert confidence, reasoning composition, and risk-note propagation are verified
through direct Alert Agent tests at the application boundary. This keeps
explainability guarantees close to the DTO-producing logic and avoids relying on
CLI or UI formatting tests to prove alert semantics.

## ADR-0013: CLI Snapshot Fixtures Anchor The Offline Command Surface

Deterministic fixture files now pin the serialized offline scan output, ranking
payload, and universe CLI output. This keeps Phase-1 command behavior stable
across refactors while leaving intelligence logic inside agents and DTOs rather
than moving it into CLI-only formatting layers.

## ADR-0014: Dashboard Bottom-Panel State Is Explicitly DTO-Projected

Alert timeline entries, scanner activity lines, diagnostics, and ranking-table
rows are now explicit dashboard-state fields produced from application DTOs.
This keeps the PySide6 shell rendering-only while giving the bottom and side
surfaces stable, testable contracts.

## ADR-0015: Scan Profile Selection Is An Explicit CLI Choice

The scan command now accepts `--profile` and `--scan-profiles` for deterministic
profile-driven runs. The checked-in app config can name a default profile for
project context, but CLI profile selection remains explicit so the base scan
snapshot stays stable unless the caller opts into a profile variant.

## ADR-0016: Sidebar And Status Surfaces Are Explicit Presentation DTOs

Watchlists, scan profiles, trade-profile labels, and top status-bar values are
now explicit presentation DTOs rather than hardcoded widget strings. This keeps
the dashboard shell rendering-only while making the sidebar/status surface
fixture-backed and deterministic.

## ADR-0017: Profile And Watchlist Summaries Have Dedicated CLI Snapshots

Trade-profile summaries, risk-profile summaries, and watchlist-oriented universe
summaries are snapshot-tested through deterministic CLI or use-case projections.
This keeps configuration and watchlist context inspectable without adding live
dependencies or UI-side parsing logic.

## ADR-0018: Sidebar Universe And Filter Labels Are Built From Local Config

Universe-selection labels, filter labels, and profile-summary sidebar strings
are projected from checked-in local config/catalog data rather than hardcoded in
widgets. This keeps the left sidebar deterministic, offline-first, and aligned
with the roadmap's watchlist/universe/filter surfaces.

## ADR-0019: Status-Bar Health And Latency Stay Deterministic In Phase 1

Provider health and scan latency labels are exposed as deterministic presentation
state in Phase 1 instead of measuring real live latency or provider heartbeat.
This keeps status-bar coverage stable while the product remains offline-first.

## ADR-0020: Right-Panel Intelligence Surfaces Are Explicit Presentation DTOs

The DELTA intelligence summary, probability panel, risk panel, and execution-
quality panel are represented as explicit `PanelSectionDTO` values in dashboard
state and serialized scan output. This keeps the right panel rendering-only,
fixture-backed, and stable across presentation refactors.

## ADR-0021: Ranking And Bottom-Panel Rendering Use Explicit Helper Contracts

Multi-row ranking tables and grouped bottom-panel content are now rendered
through small presentation helpers over DTO state instead of ad hoc widget
string assembly. This keeps the dashboard shell rendering-only while making the
ranking and diagnostics surfaces deterministic and fixture-backed.

## ADR-0022: Phase-1 Voice Starts As Deterministic Text Commands

The Phase-1 voice assistant enters through deterministic text-command parsing,
grounded response composition, and explicit safety policy enforcement. It does
not depend on live microphone capture or broker execution, and every response
must remain traceable to existing dashboard or alert DTO state.

## ADR-0023: Voice Transcript/Status Are Explicit Dashboard DTO Surfaces

Voice interaction status and transcript rows are represented as explicit
dashboard DTO fields and fixture-backed rendering helpers. This keeps transcript
and state presentation deterministic while preserving the rendering-only UI
boundary.

## ADR-0024: Phase-1 Voice Infrastructure Uses Local Deterministic Placeholders

Speech-to-text, text-to-speech, and push-to-talk infrastructure are introduced
as minimal deterministic adapters/stubs in Phase 1. This preserves offline
operation and testability while preparing extension points for future local or
cloud voice backends.

## ADR-0025: Voice Interaction State Is Updated In Application Use Cases

Voice command results are projected into dashboard `voice_status` and
`voice_transcript` fields via a dedicated application-layer updater instead of
UI-side logic. The updater enforces deterministic state transitions
(`listening`, `processing`, `responding`, `error`), bounded transcript history,
and CLI-safe mute/unmute handling while preserving immutable DTO boundaries.

## ADR-0026: Voice Queries Must Return Explicit Stale/Unavailable Responses

When voice intents require scan context but critical DTO fields are missing or
context age is stale, the voice assistant returns an explicit
"data unavailable/stale" response and audit veto state. This keeps voice output
grounded in actual system state and enforces the roadmap requirement that voice
must never invent market facts when data is unavailable.

## ADR-0027: CLI Keeps JSON Contract But Supports Terminal Operator View

The CLI default output remains deterministic JSON for snapshots and automation.
An explicit `--output terminal` mode is added for operator-facing readability.
This preserves stable machine contracts while providing a professional terminal
experience for manual runs.

## ADR-0028: Repo Uses A Segregated Roadmap Operator Skill

A dedicated repo-local skill (`.codex/skills/delta-os-roadmap-operator`) is
maintained to enforce DELTA-specific startup behavior: mandatory roadmap/docs
reads, `docs/TASKS.md`-driven sequencing, Phase-1 boundaries, deterministic
test execution, and memory-doc updates. This reduces prompt overhead and
improves continuation consistency across sessions.

## ADR-0029: Voice Audit History Uses A Dedicated Projection Helper

Compact voice audit-history rows for terminal summaries are produced through a
dedicated projection helper over `VoiceCommandResultDTO` transcript data. This
keeps rendering concerns separate from core DTO serialization while preserving
the default JSON output contract for fixtures and automation.

## ADR-0030: Online Market Data Is Added As A Provider, Not A Pipeline Fork

By explicit user override, DELTA OS now supports a real online data-ingestion
mode through a dedicated `YahooFinanceCandleProvider`. The existing scan
pipeline (`DataAgent` -> use case -> DTO chain -> rendering-only UI) is reused
unchanged. Provider selection is config/CLI-driven (`csv` or
`yahoo_finance`), and tests keep determinism by mocking transport at the
infrastructure boundary.

Execution systems remain excluded: this decision adds market-data ingestion
only and does not add broker routing, live order execution, or WebSocket
streaming.

## ADR-0031: Provider Failures Return Deterministic CLI Error Contracts

When scan context cannot be loaded from a selected data provider (for example,
online timeout/remote load failure), CLI commands now return deterministic JSON
error payloads instead of uncaught tracebacks. `scan` and `voice` use explicit
error contracts with `status=error`, provider metadata, and typed error fields,
while terminal output gets a concise operator-facing error summary.

This keeps failures testable and automation-friendly without moving fallback
reasoning into UI code or bypassing application boundaries.

## ADR-0032: Live Runtime Uses Port-Based Session Orchestration

Live runtime flow is implemented through explicit ports:
`MarketDataStreamProvider`, `BrokerExecutionProvider`, and
`ExecutionRiskGate`, coordinated by `LiveSessionOrchestrator`.
This preserves Clean Architecture boundaries while allowing broker/data
adapters to evolve independently.

Institutional safety is enforced fail-closed through the risk gate
(provider-down, stale-price, notional/slippage breaches, daily loss kill-switch),
and execution remains governed by explicit mode/arming controls.
