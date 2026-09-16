# Architecture Plan — [Feature Name]

## 1. Context and Objective
[Brief explanation of the feature, referencing `specs/<N>-<name>/spec.md` and `docs/constitution.md`.]

## 2. Component and Module Structure
[Describe affected modules and classes/functions, e.g., `habits/core.py`, `habits/storage.py`, `habits/cli.py`.]

```
habits/
├── core.py      # [Changes or additions]
├── storage.py   # [Changes or additions]
└── cli.py       # [Changes or additions]
```

## 3. Data Schema & Persistence (if applicable)
[JSON schema or structure updates with example payload. Highlight backward compatibility.]

```json
{
  "version": 1,
  "habits": []
}
```

## 4. Key Algorithms & Edge Cases
[Pseudocode or step-by-step logic for non-trivial domain rules and edge cases.]

## 5. CLI & Interface Contracts
[Tables documenting CLI commands, options, outputs, exit codes, and errors.]

| Command | Argument / Flag | Description | Expected Output / Exit Code |
| :--- | :--- | :--- | :--- |
| `habits <cmd>` | `--flag` | Description | Standard output / `0` |

## 6. Technical Decisions and Rationale
[Explain key design decisions, including trade-offs and discarded alternatives.]

- **Decision 1**: [Description]
  - *Rationale*: [Why this approach was chosen]
  - *Alternatives considered*: [Why other options were rejected]

## 7. Testing Strategy & Traceability Matrix
[Map 100% of requirements (RF-*) to planned unit and integration tests.]

| Requirement | Test File / Case | Description |
| :--- | :--- | :--- |
| RF-1 | `tests/test_core.py::...` | Verifies ... |
| RF-2 | `tests/test_cli.py::...` | Verifies ... |
