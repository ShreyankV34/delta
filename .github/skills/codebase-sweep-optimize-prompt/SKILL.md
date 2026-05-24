---
name: codebase-sweep-optimize-prompt
description: "Sweep workspace against documented scope, verify compliance, audit test coverage, and generate optimized next-task prompt for coding agents. Use when: after major milestones, before new tasks, to reset context, or to handoff between development sessions. Produces a minimal, context-aware prompt that respects completed work and guidance documents."
context: workspace
---

# Codebase Sweep & Optimized Prompt Generation

## When to Use This Skill

- After completing a milestone to confirm state and plan next work
- Before starting a new coding task to understand current context
- When handing off work between developer sessions or agents
- To reset context and ensure alignment with documented scope
- When documentation may have drifted from implementation

## What This Skill Produces

**Output**: An optimized minimal prompt for coding agents that:
1. Reflects actual codebase state (structure, completeness, test results)
2. Respects all guidance documents (AGENTS.md, TASKS.md, DECISIONS.md, etc.)
3. Identifies what's done, what's pending, what's blocked
4. Points to the next actionable task with clear acceptance criteria
5. Includes only essential context to avoid prompt bloat

**Runtime**: ~5–10 minutes depending on codebase size

---

## Step-by-Step Workflow

### Phase 1: Read Required Documentation (2–3 min)

**Goal**: Understand project scope, rules, and current state

Read in this order:
1. **`AGENTS.md`** or **`copilot-instructions.md`** — Agent operating rules, Phase/scope boundaries, architecture rules, coding rules, verification steps
2. **`readme.md`** — Public project overview and philosophy
3. **`docs/PROJECT_CONTEXT.md`** — Current milestone, completion status, package structure
4. **`docs/TASKS.md`** — Task board with Active Task, Next Tasks, Later Tasks, Acceptance Criteria
5. **`docs/DECISIONS.md`** — Architecture decisions (ADRs) to verify are implemented
6. **`docs/FEEDBACK_CHECKLIST.md`** — Review criteria that must hold for all changes
7. **`docs/DEVELOPMENT_LOG.md`** — Historical record of completed work; note latest date and milestone

**Decision Point**: If any required doc is missing or severely outdated, flag this in the final prompt. Consider updating `docs/CODEX_WORKFLOW.md` or `docs/PROJECT_CONTEXT.md` before proceeding.

### Phase 2: Codebase Structure Sweep (1–2 min)

**Goal**: Verify package organization matches documented architecture

Check:
- [ ] Domain layer (`src/<project>/domain/`) contains entities, value objects, services only
- [ ] Application layer (`src/<project>/application/`) contains DTOs, agents, ports, use cases
- [ ] Infrastructure layer (`src/<project>/infrastructure/`) implements adapters and config
- [ ] Presentation layer (`src/<project>/presentation/`) is rendering-only (no domain logic)
- [ ] No cross-layer imports (especially: domain/application do NOT import from presentation)
- [ ] All major agents listed in `application/agents/__init__.py`
- [ ] All DTOs listed in `application/dto/__init__.py`

**Tool**: Use `file_search` to spot-check layer boundaries. Use `grep_search` to detect invalid imports (e.g., `import from presentation` in domain/application files).

**Decision Point**: If violations found, note them. Are they tolerable interim violations (e.g., during refactor), or critical blocker? If critical, the next task must fix them before proceeding to features.

### Phase 3: Test Suite Verification (1–2 min)

**Goal**: Confirm all tests pass and coverage is proportional to changes

Run:
```bash
python -m pytest -v
```

Record:
- [ ] Total test count
- [ ] Pass/Fail count
- [ ] Run time
- [ ] Coverage distribution (unit vs integration vs fixture-backed)

**Decision Point**:
- **All pass**: Continue to Phase 4
- **Some fail**: Note which tests fail. Determine if they're recent failures (should be fixed before new work) or pre-existing (document as known issue)
- **None pass**: Stop. Codebase is in broken state; next prompt should prioritize test fixes

### Phase 4: Compliance Audit Against FEEDBACK_CHECKLIST (2–3 min)

**Goal**: Verify that completed code and tests meet the documented review criteria

