# DELTA OS Task Board (Roadmap-Aligned Live Integration)

## Current Phase

Phase 2: Live Market Integration Foundation.

Primary operating target is live market ingestion and execution-safe orchestration
aligned to `roadmap_docx.docx`. Deterministic replay remains for test validation,
not as the product posture.

## Current Milestone

Milestone 20: Live session contracts, orchestration, and execution safety gates.

## Completed Tasks

- [x] Read `readme.md` and `roadmap_docx.docx`
- [x] Create Clean Architecture scaffold under `src/delta_os`
- [x] Build deterministic intelligence pipeline and presentation DTO contracts
- [x] Add profile/config validation and deterministic integration fixtures
- [x] Add live polling provider path (`yahoo_finance`) with provider health projection
- [x] Add deterministic online-provider failure contracts for `scan` and `voice`
- [x] Add symbol normalization tests and provider diagnostics summaries
- [x] Implement live session runtime stack:
      add stream/broker/risk ports, live DTO contracts, session orchestrator,
      replay provider, IBKR reference execution adapter scaffold, and institutional
      risk gate with hard blocking behavior.
- [x] Add startup config hard-fail checks for unsafe live combinations

## Active Task

- [ ] Add deterministic voice parser/route failure snapshots and fallback contracts

## Next Tasks

- [ ] Add provider-down terminal-mode snapshot coverage for scan/voice error surfaces
- [ ] Add operator arming/unarming workflow and audit logging surfaces
- [ ] Add live-mode CLI command group for session status/run/stop/arm/disarm

## Later Tasks (Phase 2+)

- [ ] Add WebSocket-first live ingestion adapter with heartbeat and reconnect jitter
- [ ] Add broker account/positions reconciliation and partial-fill lifecycle tests
- [ ] Add kill-switch propagation tests across orchestrator + execution path
- [ ] Add latency budget assertions for representative live pipelines (<1s target)
- [ ] Extend provider/broker capability matrix and runbook docs

## Acceptance Criteria

- Live data, execution, and risk are separated by explicit ports and immutable DTOs.
- Risk vetoes and kill-switch events are non-bypassable.
- Live-mode decisions are config-driven with deterministic test coverage.
- UI remains rendering-only and receives state through DTO projections.
- `python -m pytest --basetemp .pytest_tmp` passes.

## Definition of Done

A task is done when:

- Code and tests are complete for the task scope.
- Runtime behavior is deterministic under replay fixtures.
- Architecture boundaries (domain/application/infrastructure/presentation) are preserved.
- Docs are updated:
  - `docs/TASKS.md`
  - `docs/PROJECT_CONTEXT.md`
  - `docs/DECISIONS.md` (if architecture changed)
  - `docs/FEEDBACK_CHECKLIST.md` (if review criteria changed)
  - `docs/DEVELOPMENT_LOG.md`
- `python -m pytest --basetemp .pytest_tmp` passes.

## Blockers / Questions

- Confirm final broker priority after IBKR reference scaffold: IBKR-only vs IBKR+India broker adapter in the next milestone.
- Confirm preferred first WebSocket data backend for production hardening.

## Next Recommended Prompt

```text
Continue from docs/TASKS.md and complete the Active Task only.
Follow roadmap_docx.docx, keep Clean Architecture and DTO/event boundaries strict,
run python -m pytest --basetemp .pytest_tmp, and update project docs.
```
