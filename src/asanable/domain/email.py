"""Gmail message domain entity."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class GmailMessage:
    """Pure domain representation of a Gmail email."""

    message_id: str
    subject: str
    sender: str
    snippet: str
    received_at: datetime
    is_unread: bool
    asana_task_gid: str | None

    @property
    def is_asana_notification(self) -> bool:
        """Check if this email originates from Asana."""
        return self.asana_task_gid is not None
