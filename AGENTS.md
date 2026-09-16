# AGENTS.md — habits-cli-sdd

## Project
Python CLI to track study habits and calculate consecutive-day streaks.
Pure domain core (`habits/core.py`) + CLI presentation layer (`habits/cli.py`).
Local JSON persistence (`habits/storage.py`).

## Commands
- Run: `python -m habits <command>`
- Tests: `pytest -q`

## Style
- Python 3.12+, type hints on all public functions.
- Standard library only (pytest solely for testing).
- Everything in English: identifiers, code, tests, documentation, and user messages.

## Rules
- **Strict context isolation:** Forbidden to read, list, search, or reference any file or directory outside the `habits-cli/` directory. Treat `habits-cli/` as the absolute and hermetic project root.
- Read `docs/constitution.md` and the active spec in `specs/` before touching code.
- Do not add dependencies or modify the JSON format without updating the spec first.
- Do not modify files in `specs/` unless explicitly requested.

## When Finishing Any Task
- Run `pytest -q` and confirm in your response that all tests pass.