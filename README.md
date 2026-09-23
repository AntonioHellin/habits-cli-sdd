# ⚡ Habits Tracker CLI (`habits-tracker-cli`)

A lightweight, reliable command-line interface in Python to track daily study habits and monitor consecutive-day streaks.

---

## Project Overview

**Habits Tracker CLI** is an educational, Spec-Driven Development (SDD) project designed to provide an ultra-lightweight CLI to build and maintain study streaks with zero external runtime dependencies.

### Repository Naming Analysis
- **Recommended Repository Name**: `habits-tracker-cli`
- **Naming Formula**: **Formula A** (`[domain/product]-[core-function]`)
- **Rationale**: Removes the redundant workflow tag (`-sdd`) in favor of a clear, functional kebab-case name specifying domain (`habits`), purpose (`tracker`), and interface form factor (`cli`).

---

## Prerequisites

- **Python**: `>= 3.12`
- **Virtual Environment Tool**: Standard `venv` or [`uv`](https://github.com/astral-sh/uv)


## Commands

```text
habits add "study python"     → creates a new habit
habits done "study python"    → marks the habit as completed TODAY
habits list                   → lists habits with their current streak
```

## Project Structure

```text
habits-cli-sdd/
├── AGENTS.md
├── GEMINI.md
├── pyproject.toml
├── docs/
│   └── constitution.md
├── specs/
│   └── 001-habits-mvp/
│       ├── spec.md
│       ├── plan.md
│       └── tasks.md
├── habits/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── core.py
│   └── storage.py
└── tests/
    ├── __init__.py
    ├── test_cli.py
    ├── test_core.py
    ├── test_smoke.py
    └── test_storage.py
```

## Usage

```bash
python -m habits add "Study Python"   # creates the habit
python -m habits done "Study Python"  # marks it as done TODAY (idempotent)
python -m habits list                 # lists habits sorted by streak descending
```

Data is stored locally in a single human-readable JSON file (`~/.habits.json` by default, configurable via the `HABITS_FILE` environment variable).
Exit codes:
- `0`: Operation succeeded.
- `1`: User/business error (empty name, duplicate name, unknown habit, or unreadable/corrupted data file). Corrupted files are never overwritten or destroyed.
- `2`: Syntax or command-line usage error.

## Development

```bash
python -m venv .venv
# On Windows: .venv\Scripts\pip install pytest
# On Linux/macOS: .venv/bin/pip install pytest
pytest -q
```

Or using `uv`:
```bash
uv run pytest -q
```

---

## SDD Prompts

### 1. Setup, Constitution, and AGENTS.md

**Constitution:**

```text
We are going to create the constitution for a new project: a Python CLI to
track study habits and calculate streaks. It is an educational project that
must be maintainable by a junior developer.

Propose a docs/constitution.md with 6 non-negotiable, short, and verifiable
principles covering: stack simplicity, relationship between spec and code,
separation between logic and interface, testing policy, data persistence,
and code/message language. Maximum 15 lines. Await my approval.
```

*Generates [docs/constitution.md](./docs/constitution.md)*  
*Configures [AGENTS.md](./AGENTS.md) and [GEMINI.md](./GEMINI.md)*

**Specification:**

```text
Do NOT write code at any time. We are going to draft the specification for the
first feature of habits-cli-sdd. Read docs/constitution.md.

Initial idea: a CLI with three commands: create a habit, mark it as done today,
and list habits with their consecutive-day streak.

Your task:
1. Ask me questions ONE by ONE to eliminate ambiguities (edge cases, error
   handling, what is out of scope for the MVP). Maximum 6 questions.
2. Based on my answers, generate specs/001-habits-mvp/spec.md with this structure:
   context and goals, target audience, user stories, numbered functional requirements
   (RF-x) with acceptance criteria in EARS notation in English, non-functional
   requirements, edge cases, out of scope, completion criteria, and open questions
   marked as [NEEDS CLARIFICATION].
3. Focus on WHAT and WHY. No stack, architecture, or file names: that belongs in the plan.
```

*Generates [specs/001-habits-mvp/spec.md](./specs/001-habits-mvp/spec.md)*

**Clarification:**

```text
Review specs/001-habits-mvp/spec.md as if you were a very thorough QA professional.
List: (1) remaining ambiguities, (2) contradictions between requirements,
(3) uncovered edge cases, (4) conflicts with docs/constitution.md.
Do not propose solutions yet: only detect. Format: numbered list.
```

**Planning:**

```text
Read docs/constitution.md and specs/001-habits-mvp/spec.md. Do NOT write code.
Generate specs/001-habits-mvp/plan.md containing: module structure, JSON data model
with an example, streak calculation algorithm in pseudocode, CLI contract (commands,
outputs, exit codes), justified technical decisions (with discarded alternatives),
and testing strategy. Everything must adhere to the constitution and cover all RFs.
Indicate which RF is covered by each section.
```

*Generates [specs/001-habits-mvp/plan.md](./specs/001-habits-mvp/plan.md)*

**Tasks:**

```text
From spec.md and plan.md, generate specs/001-habits-mvp/tasks.md:
small tasks (max. 20-30 min each), ordered by dependency, each with its covered
RFs and a verifiable "Done when:" line. Use checkboxes.
```

*Generates [specs/001-habits-mvp/tasks.md](./specs/001-habits-mvp/tasks.md)*

**Implementation:**

```text
Implement ONLY task Tn from specs/001-habits-mvp/tasks.md, following
plan.md and the constitution. Write tests first, then the code.
Run pytest -q and show me the output. When finished: check Tn in tasks.md,
state which RFs it covers, and STOP. Do not start the next task.
```

*Generates the implementation inside `habits/` and `tests/`*

**Validation:**

```text
Go through specs/001-habits-mvp/spec.md requirement by requirement (RF-1 to RF-12).
For each one indicate: which test covers it, and the execution result.
If any RF is not covered or fails, state it clearly. Then verify the completion
criteria and give me a verdict: is the spec fulfilled?
```

**Next Steps (Change Management):**

```text
New requirement for habits-cli-sdd: mark as done yesterday with
`habits done <name> --yesterday`. Do NOT touch code. First: update
specs/001-habits-mvp/spec.md (new RF with EARS + edge cases: what if yesterday
was already marked? does it affect streaks?) and show me the spec diff.
```

---

## Samples

### Sample `AGENTS.md`

```markdown
# AGENTS.md — <project>

## Project
<What it is, in 2-3 sentences. Architecture, core technologies.>

## Commands
- Run: `<command>`
- Tests: `<command>`
- Lint/Format: `<command>`

## Style and Conventions
<Language version, naming conventions, language of code and user messages.>

## Rules
- Read docs/constitution.md and active spec before touching code.
- <Boundaries: what not to modify, what not to add without asking.>

## When Finishing Any Task
- <Mandatory verification, e.g., execute tests and ensure all pass.>
```

### Sample `prompts.md`

```markdown
## Prompts by Phase

| Phase | Core Prompt |
| :--- | :--- |
| Constitution | "Propose the constitution for this project: N short, verifiable principles covering stack, quality, tests, and boundaries. Max. 15 lines. Await my approval." |
| Spec (Interview) | "Do NOT write code. Ask me questions one by one (max. 6) regarding edge cases, error handling, and scope. Then generate spec.md with numbered RFs in EARS, out of scope, and completion criteria. Only WHAT and WHY." |
| Clarification | "Review the spec like a professional QA: ambiguities, contradictions, missing edge cases, conflicts with the constitution. Detect only, do not resolve." |
| Plan | "Read constitution and spec. Without writing code: generate plan.md with modules, data model, justified decisions (with discarded alternatives), and test strategy. Map which RF covers each part." |
| Tasks | "Decompose the plan into tasks of <30 min, ordered by dependency, each with its RFs and a verifiable 'Done when:' line. Use checkboxes." |
| Implementation | "Implement ONLY task Tn. Tests first. Run the suite and show me the output. Mark Tn as done and STOP." |
| Validation | "Walk through the spec RF by RF: which test covers each one and its result. Final verdict: is the spec fulfilled?" |
| Change | "New requirement: <X>. Do NOT touch code: update the spec first and show me the diff." |
```

### Sample `spec.md`

```markdown
# Spec NNN — <Feature Name>

## Context and Goals
<What problem this solves and why it is worthwhile. One paragraph.>

## Target Audience / Actors
<Who uses this.>

## User Stories
- H1: As a <role>, I want to <action> so that <benefit>.

## Functional Requirements (Acceptance Criteria in EARS)
- RF-1: WHEN <event>, THE SYSTEM SHALL <response> (expected output/result).
- RF-2: IF <unwanted condition>, THEN THE SYSTEM SHALL <response>.
- RF-3: WHILE <state>, THE SYSTEM SHALL <response>.
- RF-4: THE SYSTEM SHALL <ubiquitous/continuous behavior>.

## Non-Functional Requirements
<Only applicable items: performance, security, platform, language...>

## Edge Cases
<Empty states, duplicates, corrupted data, limits, concurrency...>

## Out of Scope
<What is explicitly NOT done in this iteration.>

## Completion Criteria
<E.g., all RFs covered by green tests + manual walkthrough of the main flow.>

## Open Questions
- [NEEDS CLARIFICATION] <question>
```

---

## License

Proprietary. All rights reserved. Not licensed for redistribution, public sublicensing, or resale.

