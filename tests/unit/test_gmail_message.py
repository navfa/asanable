"""Tests for GmailMessage domain entity."""

from tests.factories.email_factory import make_asana_notification, make_email, make_regular_email


class TestIsAsanaNotification:
    def test_email_with_task_gid_is_asana_notification(self) -> None:
        email = make_asana_notification()
        assert email.is_asana_notification is True

    def test_email_without_task_gid_is_not_asana_notification(self) -> None:
        email = make_regular_email()
        assert email.is_asana_notification is False

    def test_unread_flag_preserved(self) -> None:
        email = make_email(is_unread=False)
        assert email.is_unread is False
