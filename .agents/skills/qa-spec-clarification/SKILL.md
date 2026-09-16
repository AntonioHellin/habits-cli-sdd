---
name: qa-spec-clarification
description: Use this skill to review a feature specification (spec.md) as a thorough QA professional, identifying ambiguities, contradictions, uncovered edge cases, and constitutional conflicts before implementation planning.
---

# QA Spec Clarification

Conducts a rigorous QA and specification audit on an existing `spec.md` before moving forward to `plan.md` or implementation. The goal is to detect flaws early without prematurely proposing solutions.

## Input Prerequisites
- `docs/constitution.md`: The project's inviolable architectural and engineering rules.
- `specs/<feature>/spec.md`: The feature specification undergoing review.

## Process

1. **Perform QA Audit**:
   Read `docs/constitution.md` and the target `specs/<feature>/spec.md` with an adversarial QA mindset.
   Identify:
   - **Ambiguities**: Vaguely phrased requirements, undefined states, or ambiguous words (e.g. "properly", "efficiently", "soon").
   - **Contradictions**: Inconsistencies between user stories, functional requirements (`RF-*`), edge cases, or out-of-scope sections.
   - **Uncovered Edge Cases**: Unhandled inputs, missing boundary conditions, data corruption scenarios, duplicate entries, or time/date variations.
   - **Constitutional Conflicts**: Any requirement that violates stack constraints, dependency limits, persistence rules, or testing principles from `docs/constitution.md`.

2. **Strict Rule — Detection Only**:
   - **Do NOT propose solutions or rewrite the spec in this step.**
   - Focus strictly on exposing questions, gaps, and potential pitfalls for the author/user to decide upon.

3. **Output Format**:
   Present findings in a structured, numbered list divided into four clear sections:
   1. `Ambiguities`
   2. `Contradictions`
   3. `Uncovered Edge Cases`
   4. `Conflicts with Constitution`
   
   If no issues are found in a specific category, explicitly state `None identified`.

