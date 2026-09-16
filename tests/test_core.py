"""Unit tests for habits.core domain models, normalization, streak calculation, and sorting."""

from datetime import date, timedelta
import pytest

from habits.core import (
    Habit,
    calculate_streak,
    clean_habit_name,
    is_done_today,
    normalize_habit_name,
    sort_habits,
)


def test_normalize_habit_name_valid() -> None:
    """Verify that habit names are lowercased and stripped of leading/trailing spaces."""
    assert normalize_habit_name("Python") == "python"
    assert normalize_habit_name("  Study Math  ") == "study math"
    assert normalize_habit_name("read book") == "read book"
    assert normalize_habit_name("Practice 100 Days") == "practice 100 days"


@pytest.mark.parametrize("invalid_name", ["", "   ", "\t", "\n  \t"])
def test_normalize_habit_name_empty_or_whitespace_raises_value_error(invalid_name: str) -> None:
    """Verify that empty or whitespace-only names raise ValueError."""
    with pytest.raises(ValueError, match="Habit name cannot be empty"):
        normalize_habit_name(invalid_name)


def test_clean_habit_name_preserves_display_case() -> None:
    """Verify that clean_habit_name strips outer whitespace while keeping original casing."""
    assert clean_habit_name("  Study Python  ") == "Study Python"
    assert clean_habit_name("Read Docs") == "Read Docs"


def test_clean_habit_name_empty_raises_value_error() -> None:
    """Verify that clean_habit_name rejects empty or whitespace-only names."""
    with pytest.raises(ValueError, match="Habit name cannot be empty"):
        clean_habit_name("   ")


def test_habit_dataclass_creation() -> None:
    """Verify Habit dataclass fields, defaults, and key property."""
    created = date(2026, 9, 15)
    habit = Habit(name="Study Python", created_at=created)

    assert habit.name == "Study Python"
    assert habit.created_at == created
    assert habit.completed_dates == set()
    assert habit.key == "study python"


def test_habit_dataclass_with_completed_dates() -> None:
    """Verify Habit dataclass supports passing initial completed dates."""
    created = date(2026, 9, 10)
    dates = {date(2026, 9, 10), date(2026, 9, 11)}
    habit = Habit(name="Read Docs", created_at=created, completed_dates=dates)

    assert habit.completed_dates == dates
    assert len(habit.completed_dates) == 2


# ============================================================================
# Tests for Streak Calculation (RF-9)
# ============================================================================


def test_calculate_streak_empty() -> None:
    """Verify streak is 0 when no dates are recorded."""
    today = date(2026, 9, 15)
    assert calculate_streak(set(), today) == 0


def test_calculate_streak_today_only() -> None:
    """Verify streak is 1 when only today is recorded."""
    today = date(2026, 9, 15)
    assert calculate_streak({today}, today) == 1


def test_calculate_streak_yesterday_only() -> None:
    """Verify streak is 1 when only yesterday is recorded (maintained today)."""
    today = date(2026, 9, 15)
    yesterday = today - timedelta(days=1)
    assert calculate_streak({yesterday}, today) == 1


def test_calculate_streak_consecutive_days_ending_today() -> None:
    """Verify streak counts consecutive days ending today."""
    today = date(2026, 9, 15)
    dates = {today - timedelta(days=i) for i in range(5)}  # 5 consecutive days
    assert calculate_streak(dates, today) == 5


def test_calculate_streak_consecutive_days_ending_yesterday() -> None:
    """Verify streak counts consecutive days ending yesterday (not completed yet today)."""
    today = date(2026, 9, 15)
    dates = {today - timedelta(days=i) for i in range(1, 6)}  # 5 days, from yesterday back
    assert calculate_streak(dates, today) == 5


def test_calculate_streak_broken_gap() -> None:
    """Verify streak drops to 0 when last completed day is before yesterday."""
    today = date(2026, 9, 15)
    two_days_ago = today - timedelta(days=2)
    three_days_ago = today - timedelta(days=3)
    assert calculate_streak({two_days_ago, three_days_ago}, today) == 0


def test_calculate_streak_gap_with_today_completed() -> None:
    """Verify streak only counts the current run if completed today with prior gap."""
    today = date(2026, 9, 15)
    two_days_ago = today - timedelta(days=2)
    # Completed today and 2 days ago, but missed yesterday
    assert calculate_streak({today, two_days_ago}, today) == 1


def test_calculate_streak_ignores_future_dates() -> None:
    """Verify future dates relative to current_date are ignored in streak calculation."""
    today = date(2026, 9, 15)
    tomorrow = today + timedelta(days=1)
    in_two_days = today + timedelta(days=2)

    # Only future dates
    assert calculate_streak({tomorrow, in_two_days}, today) == 0

    # Today + future dates
    assert calculate_streak({today, tomorrow}, today) == 1


# ============================================================================
# Tests for is_done_today and sort_habits (RF-7, RF-9)
# ============================================================================


def test_is_done_today() -> None:
    """Verify is_done_today returns True only when current_date is in completed_dates."""
    today = date(2026, 9, 15)
    yesterday = today - timedelta(days=1)

    assert is_done_today({today}, today) is True
    assert is_done_today({yesterday}, today) is False
    assert is_done_today(set(), today) is False


def test_sort_habits_by_streak_descending_and_case_insensitive_name() -> None:
    """Verify habits are sorted primarily by streak descending, and secondarily alphabetically (case-insensitive)."""
    today = date(2026, 9, 15)
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)

    h_top = Habit(name="code python", created_at=today, completed_dates={today, yesterday, two_days_ago})  # streak: 3
    h_alpha1 = Habit(name="Algorithms", created_at=today, completed_dates={today})  # streak: 1
    h_alpha2 = Habit(name="gym workout", created_at=today, completed_dates={today})  # streak: 1
    h_alpha3 = Habit(name="read docs", created_at=today, completed_dates={yesterday})  # streak: 1
    h_zero = Habit(name="Zzz Sleep", created_at=today, completed_dates=set())  # streak: 0

    unsorted = [h_alpha2, h_zero, h_top, h_alpha3, h_alpha1]
    sorted_result = sort_habits(unsorted, today)

    # Expected order:
    # 1. code python (streak 3)
    # 2. Algorithms (streak 1, 'a' < 'g' < 'r')
    # 3. gym workout (streak 1)
    # 4. read docs (streak 1)
    # 5. Zzz Sleep (streak 0)
    expected_habits = [h_top, h_alpha1, h_alpha2, h_alpha3, h_zero]
    assert [item[0] for item in sorted_result] == expected_habits

    # Verify tuple contents (habit, streak, is_done_today)
    assert sorted_result[0] == (h_top, 3, True)
    assert sorted_result[1] == (h_alpha1, 1, True)
    assert sorted_result[2] == (h_alpha2, 1, True)
    assert sorted_result[3] == (h_alpha3, 1, False)
    assert sorted_result[4] == (h_zero, 0, False)
