"""Tests for the local cache."""

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from asanable.infrastructure.cache import (
    _dict_to_task,
    _is_expired,
    _task_to_dict,
    load_tasks,
    save_tasks,
)
from tests.factories.task_factory import make_overdue_task, make_task


class TestTaskSerialization:
    def test_roundtrip_with_due_date(self) -> None:
        from datetime import date

        task = make_task(gid="111", name="Test", due_on=date(2025, 6, 15))
        data = _task_to_dict(task)
        restored = _dict_to_task(data)

        assert restored.gid == "111"
        assert restored.name == "Test"
        assert restored.due_on == date(2025, 6, 15)

    def test_roundtrip_without_due_date(self) -> None:
        task = make_task(gid="222", due_on=None)
        data = _task_to_dict(task)
        restored = _dict_to_task(data)

        assert restored.due_on is None

    def test_preserves_project_and_section(self) -> None:
        task = make_task(project_name="Backend", section_name="To Do")
        data = _task_to_dict(task)
        restored = _dict_to_task(data)

        assert restored.project_name == "Backend"
        assert restored.section_name == "To Do"


class TestIsExpired:
    def test_fresh_cache_is_not_expired(self) -> None:
        payload = {"cached_at": datetime.now(tz=UTC).isoformat()}
        assert _is_expired(payload, ttl_hours=24) is False

    def test_old_cache_is_expired(self) -> None:
        old = (datetime.now(tz=UTC) - timedelta(hours=25)).isoformat()
        payload = {"cached_at": old}
        assert _is_expired(payload, ttl_hours=24) is True

    def test_missing_timestamp_is_expired(self) -> None:
        assert _is_expired({}, ttl_hours=24) is True


class TestSaveAndLoad:
    @patch("asanable.infrastructure.cache.get_cache_path")
    def test_save_and_load_roundtrip(self, mock_path, tmp_path) -> None:
        cache_file = tmp_path / "tasks.json"
        mock_path.return_value = cache_file

        tasks = [make_task(gid="111"), make_overdue_task(gid="222")]
        save_tasks(tasks)

        loaded = load_tasks()
        assert loaded is not None
        assert len(loaded) == 2
        assert loaded[0].gid == "111"
        assert loaded[1].gid == "222"

    @patch("asanable.infrastructure.cache.get_cache_path")
    def test_returns_none_when_no_cache(self, mock_path, tmp_path) -> None:
        mock_path.return_value = tmp_path / "nonexistent.json"
        assert load_tasks() is None

    @patch("asanable.infrastructure.cache.get_cache_path")
    def test_returns_none_when_expired(self, mock_path, tmp_path) -> None:
        cache_file = tmp_path / "tasks.json"
        mock_path.return_value = cache_file

        payload = {
            "cached_at": (datetime.now(tz=UTC) - timedelta(hours=48)).isoformat(),
            "tasks": [],
        }
        cache_file.write_text(json.dumps(payload))

        assert load_tasks(ttl_hours=24) is None

    @patch("asanable.infrastructure.cache.get_cache_path")
    def test_returns_none_on_corrupt_json(self, mock_path, tmp_path) -> None:
        cache_file = tmp_path / "tasks.json"
        mock_path.return_value = cache_file
        cache_file.write_text("not json{{{")

        assert load_tasks() is None
