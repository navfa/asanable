"""Asana task domain entity."""

from dataclasses import dataclass
from datetime import date

from asanable.infrastructure.clock import today as _today


@dataclass(frozen=True)
class AsanaTask:
    """Pure domain representation of an Asana task."""

    gid: str
    name: str
    due_on: date | None
    project_name: str | None
    section_name: str | None
    permalink_url: str

    @property
    def is_overdue(self) -> bool:
        """A task is overdue when its due date is strictly before today."""
        if self.due_on is None:
            return False
        return self.due_on < _today()

    @property
    def is_due_today(self) -> bool:
        """Check if the task is due today."""
        if self.due_on is None:
            return False
        return self.due_on == _today()


def sort_tasks_by_due_date(tasks: list[AsanaTask]) -> list[AsanaTask]:
    """Sort tasks by due date ascending, no-date tasks last, then alphabetical."""
    return sorted(tasks, key=_task_sort_key)


def _task_sort_key(task: AsanaTask) -> tuple[int, date | None, str]:
    """Build a composite sort key: has_date flag, date, name."""
    if task.due_on is None:
        return (1, None, task.name.lower())
    return (0, task.due_on, task.name.lower())