Spot-check 5–10 key items from `FEEDBACK_CHECKLIST.md`:
- [ ] Phase-1 scope enforced (no forbidden systems: broker, WebSocket, live RL, C++, FPGA, HFT)
- [ ] Domain services have no UI or infrastructure dependencies
- [ ] DTOs are immutable (`@dataclass(frozen=True)` or equivalent)
- [ ] UI code renders DTOs only (no intelligence computation)
- [ ] Code has type hints
- [ ] Tests are deterministic (no flaky randomness)
- [ ] Config values not hardcoded in domain services
- [ ] Architectural decisions (ADRs) are implemented

**Tool**: Use `grep_search` for forbidden keywords (e.g., `broker`, `WebSocket`, `live_execution`). Use `semantic_search` to spot-check agent/DTO logic for violations. Read sample files from domain, application, and presentation layers.

**Decision Point**: If multiple checklist items fail, the next task must include compliance fixes. If checklist passes, proceed.

### Phase 5: Analyze TASKS.md Board (1 min)

**Goal**: Understand what's done, what's active, and what's next

Extract:
- **Current Milestone**: From `## Current Milestone` section
- **Active Task**: From `## Active Task` section (should have `[ ]` checkbox)
- **Next Tasks**: From `## Next Tasks` section (ordered list of unchecked items)
- **Blockers/Questions**: From relevant sections
- **Acceptance Criteria**: From `## Acceptance Criteria` section

**Decision Point**: 
- If Active Task is done (or incomplete but blocked), determine which Next Task should become Active
- If no Active Task is clear, next prompt must start with task definition
- If Acceptance Criteria are vague or missing, next prompt must clarify them

### Phase 6: Synthesize Compliance Audit (1–2 min)

**Goal**: Produce a summary of what's working and what needs attention

Create a table or checklist covering:

| Item | Status | Evidence |
|------|--------|----------|
| Test Coverage | ✅/⚠️/❌ | X/Y tests passing |
| Architecture | ✅/⚠️/❌ | Layer boundaries intact? |
| Phase-1 Scope | ✅/⚠️/❌ | Forbidden systems absent? |
| Documentation | ✅/⚠️/❌ | All 7 required docs present and current? |
| ADRs Implemented | ✅/⚠️/❌ | # of ADRs verified |
| Code Quality | ✅/⚠️/❌ | Type hints, determinism, config-driven? |

**Decision Point**: 
- **All ✅**: Codebase is in healthy state; next prompt can focus on feature work
- **Mix of ⚠️/❌**: Identify which areas must be fixed first
- **Multiple ❌**: Next prompt should prioritize stabilization over new features

### Phase 7: Generate Optimized Next Prompt (1–2 min)

**Goal**: Synthesize a minimal, actionable prompt for the next coding task

Template:

```
Continue from docs/TASKS.md. 
Current Milestone: [MILESTONE_NAME] ([# of tasks completed])
Active Task: [TASK_NAME]

Scope:
- [Key boundary or constraint from AGENTS.md]
- [Key boundary or constraint from AGENTS.md]

Acceptance Criteria:
- [from TASKS.md Acceptance Criteria]

Quality Gates:
- Run `python -m pytest` after changes
- Verify [1–2 key checklist items from FEEDBACK_CHECKLIST.md]
- Update [which docs] after completion

Files to Read Before Starting:
- docs/TASKS.md (for task detail)
- docs/DECISIONS.md (for architectural context)
- docs/FEEDBACK_CHECKLIST.md (for review criteria)

Next Action:
[ONE SENTENCE: what the agent should do]
```

**Optimization Rules**:
1. **Be specific**: "Add voice interaction-state updater" beats "work on voice"
2. **Be minimal**: Include only context needed to start work; don't repeat entire project history
3. **Respect boundaries**: Mention Phase-1 scope, architectural rules, test requirements explicitly
4. **Point forward**: Name the next 2–3 tasks after this one for visibility
5. **Call out blockers**: If blockers exist, mention them

---

## Quality Criteria / Completion Checks

The skill is complete when:

- [ ] All 7 required docs have been read (or absence noted)
- [ ] Test suite runs and results are recorded
- [ ] Codebase structure matches documented architecture (or violations noted)
- [ ] Compliance audit completed against FEEDBACK_CHECKLIST
- [ ] Current milestone and active task identified from TASKS.md
- [ ] Synthesized audit produced (table or checklist)
- [ ] Optimized next prompt generated (fits in 200–400 words)
- [ ] Prompt includes: scope, acceptance criteria, quality gates, next action
- [ ] Prompt is saved to session memory or shared with user

---

## Example Prompt Output

