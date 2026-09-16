---
name: task-implementation
description: Use this skill to implement exactly ONE specific task from tasks.md following TDD (test-first), updating tasks.md, and running pytest to verify quality gates.
---

# Task Implementation

Executes a single task from `specs/<feature>/tasks.md` in strict adherence to Test-Driven Development (TDD) and `docs/constitution.md`.

## Core Invariants
1. **Implement ONLY the requested task (Tn)**. Never implement multiple tasks at once.
2. **Test-First (Red -> Green -> Refactor)**:
   - Write the failing automated test(s) first.
   - Run `pytest` to confirm failure (Red).
   - Write the minimal implementation code to pass (Green).
   - Verify all tests pass (`pytest -q`).
3. **Update Tasks File**:
   - Check off the completed task in `specs/<feature>/tasks.md` (`- [x] **Tn: ...**`).
4. **Report and Stop**:
   - Report the `pytest -q` execution result, confirm all tests pass, identify the covered `RF-*` requirement IDs, and STOP. Do not start the next task.

