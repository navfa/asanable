"""Digest domain entities — unified view of tasks."""

from dataclasses import dataclass, field
from datetime import date, datetime

from asanable.constants import DigestSectionType, ItemSource


@dataclass(frozen=True)
class DigestItem:
    """A single item in the digest."""

    title: str
    source: ItemSource
    permalink: str
    due_on: date | None = None
    project_name: str | None = None
    snippet: str | None = None
    asana_task_gid: str | None = None
    is_overdue: bool = False
    score: int = 0


@dataclass(frozen=True)
class DigestSection:
    """A group of items under a common heading."""

    section_type: DigestSectionType
    items: tuple[DigestItem, ...] = ()


@dataclass(frozen=True)
class DigestSummary:
    """Quick stats for the digest header."""

    total_items: int
    overdue_count: int
    today_count: int
    this_week_count: int = 0
    later_count: int = 0
    section_counts: dict[str, int] = field(default_factory=dict)
    project_counts: dict[str, int] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class Digest:
    """Complete digest ready for rendering."""

    summary: DigestSummary
    sections: tuple[DigestSection, ...] = ()
