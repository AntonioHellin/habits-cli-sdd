---
name: plan-generation
description: Use this skill when the user asks to create, draft, or update a technical implementation plan (plan.md) from an approved specification and constitution. Formulates module architecture, data persistence models, CLI contracts, justified technical trade-offs, and testing strategies.
---

# Plan Generation

Transforms an approved functional specification (`spec.md`) and project constitution (`constitution.md`) into an actionable, decoupled technical plan (`plan.md`).

## Process

1. **Read the context.**
   - Read `docs/constitution.md` to ensure all architectural rules (stack, persistence, layer separation, language) are respected.
   - Read the active specification `specs/NNN-<feature>/spec.md`. Ensure every functional requirement (RF-x) and edge case is accounted for.
   - Inspect existing modules in `habits/` and tests in `tests/` to reuse existing patterns and avoid redundant designs.

2. **Structure the plan.**
   Use `plan-template.md` from this skill without omitting any section:
   - **Module Structure & Responsibilities:** Clearly define files, responsibilities, and which RFs each module covers. Ensure pure core logic has zero I/O or terminal dependencies.
   - **Data Persistence Model:** Document the JSON schema, field types, and an explicit JSON payload example.
   - **Algorithms in Pseudocode:** Write explicit pseudocode for core business algorithms, tracing edge cases (empty states, boundaries, gaps).
   - **CLI Contract:** Tabulate commands, argument options, exact console outputs in English, and exit codes (`0`, `1`, `2`).
   - **Technical Decisions & Trade-offs:** For every major architectural or design choice, provide:
     - *Choice*
     - *Justification* (referencing constitution/spec)
     - *Discarded Alternative* and why it was rejected
   - **Testing Strategy:** Define the test pyramid, target test files, and a traceability matrix mapping each RF-x to automated test functions.

3. **Validate coverage.**
   - Verify that 100% of functional requirements (RF-1 through RF-N) are mapped to specific modules and tests.
   - Ensure zero runtime external dependencies (Python standard library only).

4. **Ask for approval.**
   - Do not begin writing code or generating tasks until the user has reviewed and approved the plan.

## Rules

- **NO CODE:** Do not generate production code during the planning phase.
- **Traceability:** Every module and test description must reference the RF-x it satisfies.
- **Justified decisions:** Never present a technical decision without explicitly stating the discarded alternative.
- **Language:** All documentation, comments, and CLI messages must be strictly in English.

