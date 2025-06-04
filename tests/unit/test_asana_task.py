"""Tests for AsanaTask domain entity."""

from datetime import date

import pytest

from asanable.domain.task import sort_tasks_by_due_date
from tests.factories.task_factory import (
    make_future_task,
    make_no_date_task,
    make_overdue_task,
    make_task,
    make_today_task,
)


class TestIsOverdue:
    def test_past_due_date_is_overdue(self) -> None:
        task = make_overdue_task()
        assert task.is_overdue is True

    def test_today_due_date_is_not_overdue(self) -> None:
        task = make_today_task()
        assert task.is_overdue is False

    def test_future_due_date_is_not_overdue(self) -> None:
        task = make_future_task()
        assert task.is_overdue is False

    def test_no_due_date_is_never_overdue(self) -> None:
        task = make_no_date_task()
        assert task.is_overdue is False


class TestIsDueToday:
    def test_today_due_date_is_due_today(self) -> None:
        task = make_today_task()
        assert task.is_due_today is True

    def test_past_due_date_is_not_due_today(self) -> None:
        task = make_overdue_task()
        assert task.is_due_today is False

    def test_no_due_date_is_not_due_today(self) -> None:
        task = make_no_date_task()
        assert task.is_due_today is False


class TestSortByDueDate:
    def test_sorts_by_date_ascending(self) -> None:
        future = make_future_task()
        today = make_today_task()
        overdue = make_overdue_task()

        result = sort_tasks_by_due_date([future, today, overdue])

        assert result[0] == overdue
        assert result[1] == today
        assert result[2] == future

    def test_no_date_tasks_placed_last(self) -> None:
        today = make_today_task()
        no_date = make_no_date_task()

        result = sort_tasks_by_due_date([no_date, today])

        assert result[0] == today
        assert result[1] == no_date

    def test_same_date_sorted_alphabetically(self) -> None:
        task_b = make_task(name="Beta task", due_on=date.today())
        task_a = make_task(name="Alpha task", due_on=date.today())

        result = sort_tasks_by_due_date([task_b, task_a])

        assert result[0] == task_a
        assert result[1] == task_b

    def test_empty_list_returns_empty(self) -> None:
        assert sort_tasks_by_due_date([]) == []

    def test_multiple_no_date_sorted_alphabetically(self) -> None:
        task_z = make_no_date_task(name="Zebra")
        task_a = make_no_date_task(name="Alpha")

        result = sort_tasks_by_due_date([task_z, task_a])

        assert result[0].name == "Alpha"
        assert result[1].name == "Zebra"


class TestAsanaTaskImmutability:
    def test_frozen_dataclass_cannot_be_modified(self) -> None:
        task = make_task()
        with pytest.raises(AttributeError):
            task.name = "Modified"  # type: ignore[misc]
