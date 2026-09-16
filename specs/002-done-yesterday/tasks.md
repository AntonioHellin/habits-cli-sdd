# Tasks: Mark Habit as Done Yesterday

Feature Spec: `specs/002-done-yesterday/spec.md`  
Architecture Plan: `specs/002-done-yesterday/plan.md`

## Task List

- [ ] **T1: Core streak behavior verification for yesterday-only completion**
  - **Type**: Core / Test
  - **Covers**: RF-6
  - **Description**: Add unit test in `tests/test_core.py` ensuring that a habit completed yesterday but pending today yields an active streak of 1 (or connects to prior consecutive days) and confirms `is_done_today` returns False.
  - **Test First**: Write `test_streak_yesterday_completed_today_pending` in `tests/test_core.py`.
  - **Implementation**: Verify pure function `calculate_streak` handles this seamlessly without modifying core logic.
  - **Done when**: `pytest tests/test_core.py -k test_streak_yesterday_completed_today_pending` passes.

- [ ] **T2: CLI argument parser support for `--yesterday` and `-y`**
  - **Type**: CLI / Test
  - **Covers**: RF-1, RF-5
  - **Description**: Add `--yesterday` / `-y` flag to `done` subcommand parser in `habits/cli.py` (`action="store_true"`). Ensure missing name arguments trigger exit code 2.
  - **Test First**: Write test in `tests/test_cli.py` testing parser recognizing `-y` and `--yesterday`, and failing with exit code 2 when name argument is missing.
  - **Implementation**: Update `build_parser()` in `habits/cli.py` with `done_parser.add_argument("-y", "--yesterday", action="store_true", help="Mark habit as done for yesterday")`.
  - **Done when**: `pytest tests/test_cli.py -k test_done_parser_flags` passes.

- [ ] **T3: CLI command execution for marking yesterday (RF-1 & RF-2)**
  - **Type**: CLI / Test
  - **Covers**: RF-1, RF-2
  - **Description**: Update `handle_done` in `habits/cli.py` to evaluate target date as `date.today() - timedelta(days=1)` when `--yesterday` is present, record completion in storage, print `Marked '<name>' as done for yesterday.` on success (exit code 0), and print `Habit '<name>' is already marked as done for yesterday.` if already completed (exit code 0).
  - **Test First**: Write tests in `tests/test_cli.py`: `test_done_yesterday_success` and `test_done_yesterday_idempotent`.
  - **Implementation**: Implement target date resolution and specific message formatting in `handle_done()`.
  - **Done when**: `pytest tests/test_cli.py -k "test_done_yesterday_success or test_done_yesterday_idempotent"` passes.

- [ ] **T4: CLI error handling and non-functional requirements (RF-3, RF-4, RF-7)**
  - **Type**: CLI / Test
  - **Covers**: RF-3, RF-4, RF-7
  - **Description**: Verify error handling with `--yesterday` flag: non-existent habit (exit code 1), empty/whitespace habit name (exit code 1), and corrupted storage file (exit code 1, file preserved).
  - **Test First**: Write test cases in `tests/test_cli.py` covering error flows for `habits done <name> --yesterday`.
  - **Implementation**: Ensure error paths in `handle_done()` properly pass through `StorageError` and clean validation errors.
  - **Done when**: `pytest tests/test_cli.py -k "test_done_yesterday_errors"` passes.

- [ ] **T5: Full integration verification and list display (RF-6)**
  - **Type**: Integration / Test
  - **Covers**: RF-1 through RF-7
  - **Description**: End-to-end test verifying full user journey: create habit -> mark done for yesterday with `-y` -> run `habits list` and verify streak shows `1 day(s) [pending]`.
  - **Test First**: Write integration test in `tests/test_cli.py`: `test_e2e_done_yesterday_and_list`.
  - **Implementation**: Verify seamless end-to-end integration across all commands.
  - **Done when**: `pytest -q` runs all tests (existing + new) and 100% pass green.
