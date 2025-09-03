"""Tests for the mapper service."""

from asanable.constants import ItemSource
from asanable.services.mapper_service import build_digest_items
from tests.factories.task_factory import make_overdue_task, make_task


class TestBuildDigestItems:
    def test_converts_tasks_to_digest_items(self) -> None:
        tasks = [make_task(gid="111", name="Fix bug")]
        result = build_digest_items(tasks)

        assert len(result) == 1
        assert result[0].title == "Fix bug"
        assert result[0].source == ItemSource.ASANA
        assert result[0].asana_task_gid == "111"

    def test_empty_inputs_returns_empty(self) -> None:
        assert build_digest_items([]) == []

    def test_preserves_overdue_flag(self) -> None:
        tasks = [make_overdue_task(gid="111")]
        result = build_digest_items(tasks)

        assert result[0].is_overdue is True

    def test_preserves_project_name(self) -> None:
        tasks = [make_task(gid="111", project_name="Engineering")]
        result = build_digest_items(tasks)

        assert result[0].project_name == "Engineering"

    def test_multiple_tasks(self) -> None:
        tasks = [make_task(gid="111", name="Task A"), make_task(gid="222", name="Task B")]
        result = build_digest_items(tasks)

        assert len(result) == 2
        assert result[0].title == "Task A"
        assert result[1].title == "Task B"
