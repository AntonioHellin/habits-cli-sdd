---
name: spec-generation
description: Use this skill when the user asks to create, draft, or review a feature specification (spec). Guides a requirements interview and produces a spec.md following the team's template.
---

# Spec Generation

Transforms a vague idea into an agreed-upon specification. The spec is the contract: if something is not here, it is not implemented.

## Process

1. **Read the context.** Read `docs/constitution.md` if it exists, and previous specs in `specs/` to adhere to established conventions and avoid contradicting agreed-upon decisions.
2. **Interview the user.** Ask questions **ONE at a TIME**, maximum 6, waiting for an answer before asking the next one. Focus on edge cases, error handling, and what is out of scope. Do not propose technical solutions: if the user asks "how would you do it?", redirect to the WHAT. Prioritize questions whose answers alter what needs to be built; discard questions with an obvious default answer.
3. **Choose the number.** Inspect `specs/` and use the next available three-digit number: `specs/NNN-<name-in-kebab-case>/spec.md`.
4. **Draft** using `spec-template.md` from this skill, without omitting any section. Acceptance criteria **must always follow EARS notation**, numbered as RF-1, RF-2, ... Every requirement must be verifiable: if you cannot think of how to verify it, it is poorly written.
5. **Mark unknowns** as `[NEEDS CLARIFICATION: specific question]`. Never fill a gap by inventing: a visible gap is information, a silent assumption is technical debt.
6. **Ask for explicit approval** upon completion. Do not proceed to the plan or write code until approval is granted.

## Rules

- The spec describes **WHAT** and **WHY**. Forbidden to include tech stack, architecture, file names, data schemas, algorithms, or function signatures: that belongs in the plan.
- **Always** include the "Out of Scope" section. This prevents scope creep.
- One requirement, one sentence. If you need an "and" to join two behaviors, they are two requirements.
- No unmeasurable adjectives: "fast", "intuitive", "robust" are not requirements. Specify the measurable threshold or omit it.
- Language: that of the project's constitution. If none exists, that of the user.

## EARS Notation

Five patterns. Choose the matching one, do not mix them:

| Pattern | Template | When to Use |
|---|---|---|
| Ubiquitous | THE SYSTEM SHALL \<response\> | Always true |
| Event-driven | WHEN \<trigger\>, THE SYSTEM SHALL \<response\> | Responds to an event |
| State-driven | WHILE \<state\>, THE SYSTEM SHALL \<response\> | During a condition |
| Optional | WHERE \<feature\>, THE SYSTEM SHALL \<response\> | Only if feature is present |
| Unwanted behavior | IF \<unwanted condition\>, THEN THE SYSTEM SHALL \<response\> | Errors and edge cases |

Well-written example:

> RF-4: IF the name already exists (evaluated case-insensitively and ignoring outer whitespace), THEN THE SYSTEM SHALL reject the creation and report the conflict (exit code 1).

Poorly written example (for contrast):

> ~~RF-4: The system must handle duplicates properly and be fast.~~  
> Missing EARS pattern, no verifiable criterion, two ideas in one sentence, and an unmeasurable adjective.

## When Reviewing an Existing Spec

If the user asks to review instead of create, do not rewrite: **detect and list**, numbered, in four sections: (1) remaining ambiguities, (2) contradictions between requirements, (3) uncovered edge cases, (4) conflicts with the constitution. Do not propose solutions until requested.

