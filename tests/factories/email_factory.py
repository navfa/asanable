"""Factory helpers for creating GmailMessage test instances."""

from datetime import UTC, datetime

from asanable.domain.email import GmailMessage

DEFAULT_MESSAGE_ID = "msg-001"
DEFAULT_SUBJECT = "Task assigned to you"
DEFAULT_SENDER = "notifications@asana.com"
DEFAULT_SNIPPET = "You have a new task"
DEFAULT_RECEIVED_AT = datetime(2025, 6, 10, 9, 30, 0, tzinfo=UTC)


def make_email(
    *,
    message_id: str = DEFAULT_MESSAGE_ID,
    subject: str = DEFAULT_SUBJECT,
    sender: str = DEFAULT_SENDER,
    snippet: str = DEFAULT_SNIPPET,
    received_at: datetime = DEFAULT_RECEIVED_AT,
    is_unread: bool = True,
    asana_task_gid: str | None = "99001",
) -> GmailMessage:
    """Create a GmailMessage with sensible defaults for testing."""
    return GmailMessage(
        message_id=message_id,
        subject=subject,
        sender=sender,
        snippet=snippet,
        received_at=received_at,
        is_unread=is_unread,
        asana_task_gid=asana_task_gid,
    )


def make_asana_notification(**overrides) -> GmailMessage:
    """Create an email that is an Asana notification."""
    defaults = {
        "sender": "notifications@asana.com",
        "subject": "You've been assigned a task",
        "asana_task_gid": "55555",
    }
    defaults.update(overrides)
    return make_email(**defaults)


def make_regular_email(**overrides) -> GmailMessage:
    """Create a regular (non-Asana) email."""
    defaults = {
        "sender": "colleague@company.com",
        "subject": "Meeting notes",
        "asana_task_gid": None,
    }
    defaults.update(overrides)
    return make_email(**defaults)
