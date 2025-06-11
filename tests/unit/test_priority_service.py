"""Tests for the priority scoring service."""

from asanable.constants import (
    SCORE_LATER,
    SCORE_NO_DATE,
    SCORE_OVERDUE,
    SCORE_THIS_WEEK,
    SCORE_TODAY,
    SCORE_UNREAD_EMAIL,
)
from asanable.services.priority_service import score_items
from tests.factories.digest_factory import (
    make_digest_item,
    make_gmail_only_item,
    make_overdue_item,
    make_this_week_item,
    make_today_item,
)


class TestScoring:
    def test_overdue_gets_highest_score(self) -> None:
        items = score_items([make_overdue_item()])
        assert items[0].score == SCORE_OVERDUE

    def test_today_gets_today_score(self) -> None:
        items = score_items([make_today_item()])
        assert items[0].score == SCORE_TODAY

    def test_this_week_gets_week_score(self) -> None:
        items = score_items([make_this_week_item()])
        assert items[0].score == SCORE_THIS_WEEK

    def test_gmail_only_gets_email_score(self) -> None:
        items = score_items([make_gmail_only_item()])
        assert items[0].score == SCORE_UNREAD_EMAIL

    def test_future_task_with_date_gets_later_score(self) -> None:
        from datetime import date, timedelta

        item = make_digest_item(due_on=date.today() + timedelta(days=30))
        items = score_items([item])
        assert items[0].score == SCORE_LATER

    def test_no_date_task_gets_lowest_score(self) -> None:
        item = make_digest_item(due_on=None)
        items = score_items([item])
        assert items[0].score == SCORE_NO_DATE


class TestSortOrder:
    def test_sorted_by_score_descending(self) -> None:
        no_date = make_digest_item(title="Z no date", due_on=None)
        overdue = make_overdue_item(title="A overdue")
        today = make_today_item(title="B today")

        result = score_items([no_date, overdue, today])

        assert result[0].title == "A overdue"
        assert result[1].title == "B today"
        assert result[2].title == "Z no date"

    def test_same_score_sorted_by_due_date(self) -> None:
        from datetime import date, timedelta

        later_a = make_digest_item(
            title="Task A",
            due_on=date.today() + timedelta(days=15),
        )
        later_b = make_digest_item(
            title="Task B",
            due_on=date.today() + timedelta(days=10),
        )

        result = score_items([later_a, later_b])

        assert result[0].score == result[1].score
        assert result[0].due_on < result[1].due_on

    def test_empty_list_returns_empty(self) -> None:
        assert score_items([]) == []
