# Codex Workflow

This document keeps future Codex tasks small, consistent, and resumable.

## What To Read Before Each Task

Always read these files before making changes:

- `readme.md`
- `roadmap_docx.docx`
- `docs/PROJECT_CONTEXT.md`
- `docs/TASKS.md`
- `docs/DECISIONS.md`
- `docs/FEEDBACK_CHECKLIST.md`
- `docs/DEVELOPMENT_LOG.md`

Use `roadmap_docx.docx` as the source-of-truth technical specification.
Use `readme.md` as the public overview.

## Skill To Use

Apply the repo skill at task start:

- `.codex/skills/delta-os-roadmap-operator/SKILL.md`

This skill enforces roadmap-first execution, Phase-1 boundaries, deterministic
testing, and memory-doc updates.

## How To Choose The Next Task

1. Read `docs/TASKS.md`.
2. Work on `Active Task` unless the user explicitly gives a different task.
3. If `Active Task` is complete, move the next unchecked item from `Next Tasks`
   into `Active Task`.
4. Keep `Later Phase-1 Tasks` parked until current milestone work is done.
5. Do not advance phases without explicit user direction and updated docs.

## Coding Rules

- Follow `roadmap_docx.docx` as live-market-first implementation source.
- Keep deterministic replay fixtures for tests, but treat live integration as
  the main delivery track.
- Build live data, broker, and risk modules behind explicit ports and DTOs.
- Keep risk veto and kill-switch logic non-bypassable.
- Preserve Clean Architecture:
  - domain contains core entities, value objects, and services
  - application contains DTOs, agents, ports, and use cases
  - infrastructure implements ports
  - presentation renders DTOs only
- Preserve DTO boundaries and agent separation.
- Agents communicate through DTOs/events and immutable state objects.
- Avoid circular imports and shared mutable state.
- Keep UI rendering-only. Widgets must not compute market intelligence.
- Use type hints and deterministic behavior.
- Keep configuration outside domain services where practical.

## Testing Rules

- Add focused pytest coverage for behavior changes.
- Prefer deterministic fixtures under `tests/fixtures`.
- For documentation-only workflow tasks, existing tests may be sufficient.
- Always run:

```powershell
python -m pytest
```

- Fix failures before reporting completion.

## Documentation Update Rules

Update project memory after each task:

- `docs/TASKS.md`: mark completed work, set the next active task, and adjust
  next/later tasks.
- `docs/PROJECT_CONTEXT.md`: update current status and implementation direction
  when they change.
- `docs/DECISIONS.md`: add or update ADRs for architecture decisions.
- `docs/FEEDBACK_CHECKLIST.md`: update review criteria when standards change.
- `docs/DEVELOPMENT_LOG.md`: add a dated entry for the completed task.
- `AGENTS.md`: update only when the future-agent operating rules change.

## How To Report Completion

Final responses should include:

- Files created or updated
- Tests run
- Whether pytest passed
- Assumptions or constraints
- The next minimal prompt the user can give

Keep the report concise and grounded in actual changes.
