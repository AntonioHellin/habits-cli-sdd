"""JSON file persistence and storage error handling for habits-cli-sdd.

Provides load and save operations for habits using a single, human-readable
JSON file with atomic writing and fail-safe error handling.
"""

from datetime import date
import json
import os
from pathlib import Path
import tempfile

from habits.core import Habit


class StorageError(Exception):
    """Raised when an error occurs during loading or saving habit data."""


def get_storage_path() -> Path:
    """Resolve the storage file path, honoring HABITS_FILE environment variable if set."""
    env_path = os.environ.get("HABITS_FILE")
    if env_path:
        return Path(env_path)
    return Path.home() / ".habits.json"


def load_habits(path: Path) -> dict[str, Habit]:
    """Load habits from a JSON file.

    Returns an empty dict if the file does not exist.

    Raises:
        StorageError: If the file cannot be read, contains invalid JSON,
            or fails schema validation. Existing file is never modified.
    """
    if not path.exists():
        return {}

    try:
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)

        if not isinstance(data, dict):
            raise ValueError("Root element must be a JSON object.")

        habits_data = data.get("habits")
        if not isinstance(habits_data, dict):
            raise ValueError("'habits' field must be a JSON object.")

        result: dict[str, Habit] = {}
        for habit_key, raw_habit in habits_data.items():
            if not isinstance(raw_habit, dict):
                raise ValueError(f"Habit '{habit_key}' must be an object.")

            name = raw_habit.get("name")
            created_str = raw_habit.get("created_at")
            completed_strs = raw_habit.get("completed_dates")

            if not isinstance(name, str) or not isinstance(created_str, str) or not isinstance(completed_strs, list):
                raise ValueError(f"Habit '{habit_key}' has missing or invalid fields.")

            created_at = date.fromisoformat(created_str)
            completed_dates = {date.fromisoformat(d) for d in completed_strs}

            habit = Habit(
                name=name,
                created_at=created_at,
                completed_dates=completed_dates,
            )
            result[habit.key] = habit

        return result

    except Exception as exc:
        raise StorageError(f"Could not load data from {path}: {exc}") from exc


def save_habits(path: Path, habits: dict[str, Habit]) -> None:
    """Save habits atomically to a JSON file.

    Raises:
        StorageError: If the file cannot be written. Existing file remains intact.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "schema_version": 1,
            "habits": {
                habit.key: {
                    "name": habit.name,
                    "created_at": habit.created_at.isoformat(),
                    "completed_dates": sorted(d.isoformat() for d in habit.completed_dates),
                }
                for habit in habits.values()
            },
        }

        # Write to temporary file in the same directory for atomic replace
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as tmp_file:
            json.dump(payload, tmp_file, indent=2, ensure_ascii=False)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
            temp_path = Path(tmp_file.name)

        os.replace(temp_path, path)

    except Exception as exc:
        raise StorageError(f"Could not save data to {path}: {exc}") from exc
