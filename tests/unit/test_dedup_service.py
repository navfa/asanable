"""Tests for the deduplication service."""

from asanable.constants import ItemSource
from asanable.services.dedup_service import build_digest_items
from tests.factories.email_factory import make_asana_notification, make_regular_email
from tests.factories.task_factory import make_task


class TestBuildDigestItems:
    def test_converts_tasks_to_digest_items(self) -> None:
        tasks = [make_task(gid="111", name="Fix bug")]
        result = build_digest_items(tasks, [])

        assert len(result) == 1
        assert result[0].title == "Fix bug"
        assert result[0].source == ItemSource.ASANA
        assert result[0].asana_task_gid == "111"

    def test_converts_emails_to_digest_items(self) -> None:
        emails = [make_regular_email(message_id="msg-1", subject="Hello")]
        result = build_digest_items([], emails)

        assert len(result) == 1
        assert result[0].title == "Hello"
        assert result[0].source == ItemSource.GMAIL

    def test_empty_inputs_returns_empty(self) -> None:
        assert build_digest_items([], []) == []


class TestDeduplication:
    def test_merges_matching_task_and_email(self) -> None:
        tasks = [make_task(gid="555", name="Deploy service")]
        emails = [make_asana_notification(asana_task_gid="555", message_id="msg-a")]
        result = build_digest_items(tasks, emails)

        assert len(result) == 1
        assert result[0].title == "Deploy service"
        assert result[0].asana_task_gid == "555"
        assert result[0].gmail_message_id == "msg-a"
        assert result[0].source == ItemSource.ASANA

    def test_keeps_unmatched_email_separately(self) -> None:
        tasks = [make_task(gid="111")]
        emails = [make_asana_notification(asana_task_gid="999")]
        result = build_digest_items(tasks, emails)

        assert len(result) == 2

    def test_keeps_regular_email_separately(self) -> None:
        tasks = [make_task(gid="111")]
        emails = [make_regular_email()]
        result = build_digest_items(tasks, emails)

        assert len(result) == 2
        sources = {item.source for item in result}
        assert sources == {ItemSource.ASANA, ItemSource.GMAIL}

    def test_merged_item_preserves_email_snippet(self) -> None:
        tasks = [make_task(gid="555")]
        emails = [make_asana_notification(asana_task_gid="555", snippet="New comment")]
        result = build_digest_items(tasks, emails)

        assert result[0].snippet == "New comment"

    def test_multiple_tasks_one_matching_email(self) -> None:
        tasks = [make_task(gid="111"), make_task(gid="222")]
        emails = [make_asana_notification(asana_task_gid="222")]
        result = build_digest_items(tasks, emails)

        assert len(result) == 2
        merged = [r for r in result if r.gmail_message_id is not None]
        assert len(merged) == 1
        assert merged[0].asana_task_gid == "222"
