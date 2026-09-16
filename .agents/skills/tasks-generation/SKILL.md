---
name: tasks-generation
description: Use this skill to break down an approved architectural plan (plan.md) and feature spec (spec.md) into actionable, granular, TDD-oriented tasks (tasks.md).
---

# Tasks Generation

Breaks down an approved `plan.md` into small, ordered, test-driven development (TDD) tasks. Every task must be manageable in 20-30 minutes, strictly ordered by dependency, and directly tied to functional requirements (RF-*).

## Input Prerequisites
Before running this skill, verify that the active feature specification directory exists (e.g. `specs/<feature-name>/`) and contains:
1. `spec.md` — The finalized functional contract.
2. `plan.md` — The approved architectural and technical design document.

## Process

1. **Read the Context**:
   - Review `docs/constitution.md` for architectural invariants, testing standards, and design principles.
   - Review the target `specs/<feature>/spec.md` for functional requirements (`RF-*`) and success criteria.
   - Review `specs/<feature>/plan.md` for the technical breakdown, module design, and testing matrix.

2. **Generate Granular Tasks**:
   - **Order by Dependency**: Core domain model -> Data / Storage layer -> CLI presentation -> End-to-end / Integration.
   - **TDD (Test-First)**: Every task must specify writing the test first, verifying test failure (Red), implementing minimal code (Green), and refactoring if necessary.
   - **Granularity**: Sized for 20-30 minutes of focused work per task.
   - **Traceability**: Explicitly map each task to its associated `RF-*` requirement IDs.
   - **Clear Definition of Done**: Each task must end with a precise `Done when:` condition that can be validated via tests or commands.

3. **Format Output**:
   - Follow the template in `tasks-template.md`.
   - Save the result to `specs/<feature>/tasks.md`.

