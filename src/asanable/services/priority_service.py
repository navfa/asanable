"""Priority service — scores and sorts digest items."""

from datetime import timedelta

from asanable.constants import (
    SCORE_LATER,
    SCORE_NO_DATE,
    SCORE_OVERDUE,
    SCORE_THIS_WEEK,
    SCORE_TODAY,
)
from asanable.domain.digest import DigestItem
from asanable.infrastructure.clock import today as _today

DAYS_IN_WEEK = 7


def score_items(items: list[DigestItem]) -> list[DigestItem]:
    """Assign a priority score to each item and sort by priority descending."""
    scored = [_apply_score(item) for item in items]
    return sorted(scored, key=_sort_key, reverse=True)


def _apply_score(item: DigestItem) -> DigestItem:
    """Return a new DigestItem with its computed score."""
    return DigestItem(
        title=item.title,
        source=item.source,
        permalink=item.permalink,
        due_on=item.due_on,
        project_name=item.project_name,
        snippet=item.snippet,
        asana_task_gid=item.asana_task_gid,
        is_overdue=item.is_overdue,
        score=_compute_score(item),
    )


def _compute_score(item: DigestItem) -> int:
    """Pure function: compute priority score for a single item."""
    if item.is_overdue:
        return SCORE_OVERDUE
    if _is_due_today(item):
        return SCORE_TODAY
    if _is_due_this_week(item):
        return SCORE_THIS_WEEK
    if item.due_on is not None:
        return SCORE_LATER
    return SCORE_NO_DATE


def _is_due_today(item: DigestItem) -> bool:
    """Check if the item is due today."""
    return item.due_on == _today()


def _is_due_this_week(item: DigestItem) -> bool:
    """Check if the item is due within the next 7 days (excluding today)."""
    if item.due_on is None:
        return False
    today = _today()
    end_of_week = today + timedelta(days=DAYS_IN_WEEK)
    return today < item.due_on <= end_of_week


def _sort_key(item: DigestItem) -> tuple[int, int, str]:
    """Sort by score desc, then due date asc, then title asc."""
    due_order = item.due_on.toordinal() if item.due_on else 999999
    return (item.score, -due_order, item.title.lower())
