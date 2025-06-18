"""Tests for the Telegram renderer."""

from datetime import date, datetime

from asanable.constants import DigestSectionType, ItemSource
from asanable.domain.digest import Digest, DigestItem, DigestSection, DigestSummary
from asanable.renderers.telegram_renderer import _build_message


def _make_digest(*, sections: tuple = ()) -> Digest:
    return Digest(
        summary=DigestSummary(
            total_items=5,
            overdue_count=2,
            today_count=1,
            generated_at=datetime(2025, 6, 15, 8, 30),
        ),
        sections=sections,
    )


class TestBuildMessage:
    def test_contains_header(self) -> None:
        msg = _build_message(_make_digest())
        assert "*Daily Digest*" in msg
        assert "2025-06-15" in msg

    def test_contains_counters(self) -> None:
        msg = _build_message(_make_digest())
        assert "*5*" in msg
        assert "*2*" in msg

    def test_section_title_formatted(self) -> None:
        section = DigestSection(
            section_type=DigestSectionType.THIS_WEEK,
            items=(
                DigestItem(
                    title="Review PR",
                    source=ItemSource.ASANA,
                    permalink="",
                    due_on=date(2025, 6, 18),
                ),
            ),
        )
        msg = _build_message(_make_digest(sections=(section,)))
        assert "*This Week*" in msg
        assert "• Review PR" in msg
        assert "_Jun 18_" in msg

    def test_item_without_date(self) -> None:
        section = DigestSection(
            section_type=DigestSectionType.LATER,
            items=(
                DigestItem(title="Backlog", source=ItemSource.ASANA, permalink=""),
            ),
        )
        msg = _build_message(_make_digest(sections=(section,)))
        assert "• Backlog" in msg
