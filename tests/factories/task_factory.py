"""Factory helpers for creating AsanaTask test instances."""

from datetime import date, timedelta

from asanable.domain.task import AsanaTask

DEFAULT_GID = "12345"
DEFAULT_NAME = "Review pull request"
DEFAULT_PROJECT = "Engineering"
DEFAULT_SECTION = "In Progress"
DEFAULT_URL = "https://app.asana.com/0/12345/67890"


def make_task(
    *,
    gid: str = DEFAULT_GID,
    name: str = DEFAULT_NAME,
    due_on: date | None = None,
    project_name: str | None = DEFAULT_PROJECT,
    section_name: str | None = DEFAULT_SECTION,
    permalink_url: str = DEFAULT_URL,
) -> AsanaTask:
    """Create an AsanaTask with sensible defaults for testing."""
    return AsanaTask(
        gid=gid,
        name=name,
        due_on=due_on,
        project_name=project_name,
        section_name=section_name,
        permalink_url=permalink_url,
    )


def make_overdue_task(**overrides) -> AsanaTask:
    """Create a task that is overdue (due yesterday)."""
    defaults = {"due_on": date.today() - timedelta(days=1), "name": "Overdue task"}
    defaults.update(overrides)
    return make_task(**defaults)


def make_today_task(**overrides) -> AsanaTask:
    """Create a task that is due today."""
    defaults = {"due_on": date.today(), "name": "Today task"}
    defaults.update(overrides)
    return make_task(**defaults)


def make_future_task(**overrides) -> AsanaTask:
    """Create a task due in the future."""
    defaults = {"due_on": date.today() + timedelta(days=5), "name": "Future task"}
    defaults.update(overrides)
    return make_task(**defaults)


def make_no_date_task(**overrides) -> AsanaTask:
    """Create a task with no due date."""
    defaults = {"due_on": None, "name": "No date task"}
    defaults.update(overrides)
    return make_task(**defaults)
