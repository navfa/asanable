"""Tests for the digest orchestration service."""

from datetime import date, timedelta

from asanable.constants import DigestSectionType
from asanable.services.digest_service import build_digest
from tests.factories.email_factory import make_regular_email
from tests.factories.task_factory import (
    make_no_date_task,
    make_overdue_task,
    make_task,
    make_today_task,
)


class TestBuildDigest:
    def test_returns_digest_with_sections(self) -> None:
        tasks = [make_overdue_task(), make_today_task()]
        digest = build_digest(tasks, [])

        assert len(digest.sections) >= 2
        section_types = {s.section_type for s in digest.sections}
        assert DigestSectionType.OVERDUE in section_types
        assert DigestSectionType.TODAY in section_types

    def test_summary_counts_are_correct(self) -> None:
        tasks = [make_overdue_task(), make_overdue_task(gid="222"), make_today_task()]
        digest = build_digest(tasks, [])

        assert digest.summary.total_items == 3
        assert digest.summary.overdue_count == 2
        assert digest.summary.today_count == 1

    def test_empty_sections_are_excluded(self) -> None:
        tasks = [make_today_task()]
        digest = build_digest(tasks, [])

        section_types = {s.section_type for s in digest.sections}
        assert DigestSectionType.OVERDUE not in section_types

    def test_gmail_items_in_gmail_section(self) -> None:
        emails = [make_regular_email()]
        digest = build_digest([], emails)

        assert len(digest.sections) == 1
        assert digest.sections[0].section_type == DigestSectionType.GMAIL

    def test_no_data_returns_empty_digest(self) -> None:
        digest = build_digest([], [])

        assert digest.summary.total_items == 0
        assert len(digest.sections) == 0

    def test_this_week_section(self) -> None:
        task = make_task(due_on=date.today() + timedelta(days=3))
        digest = build_digest([task], [])

        section_types = {s.section_type for s in digest.sections}
        assert DigestSectionType.THIS_WEEK in section_types

    def test_later_section_for_no_date(self) -> None:
        task = make_no_date_task()
        digest = build_digest([task], [])

        section_types = {s.section_type for s in digest.sections}
        assert DigestSectionType.LATER in section_types
