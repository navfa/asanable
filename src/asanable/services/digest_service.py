"""Digest service — orchestrates dedup, scoring, and section building."""

from asanable.constants import DigestSectionType, ItemSource
from asanable.domain.digest import Digest, DigestItem, DigestSection, DigestSummary
from asanable.domain.email import GmailMessage
from asanable.domain.task import AsanaTask
from asanable.services.dedup_service import build_digest_items
from asanable.services.priority_service import score_items


def build_digest(tasks: list[AsanaTask], emails: list[GmailMessage]) -> Digest:
    """Build a complete digest from raw tasks and emails."""
    items = build_digest_items(tasks, emails)
    scored_items = score_items(items)
    sections = _build_sections(scored_items)
    summary = _build_summary(scored_items)
    return Digest(summary=summary, sections=tuple(sections))


def _build_sections(items: list[DigestItem]) -> list[DigestSection]:
    """Group scored items into ordered digest sections, skip empty ones."""
    section_map = _group_by_section(items)
    return [
        DigestSection(section_type=section_type, items=tuple(section_items))
        for section_type in DigestSectionType
        if (section_items := section_map.get(section_type, []))
    ]


def _group_by_section(items: list[DigestItem]) -> dict[DigestSectionType, list[DigestItem]]:
    """Assign each item to its section based on its attributes."""
    groups: dict[DigestSectionType, list[DigestItem]] = {}
    for item in items:
        section = _classify_item(item)
        groups.setdefault(section, []).append(item)
    return groups


def _classify_item(item: DigestItem) -> DigestSectionType:
    """Determine which section an item belongs to."""
    if item.source == ItemSource.GMAIL and item.asana_task_gid is None:
        return DigestSectionType.GMAIL
    if item.is_overdue:
        return DigestSectionType.OVERDUE
    if _is_due_today(item):
        return DigestSectionType.TODAY
    if _is_due_this_week(item):
        return DigestSectionType.THIS_WEEK
    return DigestSectionType.LATER


def _is_due_today(item: DigestItem) -> bool:
    """Check if item is due today."""
    from datetime import date

    return item.due_on == date.today()


def _is_due_this_week(item: DigestItem) -> bool:
    """Check if item is due within the next 7 days."""
    from datetime import date, timedelta

    if item.due_on is None:
        return False
    today = date.today()
    return today < item.due_on <= today + timedelta(days=7)


def _build_summary(items: list[DigestItem]) -> DigestSummary:
    """Compute summary stats from scored items."""
    overdue_count = sum(1 for item in items if item.is_overdue)
    today_count = sum(1 for item in items if _is_due_today(item))
    this_week_count = sum(1 for item in items if _is_due_this_week(item))
    later_count = len(items) - overdue_count - today_count - this_week_count
    section_counts = _count_by_section(items)
    project_counts = _count_by_project(items)
    return DigestSummary(
        total_items=len(items),
        overdue_count=overdue_count,
        today_count=today_count,
        this_week_count=this_week_count,
        later_count=later_count,
        section_counts=section_counts,
        project_counts=project_counts,
    )


def _count_by_section(items: list[DigestItem]) -> dict[str, int]:
    """Count items per section type."""
    counts: dict[str, int] = {}
    for item in items:
        section = _classify_item(item).value
        counts[section] = counts.get(section, 0) + 1
    return counts


def _count_by_project(items: list[DigestItem]) -> dict[str, int]:
    """Count items per project, sorted descending."""
    counts: dict[str, int] = {}
    for item in items:
        project = item.project_name or "No project"
        counts[project] = counts.get(project, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