```
Continue from docs/TASKS.md.
Current Milestone: 17 - Voice Dashboard Integration (11/11 scaffolding tasks complete)
Active Task: Add voice interaction-state updater

Scope:
- Keep Phase 1 offline-first and CSV-based
- Preserve DTO boundaries; agents communicate through immutable state only
- UI remains rendering-only; no domain logic in presentation code
- Risk Agent veto cannot be bypassed

Acceptance Criteria:
- Voice interaction-state updater is covered by deterministic tests
- VoiceCommandResultDTO maps into dashboard transcript/status fields
- Serialized Phase-1 output remains stable for offline scans
- python -m pytest passes (currently 74/74)

Quality Gates:
- Add focused pytest coverage for voice state mapping
- Verify no UI-side intelligence computation
- Update docs/TASKS.md with completion when done

Next Action:
Implement VoiceCommandResultDTO→DashboardStateDTO projection in the voice use case, add deterministic tests, and run pytest.
```

---

## Decision Tree

```
START
├─ Read all 7 docs
├─ Are all docs present & recent? 
│  ├─ No → Flag for update in next prompt; continue with what's available
│  └─ Yes → Proceed
├─ Run pytest
├─ Do all tests pass?
│  ├─ No → Next prompt should prioritize test fixes
│  └─ Yes → Proceed
├─ Sweep codebase for structure/imports
├─ Are architecture boundaries intact?
│  ├─ No → Next prompt should include compliance fixes
│  └─ Yes → Proceed
├─ Audit against FEEDBACK_CHECKLIST (spot-check 5–10 items)
├─ Are 80%+ items passing?
│  ├─ No → Flag violations; next prompt includes fixes
│  └─ Yes → Proceed
├─ Extract Active Task from TASKS.md
├─ Is Active Task clear & scoped?
│  ├─ No → Next prompt starts with task definition
│  └─ Yes → Generate next prompt
└─ Output optimized prompt
END
```

---

## Bundled Assets

None. This skill uses only built-in tools (file_search, grep_search, semantic_search, read_file).

---

## Related Skills/Customizations

- **`AGENTS.md`**: Agent operating rules (read this first)
- **`docs/FEEDBACK_CHECKLIST.md`**: Detailed review criteria for each checklist item
- **`docs/CODEX_WORKFLOW.md`**: Workflow for consistent task execution

---

## Anti-Patterns

❌ **Don't**:
- Skip reading required docs to save time (you'll miss critical context)
- Assume tests are passing without running them
- Ignore architecture violations in the name of moving fast
- Create prompt that repeats entire project history
- Suggest next task without confirming active task is done

✅ **Do**:
- Read docs in the specified order (each builds on the previous)
- Record actual test results and failure details
- Flag violations clearly; don't hide them
- Keep prompt minimal and actionable
- Call out blockers and assumptions explicitly

---

## Example Usage

User: "I haven't worked on this project in a week. What should I work on next?"

Agent (using this skill):
1. Reads AGENTS.md → learns Phase-1 scope and rules
2. Reads docs/TASKS.md → identifies Milestone 17, Active Task "voice interaction-state updater"
3. Runs pytest → 74/74 pass ✅
4. Sweeps architecture → Clean Architecture intact ✅
5. Audits checklist → all items passing ✅
6. Generates optimized prompt (see example above)
7. Shares with user: "Your active task is [voice updater]. Here's your next prompt: [...]"

---

## Troubleshooting

**Q: Documentation is outdated. Should I update it before generating the prompt?**  
A: Read the doc as-is. In Phase 7, note the drift in the prompt: "Note: docs/PROJECT_CONTEXT.md references Milestone X but actual code is on Milestone Y. Update context docs as part of next task." Don't let outdated docs block prompt generation.

**Q: Tests are failing. Should I fix them first?**  
A: In Phase 5, flag the failures. In Phase 7, include in prompt: "Note: X tests are currently failing. Fix or triage these before starting feature work." The agent can then decide to prioritize test fixes.

**Q: Codebase is huge. This will take 10+ minutes.**  
A: Use targeted grep/search (don't read every file). Spot-check architecture with 5–10 file samples. Run tests once and record result. You don't need 100% coverage; 80% due diligence is sufficient.

**Q: I'm blocked by something that's not in the docs.**  
A: In Phase 6, add a "Blockers" section to the synthesized audit. In Phase 7, include in prompt: "Blocker: [description]. Please clarify or remove before starting next task."

