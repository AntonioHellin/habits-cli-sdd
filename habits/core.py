"""Pure domain models and functions for habits-cli-sdd.

This module contains business entities and pure transformation functions.
It has zero dependencies on I/O, terminal printing, or command-line parsers.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta


def clean_habit_name(name: str) -> str:
    """Trim leading and trailing whitespace from a habit name.

    Raises:
        ValueError: If the resulting name is empty or composed solely of whitespace.
    """
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("Habit name cannot be empty.")
    return cleaned


def normalize_habit_name(name: str) -> str:
    """Return a lowercased and stripped key used for case-insensitive habit matching.

    Raises:
        ValueError: If the name is empty or composed solely of whitespace.
    """
    return clean_habit_name(name).lower()


@dataclass
class Habit:
    """Represents a tracked study habit."""

    name: str
    created_at: date
    completed_dates: set[date] = field(default_factory=set)

    @property
    def key(self) -> str:
        """Return the normalized unique key for dictionary lookups."""
        return normalize_habit_name(self.name)


def calculate_streak(completed_dates: set[date], current_date: date) -> int:
    """Calculate the consecutive active days ending today or yesterday.

    Future dates relative to current_date are ignored. If no completion
    is recorded for either current_date or current_date - 1 day, the streak is 0.
    """
    if not completed_dates:
        return 0

    valid_dates = {d for d in completed_dates if d <= current_date}
    if not valid_dates:
        return 0

    yesterday = current_date - timedelta(days=1)
    if current_date not in valid_dates and yesterday not in valid_dates:
        return 0

    check_date = current_date if current_date in valid_dates else yesterday
    streak = 0
    while check_date in valid_dates:
        streak += 1
        check_date -= timedelta(days=1)

    return streak


def is_done_today(completed_dates: set[date], current_date: date) -> bool:
    """Return True if current_date is recorded in completed_dates."""
    return current_date in completed_dates


def sort_habits(
    habits: list[Habit], current_date: date
) -> list[tuple[Habit, int, bool]]:
    """Sort habits by streak descending, and secondarily alphabetically (case-insensitive).

    Returns a list of tuples containing (habit, streak, is_done_today).
    """
    items: list[tuple[Habit, int, bool]] = []
    for habit in habits:
        streak = calculate_streak(habit.completed_dates, current_date)
        done_today = is_done_today(habit.completed_dates, current_date)
        items.append((habit, streak, done_today))

    items.sort(key=lambda item: (-item[1], item[0].name.lower()))
    return items
