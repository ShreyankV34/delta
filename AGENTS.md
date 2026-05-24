# DELTA OS Agent Instructions

These instructions apply to every future Codex run in this repository.

## Required Reading

Before every task, read:

- `readme.md`
- `roadmap_docx.docx`
- `docs/PROJECT_CONTEXT.md`
- `docs/TASKS.md`
- `docs/DECISIONS.md`
- `docs/FEEDBACK_CHECKLIST.md`
- `docs/DEVELOPMENT_LOG.md`

Treat `roadmap_docx.docx` as the source-of-truth technical specification.
Treat `readme.md` as the public project overview.

## Skill Usage

Use the segregated repo skill for DELTA execution workflow:

- Skill name: `delta-os-roadmap-operator`
- Skill path: `.codex/skills/delta-os-roadmap-operator/SKILL.md`

When a task starts, apply this skill's workflow before coding so roadmap-first
task selection, boundaries, testing, and doc updates remain consistent.

## Task Selection

- Continue from `docs/TASKS.md`.
- Use the `Active Task` first unless the user explicitly overrides it.
- If the active task is complete, move to `Next Tasks` in order.
- Do not start later milestones before current acceptance criteria are met.

## Live Integration Boundaries

- Follow `roadmap_docx.docx` live-market direction as primary implementation
  posture.
- Build production-grade scaffolding for live data, orchestration, execution
  adapters, and risk/safety controls through clean ports and DTO/event
  boundaries.
- Keep high-risk capabilities gated by explicit runtime controls and risk
  vetoes.
- Do not bypass risk/kill-switch logic from any fusion/execution path.
- Keep UI rendering-only; no market intelligence or risk decisions in UI code.

## Architecture Rules

- Preserve Clean Architecture boundaries.
- Keep domain intelligence out of UI and infrastructure code.
- Preserve DTO boundaries and agent separation.
- Agents communicate through DTOs/events and immutable state objects.
- Avoid shared mutable state and circular imports.
- The Risk Agent can veto setup output.
- The Fusion Agent must not bypass or erase risk vetoes.
- UI remains rendering-only and must not compute market intelligence.

## Coding Rules

- Use Python 3.11+ and type hints.
- Keep changes scoped to the active task.
- Prefer deterministic, config-driven behavior.
- Avoid hardcoded symbols, secrets, and environment-specific assumptions.
- Add focused pytest coverage for behavior changes.

## Verification And Documentation

- Run `python -m pytest` after changes.
- Fix test failures before reporting completion.
- Update project docs after each task:
  - `docs/TASKS.md`
  - `docs/PROJECT_CONTEXT.md` when status or direction changes
  - `docs/DECISIONS.md` when an architectural decision changes
  - `docs/FEEDBACK_CHECKLIST.md` when review criteria change
  - `docs/DEVELOPMENT_LOG.md` for every completed task
- Report files changed, tests run, pass/fail result, assumptions, and the next
  minimal prompt.
