"""Acceptance and CLI tests for habits.cli command interface."""

from datetime import date
from pathlib import Path
import pytest

from habits.cli import main
from habits.storage import load_habits


@pytest.fixture
def temp_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolate storage to a temporary file for CLI tests."""
    storage_file = tmp_path / "habits_test.json"
    monkeypatch.setenv("HABITS_FILE", str(storage_file))
    return storage_file


def test_cli_add_habit_success(temp_storage: Path, capsys: pytest.CaptureFixture) -> None:
    """Verify adding a valid habit creates it, prints confirmation, and exits with 0 (RF-1)."""
    exit_code = main(["add", "Study", "Python"])
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "Habit 'Study Python' created successfully." in captured.out

    habits = load_habits(temp_storage)
    assert "study python" in habits
    assert habits["study python"].name == "Study Python"


def test_cli_add_habit_quoted_multi_word(temp_storage: Path, capsys: pytest.CaptureFixture) -> None:
    """Verify adding a habit as a single quoted argument works properly (RF-1)."""
    exit_code = main(["add", "Read Documentation"])
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "Habit 'Read Documentation' created successfully." in captured.out

    habits = load_habits(temp_storage)
    assert "read documentation" in habits


def test_cli_add_habit_duplicate_conflict(temp_storage: Path, capsys: pytest.CaptureFixture) -> None:
    """Verify adding duplicate name (case-insensitive) fails with code 1 (RF-2)."""
    exit_code_1 = main(["add", "Exercise Daily"])
    assert exit_code_1 == 0

    # Attempt to add same habit with different casing and extra spaces
    exit_code_2 = main(["add", "  exercise", "DAILY  "])
    assert exit_code_2 == 1

    captured = capsys.readouterr()
    assert "Error: Habit 'exercise DAILY' already exists." in captured.err


def test_cli_add_habit_empty_or_whitespace_name(temp_storage: Path, capsys: pytest.CaptureFixture) -> None:
    """Verify adding empty or whitespace-only name fails with code 1 (RF-3)."""
    exit_code = main(["add", "   "])
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Error: Habit name cannot be empty." in captured.err


# ============================================================================
# Tests for `habits done` (T6: RF-4, RF-5, RF-6)
# ============================================================================


def test_cli_done_habit_success(temp_storage: Path, capsys: pytest.CaptureFixture) -> None:
    """Verify marking habit done registers today's date and exits with 0 (RF-4)."""
    main(["add", "Study", "Python"])
    capsys.readouterr()

    exit_code = main(["done", "study", "python"])
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "Marked 'Study Python' as done for today." in captured.out

    habits = load_habits(temp_storage)
    assert date.today() in habits["study python"].completed_dates


def test_cli_done_habit_already_done_today(temp_storage: Path, capsys: pytest.CaptureFixture) -> None:
    """Verify marking habit done twice on the same day is idempotent (RF-5)."""
    main(["add", "Read Docs"])
    main(["done", "Read Docs"])
    capsys.readouterr()

    exit_code = main(["done", "read docs"])
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "Habit 'Read Docs' is already marked as done for today." in captured.out

    habits = load_habits(temp_storage)
    assert len(habits["read docs"].completed_dates) == 1


def test_cli_done_habit_not_found(temp_storage: Path, capsys: pytest.CaptureFixture) -> None:
    """Verify marking a non-existent habit reports error suggesting 'habits list' and exits with 1 (RF-6)."""
    exit_code = main(["done", "Nonexistent Habit"])
    assert exit_code == 1

    captured = capsys.readouterr()
    assert (
        "Error: Habit 'Nonexistent Habit' not found. Use 'habits list' to see available habits."
        in captured.err
    )


def test_cli_done_habit_empty_name(temp_storage: Path, capsys: pytest.CaptureFixture) -> None:
    """Verify passing empty string to done results in error with code 1."""
    exit_code = main(["done", "   "])
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Error: Habit name cannot be empty." in captured.err


# ============================================================================
# Tests for `habits list` (T7: RF-7, RF-8)
# ============================================================================


def test_cli_list_habits_empty(temp_storage: Path, capsys: pytest.CaptureFixture) -> None:
    """Verify empty list outputs helpful invitation message and exits with 0 (RF-8)."""
    exit_code = main(["list"])
    assert exit_code == 0

    captured = capsys.readouterr()
    assert (
        "No habits registered yet. Create your first habit with 'habits add <name>'."
        in captured.out
    )


