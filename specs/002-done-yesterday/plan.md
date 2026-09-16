# Architecture Plan — Mark Habit as Done Yesterday

## 1. Context and Objective
Provides the technical architecture and design for `specs/002-done-yesterday/spec.md`. The feature introduces an optional `--yesterday` / `-y` flag to the `habits done` command, allowing users to log completion for the previous calendar day without breaking their ongoing consistency streak.

This plan adheres to `docs/constitution.md`:
- Standard library only (`argparse`, `datetime`).
- Clean separation: core streak logic remains pure; CLI handles argument parsing and terminal I/O.
- Non-destructive JSON persistence and full error handling.
- All code, tests, and user-facing messages in English.

## 2. Component and Module Structure

```text
habits/
├── core.py      # No data model change; core functions already calculate streaks ending yesterday or today.
├── storage.py   # No schema change; completed_dates accepts any ISO YYYY-MM-DD date.
└── cli.py       # Update build_parser() for done command with --yesterday/-y flag, update handle_done() to resolve target date and print messages.
tests/
└── test_cli.py  # New CLI acceptance and unit tests for --yesterday flag, idempotency, error conditions, and output.
```

### Module Responsibilities:
- `habits/core.py` (Covers RF-6):
  - `calculate_streak(completed_dates, current_date)` already evaluates streaks ending on `current_date` or `current_date - 1 day`. No structural changes required; fully verified by existing and new tests.
- `habits/storage.py` (Covers RF-1, RF-7):
  - Storage format already persists `completed_dates` as `YYYY-MM-DD` strings. Handled transparently.
- `habits/cli.py` (Covers RF-1, RF-2, RF-3, RF-4, RF-5, RF-7):
  - Add `--yesterday` / `-y` (`action="store_true"`) to `done_parser`.
  - In `handle_done()`, determine target date (`date.today() - timedelta(days=1)` if `args.yesterday` else `date.today()`).
  - Output appropriate English messages (`Marked '<name>' as done for yesterday.` or `Habit '<name>' is already marked as done for yesterday.`).

## 3. Data Schema & Persistence (RF-1, RF-7)
The JSON schema remains 100% backward compatible (version 1). Completed dates are stored as ISO 8601 strings in `completed_dates`.

### Example Payload:
```json
{
  "version": 1,
  "habits": [
    {
      "name": "Study Python",
      "created_at": "2026-09-15",
      "completed_dates": [
        "2026-09-15",
        "2026-09-16"
      ]
    }
  ]
}
```

## 4. Key Algorithms & Edge Cases
### Command Dispatch Logic in `handle_done()`:
```text
1. Parse arguments:
   - If no name is provided: argparse automatically raises error, prints usage, exits with code 2 (RF-5).
   - Clean and normalize habit name. If name is empty/whitespace -> print error, return exit code 1 (RF-4).
2. Load habits from storage:
   - If storage is corrupted or unreadable -> print "Error: <reason>", return exit code 1 (RF-7).
3. Check habit existence:
   - If normalized key not in habits -> print "Error: Habit '<name>' not found. Use 'habits list' to see available habits.", return exit code 1 (RF-3).
4. Resolve target date (RF-1, atomic reference):
   - today = date.today()
   - target_date = today - timedelta(days=1) if args.yesterday else today
   - period_label = "yesterday" if args.yesterday else "today"
5. Idempotency Check (RF-2):
   - If target_date in habit.completed_dates:
       print(f"Habit '{habit.name}' is already marked as done for {period_label}.")
       return 0
6. Mutate and Save (RF-1, RF-7):
   - habit.completed_dates.add(target_date)
   - Save habits to storage. If save fails -> print "Error: <reason>", return exit code 1.
7. Confirmation Output (RF-1):
   - print(f"Marked '{habit.name}' as done for {period_label}.")
   - return 0
```

## 5. CLI & Interface Contracts

