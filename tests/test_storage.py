"""Unit and integration tests for habits.storage JSON persistence."""

from datetime import date
import json
from pathlib import Path
import pytest

from habits.core import Habit
from habits.storage import (
    StorageError,
    get_storage_path,
    load_habits,
    save_habits,
)


def test_get_storage_path_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify default storage path points to ~/.habits.json when HABITS_FILE is unset."""
    monkeypatch.delenv("HABITS_FILE", raising=False)
    expected = Path.home() / ".habits.json"
    assert get_storage_path() == expected


def test_get_storage_path_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Verify HABITS_FILE environment variable overrides default storage path."""
    custom_file = tmp_path / "custom_habits.json"
    monkeypatch.setenv("HABITS_FILE", str(custom_file))
    assert get_storage_path() == custom_file


def test_load_habits_non_existent_file(tmp_path: Path) -> None:
    """Verify loading from a non-existent file returns an empty dictionary without error."""
    non_existent = tmp_path / "does_not_exist.json"
    habits = load_habits(non_existent)
    assert habits == {}


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    """Verify habits can be saved to JSON and accurately reloaded."""
    file_path = tmp_path / "habits.json"

    habit1 = Habit(
        name="Study Python",
        created_at=date(2026, 9, 10),
        completed_dates={date(2026, 9, 14), date(2026, 9, 15)},
    )
    habit2 = Habit(
        name="Exercise Daily",
        created_at=date(2026, 9, 15),
        completed_dates=set(),
    )

    habits_dict = {
        habit1.key: habit1,
        habit2.key: habit2,
    }

    save_habits(file_path, habits_dict)

    # Verify physical file existence and JSON schema
    assert file_path.exists()
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["schema_version"] == 1
    assert "study python" in data["habits"]
    assert data["habits"]["study python"]["name"] == "Study Python"
    assert data["habits"]["study python"]["created_at"] == "2026-09-10"
    assert data["habits"]["study python"]["completed_dates"] == ["2026-09-14", "2026-09-15"]
    assert data["habits"]["exercise daily"]["completed_dates"] == []

    # Verify reloading reconstitutes Habit instances correctly
    loaded = load_habits(file_path)
    assert len(loaded) == 2
    assert loaded["study python"] == habit1
    assert loaded["exercise daily"] == habit2


def test_load_habits_corrupted_json_raises_storage_error(tmp_path: Path) -> None:
    """Verify invalid JSON raises StorageError and does not overwrite or destroy file."""
    file_path = tmp_path / "corrupt.json"
    corrupt_content = '{"schema_version": 1, "habits": { INVALID JSON'
    file_path.write_text(corrupt_content, encoding="utf-8")

    with pytest.raises(StorageError, match="Could not load"):
        load_habits(file_path)

    # Verify file content is unchanged
    assert file_path.read_text(encoding="utf-8") == corrupt_content


@pytest.mark.parametrize(
    "invalid_data",
    [
        {"habits": []},  # habits should be a dict
        {"schema_version": 1},  # missing habits key
        {"habits": {"bad": {"name": "Bad"}}},  # missing created_at and completed_dates
        {"habits": {"bad": {"name": "Bad", "created_at": "invalid-date", "completed_dates": []}}},
        {"habits": {"bad": {"name": "Bad", "created_at": "2026-09-10", "completed_dates": ["not-a-date"]}}},
    ],
)
def test_load_habits_invalid_structure_raises_storage_error(tmp_path: Path, invalid_data: dict) -> None:
    """Verify non-conforming data structures raise StorageError."""
    file_path = tmp_path / "invalid_structure.json"
    file_path.write_text(json.dumps(invalid_data), encoding="utf-8")

    with pytest.raises(StorageError):
        load_habits(file_path)


def test_save_habits_creates_parent_directories(tmp_path: Path) -> None:
    """Verify save_habits creates intermediate parent directories if they do not exist."""
    nested_path = tmp_path / "nested" / "dir" / "habits.json"
    habit = Habit(name="Deep Work", created_at=date(2026, 9, 15))

    save_habits(nested_path, {habit.key: habit})
    assert nested_path.exists()
    loaded = load_habits(nested_path)
    assert loaded["deep work"].name == "Deep Work"
