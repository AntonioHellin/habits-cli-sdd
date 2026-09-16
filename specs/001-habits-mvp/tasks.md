# Tasks 001 — habits-cli-sdd MVP Implementation Tasks

This document defines the incremental, test-first task breakdown for implementing `habits-cli-sdd`. Each task is scoped to approximately 20–30 minutes, organized in dependency order, maps directly to functional requirements (RF), and features a concrete, verifiable completion criterion.

---

## Task List

- [x] **T1: Project Skeleton, Packaging, and Test Setup**
  - **Covers:** Constitution Principle 1 & 4 (Python 3.12+, standard library, pytest setup)
  - **Scope:**
    - Create `pyproject.toml` configuring pytest and project metadata.
    - Set up package structure: `habits/__init__.py`, `habits/__main__.py`, and `tests/__init__.py`.
    - Add a baseline smoke test in `tests/test_smoke.py`.
  - **Done when:** Running `pytest -q` executes without errors and passes the baseline smoke test.

- [x] **T2: Domain Model and Habit Name Normalization**
  - **Covers:** RF-2, RF-3
  - **Scope:**
    - In `habits/core.py`, define the `Habit` domain dataclass (`name`, `created_at`, `completed_dates`).
    - Implement pure function `normalize_habit_name(name: str) -> str` (stripping whitespace, validating non-empty).
    - Raise `ValueError` on empty or whitespace-only names.
    - Write unit tests in `tests/test_core.py` covering case normalization, whitespace trimming, and rejection of invalid names.
  - **Done when:** `pytest -q tests/test_core.py` passes all unit tests for name normalization and validation.

- [x] **T3: Streak Calculation Algorithm and Sorting Logic**
  - **Covers:** RF-7, RF-9
  - **Scope:**
    - In `habits/core.py`, implement `calculate_streak(completed_dates: set[date], current_date: date) -> int`.
    - Implement helper functions `is_done_today(completed_dates: set[date], current_date: date) -> bool` and `sort_habits(habits: list[Habit], current_date: date) -> list[tuple[Habit, int, bool]]`.
    - Write unit tests in `tests/test_core.py` covering all streak cases: zero completions, completed today only (1), completed yesterday only (1), consecutive days (N), broken streak (>1 day gap returns 0), future dates ignored, and case-insensitive secondary sorting.
  - **Done when:** `pytest -q tests/test_core.py` passes all streak computation and sorting test cases.

- [x] **T4: JSON Persistence, File Resolution, and Storage Error Handling**
  - **Covers:** RF-10, RF-11
  - **Scope:**
    - In `habits/storage.py`, implement `get_storage_path() -> Path` with `HABITS_FILE` environment variable support (defaulting to `~/.habits.json`).
    - Implement `load_habits(path: Path) -> dict[str, Habit]` returning an empty dict if the file does not exist.
    - Implement `save_habits(path: Path, habits: dict[str, Habit]) -> None` with atomic file writing.
    - Define `StorageError` exception and ensure corrupted JSON or I/O access errors raise `StorageError` without modifying/destroying the existing file.
    - Write tests in `tests/test_storage.py` covering round-trip serialization, missing file handling, and corrupted file protection.
  - **Done when:** `pytest -q tests/test_storage.py` passes all tests for JSON persistence and fail-safe error handling.

- [x] **T5: CLI Command — Add Habit (`habits add`)**
  - **Covers:** RF-1, RF-2, RF-3
  - **Scope:**
    - In `habits/cli.py`, configure `argparse` with the `add` subcommand supporting multi-word arguments (`nargs="+"`).
    - Implement handler for `add`: validate name, check for existing duplicates case-insensitively, persist new habit via `storage.py`, and print confirmation.
    - Return exit code `0` on success; exit code `1` with descriptive error on duplicate conflict or empty name.
    - Write acceptance tests in `tests/test_cli.py` for `add` success, multi-word names, duplicates, and empty input.
  - **Done when:** `pytest -q tests/test_cli.py -k add` passes all tests verifying exit codes, messages, and persistence.

- [x] **T6: CLI Command — Mark Habit Done (`habits done`)**
  - **Covers:** RF-4, RF-5, RF-6
  - **Scope:**
    - In `habits/cli.py`, implement the `done` subcommand with multi-word support.
    - Match habit case-insensitively and record today's date (`date.today()`).
    - If already completed today, inform the user idempotently without duplicating dates and exit with code `0`.
    - If habit does not exist, display error suggesting `habits list` and exit with code `1`.
    - Write acceptance tests in `tests/test_cli.py` for completion, idempotency, and unknown habit errors.
  - **Done when:** `pytest -q tests/test_cli.py -k done` passes all tests verifying completion behavior and exit codes.

- [x] **T7: CLI Command — List Habits and Streaks (`habits list`)**
  - **Covers:** RF-7, RF-8
  - **Scope:**
    - In `habits/cli.py`, implement the `list` subcommand.
    - If storage has no habits, output the empty state message inviting the user to create the first habit (exit code `0`).
    - If habits exist, display sorted items formatted as `- <Name>: <N> day(s) [<done today|pending>]` (exit code `0`).
    - Write acceptance tests in `tests/test_cli.py` for empty and populated listings.
  - **Done when:** `pytest -q tests/test_cli.py -k list` passes all tests verifying output formatting, sorting, and status tags.

- [x] **T8: Global CLI Error Handling and End-to-End Suite Validation**
  - **Covers:** RF-11, RF-12, Definition of Done
  - **Scope:**
    - Connect `habits/__main__.py` to invoke `cli.main()`.
    - Handle missing subcommands and invalid arguments with usage instructions (exit code `2`).
    - Catch `StorageError` at the CLI boundary, printing error to stderr and exiting with code `1`.
    - Add an end-to-end integration test executing the complete user journey: `add` -> `done` -> `list`.
    - Execute the entire test suite and verify clean output.
  - **Done when:** `pytest -q` runs the complete test suite with 100% green tests and zero failures.