| Command | Arguments / Flags | Condition | Standard Output / Standard Error | Exit Code | RF Covered |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `habits done` | `<name> --yesterday` | Success (new) | stdout: `Marked '<name>' as done for yesterday.` | `0` | RF-1 |
| `habits done` | `<name> -y` | Success (new) | stdout: `Marked '<name>' as done for yesterday.` | `0` | RF-1 |
| `habits done` | `<name> --yesterday` | Already marked yesterday | stdout: `Habit '<name>' is already marked as done for yesterday.` | `0` | RF-2 |
| `habits done` | `<missing_name> -y` | Name not found | stderr: `Error: Habit '<name>' not found. Use 'habits list' to see available habits.` | `1` | RF-3 |
| `habits done` | `"" --yesterday` | Name is empty/spaces | stderr: `Error: Habit name cannot be empty.` | `1` | RF-4 |
| `habits done` | `--yesterday` | Missing name argument | stderr: `usage: habits done [-h] [-y] name [name ...]` | `2` | RF-5 |
| `habits list` | *(none)* | Yesterday marked, today pending | stdout: `- <name>: <streak> day(s) [pending]` | `0` | RF-6 |
| `habits done` | `<name> -y` | Corrupted storage file | stderr: `Error: ...` | `1` | RF-7 |

## 6. Technical Decisions and Rationale

- **Decision 1: Use `argparse` with `action="store_true"` for `--yesterday` and `-y`.**
  - *Rationale*: Native standard library parser supports both short and long options, handles flag position flexibility (before or after positional arguments), and formats help/syntax automatically.
  - *Discarded Alternative*: Custom manual parsing of `sys.argv`. Rejected because it introduces fragility, violates DRY, and requires manual edge case handling for `-h` and unknown flags.

- **Decision 2: Atomic `date.today()` evaluation in `handle_done`.**
  - *Rationale*: Evaluates `date.today()` once at the start of the handler to eliminate date shifts if execution spans across midnight.
  - *Discarded Alternative*: Calling `date.today()` multiple times in conditional branches. Rejected to prevent timing race conditions.

- **Decision 3: Reuse `calculate_streak` and `completed_dates` architecture without schema changes.**
  - *Rationale*: The MVP data model and domain core already treat dates as arbitrary historical `set[date]`. The streak calculation algorithm naturally bridges consecutive days regardless of the order they were inserted.
  - *Discarded Alternative*: Adding a separate `yesterday_completed` boolean flag to the habit data model. Rejected because it corrupts history tracking, prevents multi-day streaks, and violates the single source of truth for dates.

## 7. Testing Strategy & Traceability Matrix

### Test Pyramid:
- **CLI Acceptance & Integration Tests (`tests/test_cli.py`)**: End-to-end command invocations via `main()`, validating stdout/stderr, exit codes, and JSON persistence.
- **Core Domain Tests (`tests/test_core.py`)**: Streak calculation continuity when yesterday is marked and today is pending.

| Requirement | Test Function / Case | File | Description |
| :--- | :--- | :--- | :--- |
| **RF-1** | `test_done_yesterday_success` | `tests/test_cli.py` | Verifies `habits done <name> --yesterday` & `-y` marks yesterday, prints confirmation, exit code 0. |
| **RF-2** | `test_done_yesterday_idempotent` | `tests/test_cli.py` | Verifies second call prints already marked message, exit code 0, no duplicate dates. |
| **RF-3** | `test_done_yesterday_nonexistent_habit` | `tests/test_cli.py` | Verifies unknown habit prints not found error to stderr, exit code 1. |
| **RF-4** | `test_done_yesterday_empty_name` | `tests/test_cli.py` | Verifies empty/whitespace name prints error, exit code 1. |
| **RF-5** | `test_done_yesterday_missing_name_arg` | `tests/test_cli.py` | Verifies omitting name prints usage to stderr, exit code 2. |
| **RF-6** | `test_streak_with_yesterday_and_pending_today` | `tests/test_core.py` & `test_cli.py` | Verifies streak is preserved and `habits list` shows `[pending]` for today. |
| **RF-7** | `test_done_yesterday_corrupted_storage` | `tests/test_cli.py` | Verifies corrupted JSON file yields exit code 1 without altering or destroying the file. |
