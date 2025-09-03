"""Conversion service — converts Asana tasks to digest items."""

from asanable.constants import ItemSource
from asanable.domain.digest import DigestItem
from asanable.domain.task import AsanaTask


def build_digest_items(tasks: list[AsanaTask]) -> list[DigestItem]:
    """Convert tasks into unified digest items."""
    return [_task_to_item(task) for task in tasks]


def _task_to_item(task: AsanaTask) -> DigestItem:
    """Convert a single Asana task to a digest item."""
    return DigestItem(
        title=task.name,
        source=ItemSource.ASANA,
        permalink=task.permalink_url,
        due_on=task.due_on,
        project_name=task.project_name,
        asana_task_gid=task.gid,
        is_overdue=task.is_overdue,
    )
