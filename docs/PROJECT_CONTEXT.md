# DELTA OS Project Context

## Source of Truth

`roadmap_docx.docx` is the technical source of truth. `readme.md` is the public
project overview.

## Delivery Boundary

The repository now follows live-market integration as the primary roadmap path.
Deterministic replay fixtures remain for testability and regression control.
Live execution capabilities must remain safety-gated through explicit risk and
kill-switch controls.

Included in this repository initialization:

- Clean Architecture package scaffold under `src/delta_os`
- Domain entities, value objects, and deterministic services
-- Live and polling candle providers (e.g. `yahoo_finance`) and timeframe builder
- Swing detection, trendline fitting, wedge/channel detection
- FVG, liquidity sweep, BOS, and CHOCH event detection
- Baseline probability, risk, ranking, fusion, and alert agents
- Presentation-only PySide6 dashboard skeleton
  - Example YAML configs and recorded fixture data for deterministic replay
- Pytest unit/integration tests and GitHub Actions CI

Current stage emphasis:

- Live data providers and stream-ready ingestion contracts
- Execution adapter interfaces and reference broker scaffolding
- Institutional risk/safety gating and auditability
- Replay determinism and CI-safe integration testing

## Architectural Rules

- Domain intelligence lives outside the UI.
- Agents communicate through DTOs and immutable event-style outputs.
- The Risk Agent can veto a setup.
- The Fusion Agent cannot bypass a Risk Agent veto.
- DTOs are serializable and deterministic in tests.
- Config files define symbols, timeframes, scoring thresholds, and risk gates.

## Current Status

Milestone 1 scaffold is complete. The repository contains the Phase-1 package
scaffold, config files, docs, sample CSV data, pytest coverage, and CI workflow.
Workflow memory has been hardened with root-level `AGENTS.md`,
`docs/CODEX_WORKFLOW.md`, and a richer `docs/TASKS.md` board so future Codex
runs can continue from the active task with minimal prompting.

Milestone 2 is complete. Deterministic structural geometry fixtures now cover
noisy wedges, channel-like structures, false-breakout sweeps, and imperfect
trendline respect. Baseline structural classification thresholds are explicit
through `StructureScoringConfig`, and fixture-backed tests cover stricter channel
and wedge maturity settings.

Milestone 3 is complete. Presentation DTO fixture coverage now includes a richer
dashboard-state fixture with multiple overlays and timeframe rows, plus pure
render helpers that prove the GUI consumes DTO state without computing domain
intelligence.

Milestone 4 is complete. YAML config schema validation now covers the checked-in
Phase-1 profile files at the config-loading boundary, and invalid app/profile/
voice shapes are rejected deterministically.

Milestone 5 is complete. Repository-level logging now covers offline scan
lifecycle and failure handling, including deterministic tests for successful
scan logging and bad-CSV failure context.

Milestone 6 is complete. Offline scanner replay coverage now proves identical
serialized DTO output across repeated runs, including the config-driven scan
path through deterministic alert timestamps.

Milestone 7 is complete. The Universe Agent now loads local watchlist catalogs,
normalizes symbols, filters invalid or duplicate entries deterministically, and
supports a file-based CLI/use-case path for offline scanner context.

Milestone 8 is complete. The offline scanner now builds ordered
`TimeframeIntelligenceDTO` summaries across available timeframes and passes them
to the UI as rendering-only dashboard rows. This mirrors the roadmap's
Timeframe Agent family in a Phase-1-safe, deterministic form without adding
live execution or UI-side intelligence logic.

Milestone 9 is complete. Alert explainability coverage now pins down the
Alert Agent's deterministic branch selection, confidence values, reasoning
composition, and risk-note propagation across veto, breakout, liquidity-event,
and monitor scenarios.

Milestone 10 is complete. The offline command surface now has fixture-backed
coverage for full scan JSON output, the ranking payload, and the local universe
CLI output. This locks deterministic serialized behavior around the scanner's
multi-timeframe summary path and ranking block.

Milestone 11 is complete. The dashboard state and CLI surface now have explicit
fixture-backed coverage for scanner activity lines, alert-timeline summaries,
ranking-table projection, and profile-driven scan variants. The scan command can
now optionally select a named scan profile without pushing intelligence into the
CLI layer.

Milestone 12 is complete. The dashboard state now carries explicit sidebar and
top-status DTO projections, and the CLI surface now has deterministic summary
fixtures for trade profiles, risk profiles, and watchlist-oriented universe
views. The GUI shell remains rendering-only while these presentation surfaces
become stable contracts.

Milestone 13 is complete. The dashboard now carries explicit universe-selection
and filter sidebar labels, richer top-status labels for provider health and
scan latency, and profile-summary style sidebar projections. The CLI surface
also now snapshot-tests a non-custom universe output path.

