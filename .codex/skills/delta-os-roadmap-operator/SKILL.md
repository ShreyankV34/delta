---
name: delta-os-roadmap-operator
description: Execute DELTA OS repository work in a roadmap-first, memory-driven way. Use for any coding, docs, testing, or review task inside the DELTA OS repo where `roadmap_docx.docx` is the source of truth and progress must continue from `docs/TASKS.md` within Phase-1 boundaries.
---

# Delta Os Roadmap Operator

## Workflow

1. Read required project memory before touching code:
   - `readme.md`
   - `roadmap_docx.docx`
   - `docs/PROJECT_CONTEXT.md`
   - `docs/TASKS.md`
   - `docs/DECISIONS.md`
   - `docs/FEEDBACK_CHECKLIST.md`
   - `docs/DEVELOPMENT_LOG.md`
2. Treat `roadmap_docx.docx` as source-of-truth technical specification.
3. Select work from `docs/TASKS.md`:
   - Do `Active Task` first unless user overrides.
   - If complete, promote next item from `Next Tasks`.
4. Enforce Phase-1 boundaries:
   - Keep offline-first and CSV-based.
   - Do not implement broker execution, live routing, WebSockets, exchange connectivity, live RL execution, C++, FPGA, or HFT routing.
5. Enforce architecture rules:
   - Keep Clean Architecture boundaries.
   - Keep UI rendering-only (no domain intelligence in UI/widgets).
   - Keep agent communication via DTOs/events.
6. Implement and verify:
   - Add focused deterministic tests.
   - Run `python -m pytest --basetemp .pytest_tmp`.
   - Fix failures before completion.
7. Update memory docs after each completed task:
   - `docs/TASKS.md`
   - `docs/PROJECT_CONTEXT.md`
   - `docs/DECISIONS.md`
   - `docs/FEEDBACK_CHECKLIST.md`
   - `docs/DEVELOPMENT_LOG.md`
8. Report completion with:
   - files changed
   - tests run + pass/fail
   - assumptions
   - next minimal prompt

## Task Routing Rules

- For feature requests: implement directly, then test and update docs.
- For review requests: prioritize bugs/regressions/test gaps first.
- For workflow/setup requests: update instructions/docs and verify reproducibility.
- For GUI polish requests: improve presentation only; do not move intelligence into UI.

## Output Contract

- Keep CLI JSON output as default machine contract when existing fixtures depend on it.
- Add optional human-readable terminal output only through explicit flags.
- Preserve deterministic snapshots for integration tests.

## Commands

- Run tests:
  - `python -m pytest --basetemp .pytest_tmp`
- Run scanner:
  - `python -m delta_os.presentation.cli.main scan --config configs/app.yaml`
- Run voice command:
  - `python -m delta_os.presentation.cli.main voice --config configs/app.yaml --text "Show top compression candidates."`

Use this skill whenever working inside this repo so execution stays roadmap-aligned and resumable.