def test_cli_list_habits_formatted_and_sorted(temp_storage: Path, capsys: pytest.CaptureFixture) -> None:
    """Verify list outputs habits with formatted streaks, today's status, and proper sorting (RF-7)."""
    today = date.today()
    from datetime import timedelta
    from habits.core import Habit
    from habits.storage import save_habits

    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)

    h1 = Habit(name="Read Documentation", created_at=today, completed_dates={today, yesterday, two_days_ago})  # streak 3, done today
    h2 = Habit(name="Python Practice", created_at=today, completed_dates=set())  # streak 0, pending
    h3 = Habit(name="Algorithms", created_at=today, completed_dates={today})  # streak 1, done today
    h4 = Habit(name="gym workout", created_at=today, completed_dates={yesterday})  # streak 1, pending

    save_habits(temp_storage, {h.key: h for h in [h1, h2, h3, h4]})

    exit_code = main(["list"])
    assert exit_code == 0

    captured = capsys.readouterr()
    lines = [line.strip() for line in captured.out.strip().splitlines()]

    # Expected order:
    # 1. Read Documentation: 3 day(s) [done today]
    # 2. Algorithms: 1 day(s) [done today]
    # 3. gym workout: 1 day(s) [pending]
    # 4. Python Practice: 0 day(s) [pending]
    assert len(lines) == 4
    assert lines[0] == "- Read Documentation: 3 day(s) [done today]"
    assert lines[1] == "- Algorithms: 1 day(s) [done today]"
    assert lines[2] == "- gym workout: 1 day(s) [pending]"
    assert lines[3] == "- Python Practice: 0 day(s) [pending]"


# ============================================================================
# Tests for Global Error Handling & E2E Validation (T8: RF-11, RF-12)
# ============================================================================


def test_cli_missing_subcommand_prints_help_and_exits_2(capsys: pytest.CaptureFixture) -> None:
    """Verify running habits without arguments prints usage to stderr and exits with code 2 (RF-12)."""
    exit_code = main([])
    assert exit_code == 2

    captured = capsys.readouterr()
    assert "usage: habits" in captured.err


def test_cli_unrecognized_command_exits_code_2(capsys: pytest.CaptureFixture) -> None:
    """Verify unrecognized command exits with code 2 (RF-12)."""
    with pytest.raises(SystemExit) as exc_info:
        main(["unknown_cmd"])
    assert exc_info.value.code == 2

    captured = capsys.readouterr()
    assert "invalid choice: 'unknown_cmd'" in captured.err


def test_cli_storage_error_failsafe_preserves_corrupted_file(
    temp_storage: Path, capsys: pytest.CaptureFixture
) -> None:
    """Verify StorageError returns exit code 1 without destroying existing file (RF-11)."""
    corrupt_data = "{ this is not valid json"
    temp_storage.write_text(corrupt_data, encoding="utf-8")

    # Verify add exits with 1
    assert main(["add", "Test Habit"]) == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err

    # Verify done exits with 1
    assert main(["done", "Test Habit"]) == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err

    # Verify list exits with 1
    assert main(["list"]) == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err

    # Verify file was never modified or destroyed
    assert temp_storage.read_text(encoding="utf-8") == corrupt_data


def test_main_module_delegates_to_cli_main(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify habits.__main__.main() calls and forwards exit code from habits.cli.main()."""
    import habits.__main__

    monkeypatch.setattr("habits.cli.main", lambda argv=None: 42)
    assert habits.__main__.main() == 42


def test_cli_e2e_complete_workflow(temp_storage: Path, capsys: pytest.CaptureFixture) -> None:
    """End-to-end user journey test: list (empty) -> add -> list -> done -> list -> duplicate done."""
    # 1. List on empty storage
    assert main(["list"]) == 0
    out1 = capsys.readouterr().out
    assert "No habits registered yet" in out1

    # 2. Add first habit
    assert main(["add", "Study", "Python"]) == 0
    out2 = capsys.readouterr().out
    assert "Habit 'Study Python' created successfully." in out2

    # 3. Add second habit
    assert main(["add", "Daily Reading"]) == 0
    out3 = capsys.readouterr().out
    assert "Habit 'Daily Reading' created successfully." in out3

    # 4. List shows both pending with 0 streak
    assert main(["list"]) == 0
    out4 = capsys.readouterr().out
    assert "- Daily Reading: 0 day(s) [pending]" in out4
    assert "- Study Python: 0 day(s) [pending]" in out4

    # 5. Mark Study Python as done
    assert main(["done", "study", "python"]) == 0
    out5 = capsys.readouterr().out
    assert "Marked 'Study Python' as done for today." in out5

    # 6. List shows Study Python done today with 1 streak, Daily Reading still pending
    assert main(["list"]) == 0
    out6 = capsys.readouterr().out
    lines = [line.strip() for line in out6.strip().splitlines()]
    assert lines[0] == "- Study Python: 1 day(s) [done today]"
    assert lines[1] == "- Daily Reading: 0 day(s) [pending]"

    # 7. Repeat done on Study Python is idempotent
    assert main(["done", "Study Python"]) == 0
    out7 = capsys.readouterr().out
    assert "Habit 'Study Python' is already marked as done for today." in out7

    # 8. Mark unknown habit reports error
    assert main(["done", "Cook Dinner"]) == 1
    err8 = capsys.readouterr().err
    assert "Error: Habit 'Cook Dinner' not found. Use 'habits list' to see available habits." in err8