Milestone 14 is complete. Right-panel summary, probability, risk, and
execution-quality presentation surfaces are now fixture-backed through explicit
`PanelSectionDTO` coverage in both UI fixtures and scan output snapshots.

Milestone 15 is complete. The dashboard fixture state now covers multi-row
ranking tables, grouped bottom-panel rendering, scan-profile override/fallback
CLI summaries, and contributor installation guidance through `requirements.txt`.

Milestone 16 is complete. The repository now includes a deterministic Phase-1
text-command voice assistant scaffold with voice DTOs, intent parsing, safety
policy, response composition, a grounded voice use case, CLI snapshot coverage,
dashboard transcript/status DTO fixture coverage, right-panel voice response
card coverage, blocked-execution and alert-explanation snapshots, and local
TTS/push-to-talk placeholders without microphone dependency.

Milestone 17 is complete. Voice interaction-state projection now maps
`VoiceCommandResultDTO` outputs into dashboard `voice_status` and
`voice_transcript` fields through a deterministic application-layer updater.
The updater now also enforces bounded transcript history, explicit state
transitions between listening, processing, responding, and error, and
CLI-safe mute/unmute command paths.

Milestone 18 has started. Voice query handling now includes a deterministic
stale-data guard that returns explicit "data unavailable/stale" responses when
required context is missing or alert context age exceeds the Phase-1 guard.
Voice terminal summaries now also include a compact audit-history section
through a dedicated projection helper, keeping audit readability separate from
the raw JSON contract.

By user override, a professional presentation polish pass is also complete:
the PySide6 shell now uses a denser desk-style panel hierarchy/theme and the
CLI supports an optional terminal summary output mode via `--output terminal`
while preserving JSON as the default contract for deterministic fixtures.

Workflow execution now also includes a segregated repo skill:
`.codex/skills/delta-os-roadmap-operator/SKILL.md`, wired into `AGENTS.md` and
`docs/CODEX_WORKFLOW.md` so future runs can follow roadmap-first behavior with
minimal prompting.

Repository ergonomics also now include a root-level `requirements.txt` that
installs the package in editable mode with the Phase-1 dev/test toolchain and
YAML support by default, while keeping PySide6 GUI dependencies optional.

Milestone 19 is in progress. The scanner supports a real
market-data ingestion path via
`src/delta_os/infrastructure/data/yahoo_finance_candle_provider.py`, selected
through CLI/config provider routing (`--provider yahoo_finance`) while keeping
the same DataAgent/use-case/DTO flow.

Milestone 19 hardening includes deterministic online-provider timeout error
snapshots for both `scan` and `voice` commands, explicit provider health
projection (`ready/degraded/down`) from data-agent outcomes into dashboard
status items, symbol-normalization policy tests for mapped/dotted symbols, and
provider fetch-profile diagnostics surfaced through DTO-backed dashboard output.

Milestone 20 foundation is now partially complete. The codebase includes:
- live market stream/broker/risk ports
- immutable live/execution/risk-event DTO contracts
- live session orchestrator use case (`start/poll/submit/stop`)
- replay live-data provider with normalized event bus sequencing
- IBKR reference broker adapter scaffold with idempotent client-order behavior
- institutional execution risk gate with hard-block checks and kill-switch events
- config schema extensions for `live_data`, `execution`, `risk_limits`,
  `connectivity`, and `latency_slo`, plus hard-fail safety checks for unsafe
  live mode combinations

`python -m pytest` is the required verification command after changes. The
current scaffold test suite passes with 121 tests.

## Package Structure Summary

- `src/delta_os/domain`: framework-free entities, value objects, and services
  for candles, swings, trendlines, timeframe building, structure detection,
  liquidity concepts, probability, risk, and ranking.
- `src/delta_os/application`: DTOs, agent classes, ports, and use cases that
  coordinate domain services through explicit boundaries.
- `src/delta_os/application/dto/timeframe_intelligence.py`: deterministic
  per-timeframe summary DTOs for bias, structure, liquidity, volatility,
  breakout/fakeout, confidence, execution quality, and alignment.
- `src/delta_os/application/agents/timeframe_intelligence_agent.py`:
  application-layer builder for ordered multi-timeframe summaries and
  higher-timeframe alignment labels.
- `src/delta_os/infrastructure`: live/polling data providers, config loading/
  validation, logging, local universe/watchlist loading, and extension-point
  packages for alerts/voice/execution/risk/live orchestration.
- `src/delta_os/presentation`: CLI scanner entry point and PySide6 dashboard
  skeleton that renders DTO state only.
- `tests`: deterministic unit/integration/fixture coverage for live-integration
  contracts and replay-safe behavior.

## Next Implementation Direction

Complete deterministic voice parser/route failure snapshots and fallback
contracts, then add provider-down terminal-mode fixture coverage and operator
arming/audit workflows for the live command surface.
