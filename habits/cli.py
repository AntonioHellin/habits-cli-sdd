"""Command-line interface (CLI) for habits-cli-sdd.

Provides command parsing, formatting, and dispatch for habits management.
All user messages, errors, and help texts are in English.
"""

import argparse
from datetime import date
import sys

from habits.core import (
    Habit,
    clean_habit_name,
    normalize_habit_name,
    sort_habits,
)
from habits.storage import (
    StorageError,
    get_storage_path,
    load_habits,
    save_habits,
)


def build_parser() -> argparse.ArgumentParser:
    """Build and configure the argument parser for habits-cli-sdd."""
    parser = argparse.ArgumentParser(
        prog="habits",
        description="A lightweight CLI to track daily study habits and streaks.",
    )
    subparsers = parser.add_subparsers(dest="subcommand")

    # habits add <name...>
    add_parser = subparsers.add_parser("add", help="Add a new habit to track")
    add_parser.add_argument("name", nargs="+", help="Name of the habit")

    # habits done <name...>
    done_parser = subparsers.add_parser("done", help="Mark a habit as done for today")
    done_parser.add_argument("name", nargs="+", help="Name of the habit")

    # habits list
    subparsers.add_parser("list", help="List all habits and their current streaks")

    return parser


def handle_add(args: argparse.Namespace) -> int:
    """Handle the 'add' subcommand."""
    raw_name = " ".join(args.name)
    try:
        cleaned_name = clean_habit_name(raw_name)
        norm_key = normalize_habit_name(raw_name)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    storage_path = get_storage_path()
    try:
        habits = load_habits(storage_path)
    except StorageError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    if norm_key in habits:
        print(f"Error: Habit '{cleaned_name}' already exists.", file=sys.stderr)
        return 1

    new_habit = Habit(name=cleaned_name, created_at=date.today())
    habits[new_habit.key] = new_habit

    try:
        save_habits(storage_path, habits)
    except StorageError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    print(f"Habit '{cleaned_name}' created successfully.")
    return 0


def handle_done(args: argparse.Namespace) -> int:
    """Handle the 'done' subcommand."""
    raw_name = " ".join(args.name)
    try:
        cleaned_name = clean_habit_name(raw_name)
        norm_key = normalize_habit_name(raw_name)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    storage_path = get_storage_path()
    try:
        habits = load_habits(storage_path)
    except StorageError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    if norm_key not in habits:
        print(
            f"Error: Habit '{cleaned_name}' not found. Use 'habits list' to see available habits.",
            file=sys.stderr,
        )
        return 1

    habit = habits[norm_key]
    today = date.today()

    if today in habit.completed_dates:
        print(f"Habit '{habit.name}' is already marked as done for today.")
        return 0

    habit.completed_dates.add(today)

    try:
        save_habits(storage_path, habits)
    except StorageError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    print(f"Marked '{habit.name}' as done for today.")
    return 0


def handle_list(args: argparse.Namespace) -> int:
    """Handle the 'list' subcommand."""
    storage_path = get_storage_path()
    try:
        habits = load_habits(storage_path)
    except StorageError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    if not habits:
        print("No habits registered yet. Create your first habit with 'habits add <name>'.")
        return 0

    sorted_items = sort_habits(list(habits.values()), date.today())
    for habit, streak, is_done in sorted_items:
        status_tag = "done today" if is_done else "pending"
        print(f"- {habit.name}: {streak} day(s) [{status_tag}]")

    return 0


def main(argv: list[str] | None = None) -> int:
    """Main CLI entrypoint function."""
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.subcommand == "add":
        return handle_add(args)
    if args.subcommand == "done":
        return handle_done(args)
    if args.subcommand == "list":
        return handle_list(args)

    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
