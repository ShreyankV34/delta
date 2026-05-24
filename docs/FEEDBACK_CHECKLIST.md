# DELTA OS Feedback Checklist

Use this checklist when reviewing future Codex or human changes.

## Scope

- [ ] Data mode remains within approved scope: live provider(s) (e.g. `yahoo_finance`, websocket adapters) as primary; deterministic replay and recorded fixtures remain available for tests.
- [ ] No unapproved broker execution, live order routing, or unsafe live RL execution has been enabled without sandboxing and Risk & Safety checks. WebSocket-based data adapters are allowed with deterministic mocks for CI.
- [ ] Future-only components are represented as docs or interfaces, not working
      live execution paths.

## Architecture

- [ ] Domain services have no UI or infrastructure dependencies.
- [ ] Application agents communicate through DTOs/events.
- [ ] DTOs are immutable and serializable.
- [ ] UI code renders DTOs only.
- [ ] Risk veto cannot be bypassed by fusion or ranking.

## Engineering Quality

- [ ] Code has type hints.
- [ ] Tests are deterministic.
- [ ] Config values are not hardcoded in domain services.
- [ ] New behavior has focused pytest coverage.
- [ ] Structural geometry changes preserve or update fixture coverage for noisy
      wedges, channels, false-breakout sweeps, and imperfect trendline respect.
- [ ] Structural geometry threshold changes are represented through
      `StructureScoringConfig` instead of hidden magic values.
- [ ] UI fixture changes preserve DTO-driven coverage for overlays and
      multi-timeframe rows without adding domain logic to widgets.
- [ ] Config schema validation remains near config loading and covers the
      checked-in Phase-1 YAML profiles.
- [ ] Offline pipeline logging remains test-covered for both success and failure
      paths without moving orchestration concerns into UI code.
- [ ] Deterministic replay coverage still proves repeated offline scans produce
      identical serialized output when replay mode is configured.
- [ ] Universe loading remains local, deterministic, and free of live market
      dependencies in Phase 1.
- [ ] Online data ingestion (when enabled) stays isolated to infrastructure
      provider adapters and does not fork application/domain logic.
- [ ] Online-provider tests use deterministic mocked transport (no flaky live
      network dependency in CI).
- [ ] Provider health transitions (`ready/degraded/down`) are sourced from
      data-agent/provider outcomes and projected through DTO status items.
- [ ] Scan/voice provider-failure paths return deterministic CLI error
      contracts (JSON + terminal summaries) rather than uncaught crashes.
- [ ] Live runtime orchestration remains port-based (stream/broker/risk) with
      immutable DTO/event boundaries.
- [ ] Execution risk gate stays fail-closed for provider-down/daily-loss
      breaches and kill-switch propagation.
- [ ] Multi-timeframe summaries remain ordered from higher to lower timeframe
      and are produced by application agents rather than UI widgets.
- [ ] Dashboard timeframe rows remain a rendering projection of
      `TimeframeIntelligenceDTO` state.
- [ ] Alert behavior remains deterministic across veto, breakout, liquidity,
      and monitor branches.
- [ ] Alert DTOs preserve confidence, reasoning, and risk notes from the agent
      boundary outward.
- [ ] CLI scan output remains fixture-backed for deterministic multi-timeframe
      replay/live summaries.
- [ ] Ranking and universe command outputs remain fixture-backed and stable
      across live-integration refactors.
- [ ] Dashboard ranking rows, alert timeline entries, and scanner activity lines
      remain DTO-projected and fixture-backed.
- [ ] Scan-profile CLI variants remain deterministic and schema-validated.
- [ ] Sidebar sections and top-status values remain DTO-projected and
      fixture-backed rather than hardcoded in widgets alone.
- [ ] Trade/risk profile summaries and watchlist summary projections remain
      deterministic and snapshot-tested.
- [ ] Universe-selection and filter sidebar labels remain config-derived and
      fixture-backed.
- [ ] Status-bar provider health and scan latency remain deterministic in Phase 1.
- [ ] Right-panel summary, probability, risk, and execution-quality sections
      remain DTO-projected and fixture-backed.
- [ ] Multi-row ranking dashboard output remains fixture-backed and
      rendering-only.
- [ ] Bottom-panel alerts, timeline, scanner activity, and diagnostics remain
      grouped through DTO-backed helpers rather than widget-local logic.
- [ ] Scan-profile override/fallback behavior remains snapshot-tested for the
      CLI surface.
- [ ] Phase-1 voice commands remain deterministic, grounded in DTO state, and
      blocked from execution flows unless future safety gates explicitly change.
- [ ] Dashboard voice transcript and voice status fields remain DTO-projected
      and fixture-backed.
- [ ] Right-panel voice response cards remain deterministic and grounded in
      voice response DTO outputs.
- [ ] Voice CLI blocked-execution and alert-explanation outputs remain
      snapshot-tested.
- [ ] Local voice infrastructure placeholders (STT/TTS/push-to-talk) remain
      dependency-light and deterministic in Phase 1.
- [ ] Voice interaction-state projection remains use-case-owned (not UI-owned)
      and maps command results into dashboard status/transcript fields.
- [ ] Voice transcript history truncation remains deterministic and bounded.
- [ ] Voice status transitions (listening/processing/responding/error) remain
      test-covered.
- [ ] Voice mute/unmute command paths remain CLI-safe and GUI-independent.
- [ ] Voice stale/unavailable guard responses remain explicit when context is
      outdated or missing required DTO fields.
- [ ] CLI default JSON output contract remains stable while optional
      `--output terminal` summaries stay readable and deterministic.
- [ ] Compact voice audit-history projection remains deterministic in terminal
      summaries and sourced from voice transcript DTO state.
- [ ] GUI shell styling/layout changes keep UI rendering-only boundaries and do
      not move domain intelligence into widgets.
- [ ] Repo skill `.codex/skills/delta-os-roadmap-operator` remains aligned with
      `AGENTS.md`, `docs/CODEX_WORKFLOW.md`, and current Phase-1 boundaries.
- [ ] Public project story remains in `readme.md`; technical implementation
      rules remain aligned to `roadmap_docx.docx`.
