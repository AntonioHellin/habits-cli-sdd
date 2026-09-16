# Plan 001 — habits-cli-sdd MVP Architecture and Implementation Plan

## Overview and Objectives
This plan outlines the technical design, module decomposition, data persistence model, CLI contract, and test strategy for the initial MVP of `habits-cli-sdd`. The design strictly complies with the project's [constitution](file:///e:/_Documents/Programming/dev/hello-sdd-main/habits-cli/docs/constitution.md) and addresses all functional requirements in [spec.md](file:///e:/_Documents/Programming/dev/hello-sdd-main/habits-cli/specs/001-habits-mvp/spec.md) (RF-1 through RF-12).

---

## 1. Module Structure and Responsibilities
The codebase follows a 3-tier decoupled architecture keeping domain logic pure, storage encapsulated, and the CLI as a presentation layer.

```
habits-cli/
├── habits/
│   ├── __init__.py       # Package marker and version (__version__ = "0.1.0")
│   ├── __main__.py       # CLI invocation entry point for `python -m habits`
│   ├── core.py           # Pure domain models, streak calculation, business rules
│   ├── storage.py        # JSON file persistence, atomic writes, error handling
│   └── cli.py            # Argparse CLI interface, output formatting, exit codes
└── tests/
    ├── __init__.py
    ├── test_core.py      # Unit tests for domain logic and streak algorithm
    ├── test_storage.py   # Unit & integration tests for JSON persistence and error cases
    └── test_cli.py       # End-to-end CLI tests verifying stdout/stderr and exit codes
```

### Module Breakdown
- **`habits/core.py`**
  - Contains domain dataclass `Habit`.
  - Implements pure functions: `normalize_habit_name`, `calculate_streak`, `is_done_today`, and `sort_habits`.
  - **Zero dependencies on `sys`, `print`, `argparse`, or filesystem I/O.**
  - *Covers:* RF-1, RF-2, RF-3, RF-4, RF-5, RF-7, RF-9.

- **`habits/storage.py`**
  - Manages loading and saving habit records to a single local JSON file.
  - Resolves storage path via `HABITS_FILE` environment variable (defaulting to `~/.habits.json`).
  - Detects malformed JSON and I/O failures, raising structured exceptions (`StorageError`) without destroying existing files.
  - *Covers:* RF-10, RF-11.

- **`habits/cli.py`**
  - Implements the command-line parser using Python's standard `argparse`.
  - Subcommands: `add`, `done`, `list`.
  - Formats all console messages in English and returns appropriate exit codes (0 for success, 1 for user/business error, 2 for parser syntax error).
  - *Covers:* RF-1, RF-2, RF-3, RF-4, RF-5, RF-6, RF-7, RF-8, RF-12.

- **`habits/__main__.py`**
  - Calls `cli.main()` and forwards its return code to `sys.exit()`.
  - Enables execution via `python -m habits <command>`.

---

## 2. JSON Data Model and Persistence Format
Persistence uses a single human-readable JSON file. The top-level object includes a `schema_version` to support future non-breaking migrations and a dictionary of habits keyed by normalized (lowercased) name for $O(1)$ collision and retrieval.

### JSON Schema
```json
{
  "schema_version": 1,
  "habits": {
    "read documentation": {
      "name": "Read Documentation",
      "created_at": "2026-09-10",
      "completed_dates": [
        "2026-09-13",
        "2026-09-14",
        "2026-09-15"
      ]
    },
    "python practice": {
      "name": "Python Practice",
      "created_at": "2026-09-15",
      "completed_dates": []
    }
  }
}
```

### Field Definitions
- `schema_version` (integer): Version identifier for the storage structure.
- `habits` (object): Map of `<normalized_key>` -> `<habit_record>`.
  - `name` (string): Preserved original display casing as entered by the user.
  - `created_at` (string, ISO `YYYY-MM-DD`): Date the habit was created.
  - `completed_dates` (array of strings, ISO `YYYY-MM-DD`): Unique, sorted dates on which the habit was completed.

*Covers:* RF-9, RF-10, RF-11.

---

## 3. Streak Calculation Algorithm (Pseudocode)

