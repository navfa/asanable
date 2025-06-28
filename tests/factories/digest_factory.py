"""Factory helpers for creating DigestItem test instances."""

from datetime import date, timedelta

from asanable.constants import ItemSource
from asanable.domain.digest import DigestItem


def make_digest_item(
    *,
    title: str = "Some task",
    source: ItemSource = ItemSource.ASANA,
    permalink: str = "https://app.asana.com/0/123/456",
    due_on: date | None = None,
    project_name: str | None = "Engineering",
    snippet: str | None = None,
    asana_task_gid: str | None = "456",
    is_overdue: bool = False,
    score: int = 0,
) -> DigestItem:
    """Create a DigestItem with sensible defaults."""
    return DigestItem(
        title=title,
        source=source,
        permalink=permalink,
        due_on=due_on,
        project_name=project_name,
        snippet=snippet,
        asana_task_gid=asana_task_gid,
        is_overdue=is_overdue,
        score=score,
    )


def make_overdue_item(**overrides) -> DigestItem:
    defaults = {
        "title": "Overdue item",
        "due_on": date.today() - timedelta(days=2),
        "is_overdue": True,
    }
    defaults.update(overrides)
    return make_digest_item(**defaults)


def make_today_item(**overrides) -> DigestItem:
    defaults = {
        "title": "Today item",
        "due_on": date.today(),
    }
    defaults.update(overrides)
    return make_digest_item(**defaults)


def make_this_week_item(**overrides) -> DigestItem:
    defaults = {
        "title": "This week item",
        "due_on": date.today() + timedelta(days=3),
    }
    defaults.update(overrides)
    return make_digest_item(**defaults)
