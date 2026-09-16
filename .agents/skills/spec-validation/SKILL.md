---
name: spec-validation
description: Use this skill to validate an implemented feature against its specification (spec.md), checking requirements RF-by-RF against automated tests, verifying completion criteria, and delivering a pass/fail verdict.
---

# Spec Validation

Audits an implemented feature specification against the actual automated test suite to ensure 100% test coverage and compliance with all criteria.

## Process
1. **Read Active Specification**:
   - Locate `specs/<feature>/spec.md` and extract all functional requirements (`RF-1` to `RF-N`) and the `Completion Criteria` section.
2. **Requirement-by-Requirement Verification**:
   - For every single `RF-x`, identify:
     - The exact test file and test function covering it.
     - The execution status of that test.
   - Explicitly flag any uncovered or failing requirement.
3. **Completion Criteria Check**:
   - Verify that all conditions listed under `Completion Criteria` in `spec.md` are satisfied (e.g. green test suite, error code adherence, CLI smoke tests).
4. **Final Verdict**:
   - Run `pytest -q` across the entire project test suite.
   - Deliver an unambiguous verdict: **Spec Fulfilled** (PASS) or **Spec Not Fulfilled** (FAIL) with supporting rationale.