```python
FUNCTION calculate_streak(completed_dates: Set[Date], current_date: Date) -> Integer:
    """
    Computes consecutive active days ending today or yesterday.
    Future dates relative to current_date are ignored.
    """
    IF completed_dates IS EMPTY:
        RETURN 0

    # Filter out any future dates
    valid_dates = {d FOR d IN completed_dates IF d <= current_date}
    IF valid_dates IS EMPTY:
        RETURN 0

    yesterday = current_date - 1 day

    # If completed neither today nor yesterday, the streak is broken
    IF (current_date NOT IN valid_dates) AND (yesterday NOT IN valid_dates):
        RETURN 0

    # Start checking backwards from current_date if done today, else from yesterday
    check_date = current_date IF current_date IN valid_dates ELSE yesterday
    streak = 0

    WHILE check_date IN valid_dates:
        streak = streak + 1
        check_date = check_date - 1 day

    RETURN streak
```

### Edge Case Trace
1. **Never completed (`completed_dates == []`)**: returns `0`.
2. **Completed today only**: `check_date = current_date`, loops once, returns `1`.
3. **Completed yesterday only**: `current_date NOT IN valid_dates`, `yesterday IN valid_dates`, `check_date = yesterday`, loops once, returns `1` (streak maintained today).
4. **Completed today, yesterday, and day before**: `check_date = current_date`, decrements 3 times, returns `3`.
5. **Completed 2 days ago, but missed yesterday and today**: `current_date` and `yesterday` not in set -> returns `0`.
6. **Future date in file (e.g. tomorrow due to clock sync)**: filtered out by `d <= current_date`, does not artificially inflate streak.

*Covers:* RF-9.

---

## 4. CLI Contract

### General Invocation
- Entry command: `python -m habits <subcommand> [args]`
- Missing subcommand or unknown argument: prints usage help to `stderr` and exits with code `2` (*RF-12*).

### Subcommands Specification

| Command | Arguments | Condition | Output Message | Exit Code | RF |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `habits add` | `<name...>` | Success (non-empty, non-existing) | `Habit '<name>' created successfully.` | `0` | RF-1 |
| `habits add` | `<name...>` | Name already exists (case-insensitive) | `Error: Habit '<name>' already exists.` | `1` | RF-2 |
| `habits add` | (empty / whitespace) | Empty or whitespace name | `Error: Habit name cannot be empty.` | `1` | RF-3 |
| `habits done` | `<name...>` | Success (habit exists, not done today) | `Marked '<name>' as done for today.` | `0` | RF-4 |
| `habits done` | `<name...>` | Idempotent (already marked today) | `Habit '<name>' is already marked as done for today.` | `0` | RF-5 |
| `habits done` | `<name...>` | Habit not found (case-insensitive) | `Error: Habit '<name>' not found. Use 'habits list' to see available habits.` | `1` | RF-6 |
| `habits list` | (none) | Habits exist in storage | `- <Name>: <N> day(s) [<done today\|pending>]` (sorted) | `0` | RF-7 |
| `habits list` | (none) | Zero habits exist in storage | `No habits registered yet. Create your first habit with 'habits add <name>'.` | `0` | RF-8 |

### Multi-word Argument Support
- Defined as `parser.add_argument("name", nargs="+", help="Habit name")`.
- Parsed via `" ".join(args.name).strip()`. Handles `habits add read book` identically to `habits add "read book"`.

### Global Error Handling
- **Corrupted JSON file or Permission Denied:**
  - Standard error message: `Error: Storage failure: <details>. Data file was not modified.`
  - Exit code: `1` (*RF-11*).

---

## 5. Technical Decisions and Justifications

### Decision 1: Standard Library Only (Argparse, JSON, Dataclasses)
- **Choice:** Rely exclusively on standard library modules (`argparse`, `json`, `dataclasses`, `pathlib`, `datetime`).
- **Justification:** Complies with Constitution Principle 1 (simplicity) and Principle 5. Eliminates runtime packaging friction and allows junior developers to run the tool out of the box on any machine with Python 3.12+.
- **Discarded Alternative:** Using third-party frameworks like `click` or `typer` + `rich`. Discarded because external dependencies introduce version drift, complex typing abstractions, and violate the constitutional constraint of zero runtime dependencies.

### Decision 2: 3-Layer Decoupled Architecture
- **Choice:** Strict separation between pure domain logic (`core.py`), file I/O (`storage.py`), and CLI presentation (`cli.py`).
- **Justification:** Complies with Constitution Principle 3. Business logic (such as streak calculation and normalization) can be exhaustively tested in isolation in milliseconds without mocking terminal standard streams or disk files.
- **Discarded Alternative:** Single-file script or Active-Record style models handling their own serialization and printing. Discarded because it tightly couples I/O with logic, impeding unit testing and violating separation of concerns.

### Decision 3: JSON Storage with Environment Variable Override
- **Choice:** Single local JSON file defaulting to `~/.habits.json`, configurable via the `HABITS_FILE` environment variable.
- **Justification:** Complies with Constitution Principle 5 (transparent, human-readable, no database). The environment variable allows test suites (`pytest`) to point to isolated temporary directories (`tmp_path`) seamlessly without touching user data.
- **Discarded Alternative:** SQLite database or pickled binary files. Discarded because SQLite is opaque to direct inspection with a text editor, while pickle introduces security risks and is binary.

### Decision 4: Dual Keying for Habit Names (Normalized Key + Display Name)
- **Choice:** Key the internal storage map by `name.strip().lower()`, but store the user's original casing in `Habit.name`.
- **Justification:** Guarantees $O(1)$ case-insensitive uniqueness checks and lookup while respecting how the user capitalized their habit when displaying it in `habits list`.
- **Discarded Alternative:** Strictly case-sensitive lookup. Discarded because having both `"Python"` and `"python"` leads to severe user confusion in command-line environments.

### Decision 5: Calendar Day Traversal for Streak Calculation
- **Choice:** Step backward day-by-day from today/yesterday while checking date existence in a set.
- **Justification:** $O(S)$ where $S$ is the streak count in days (typically small). It is completely immune to out-of-order data, duplicate completions, and leap years.
- **Discarded Alternative:** Sorting dates array and computing day deltas (`date[i] - date[i-1] == 1`). Discarded because date gaps, duplicate entries on the same day, and boundary conditions make sorting algorithms more error-prone for junior maintenance.

---

## 6. Testing Strategy

Testing is the gatekeeper of quality (Constitution Principle 4). Development will use `pytest` as the sole testing dependency.

### Test Directory Layout
```
tests/
├── test_core.py      # Unit tests: pure logic & algorithms
├── test_storage.py   # Unit/integration tests: JSON serialization and file errors
└── test_cli.py       # Acceptance/CLI tests: command invocations, outputs, and exit codes
```

### Coverage Matrix (Requirements to Tests)

| Test Module | Test Functions | Covered Requirements |
| :--- | :--- | :--- |
| `test_core.py` | `test_normalize_habit_name()` | RF-2, RF-3 |
| `test_core.py` | `test_calculate_streak_empty()` | RF-9 |
| `test_core.py` | `test_calculate_streak_today_only()` | RF-9 |
| `test_core.py` | `test_calculate_streak_yesterday_only()` | RF-9 |
| `test_core.py` | `test_calculate_streak_consecutive_days()` | RF-9 |
| `test_core.py` | `test_calculate_streak_broken_gap()` | RF-9 |
| `test_core.py` | `test_calculate_streak_ignores_future_dates()` | RF-9 |
| `test_core.py` | `test_sort_habits_by_streak_and_name()` | RF-7 |
| `test_storage.py`| `test_load_non_existent_file_initializes_empty()` | RF-10 |
| `test_storage.py`| `test_save_and_load_round_trip()` | RF-10 |
| `test_storage.py`| `test_load_corrupted_json_raises_storage_error()` | RF-11 |
| `test_storage.py`| `test_storage_error_does_not_overwrite_file()` | RF-11 |
| `test_cli.py` | `test_cli_add_habit_success()` | RF-1 |
| `test_cli.py` | `test_cli_add_habit_duplicate_conflict()` | RF-2 |
| `test_cli.py` | `test_cli_add_habit_empty_name()` | RF-3 |
| `test_cli.py` | `test_cli_add_habit_multi_word()` | RF-1 |
| `test_cli.py` | `test_cli_done_habit_success()` | RF-4 |
| `test_cli.py` | `test_cli_done_habit_already_done_today()` | RF-5 |
| `test_cli.py` | `test_cli_done_habit_not_found()` | RF-6 |
| `test_cli.py` | `test_cli_list_habits_empty()` | RF-8 |
| `test_cli.py` | `test_cli_list_habits_formatted_and_sorted()` | RF-7 |
| `test_cli.py` | `test_cli_storage_corruption_exits_with_error()`| RF-11 |
| `test_cli.py` | `test_cli_missing_or_unknown_command()` | RF-12 |

### Quality Gate Rule
- Every development task will practice test-first implementation.
- All tests must pass cleanly (`pytest -q`) before completing any task. Zero failing tests permitted.
