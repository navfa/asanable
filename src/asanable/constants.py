"""Global constants and enums for asanable."""

from enum import StrEnum


class TaskStatus(StrEnum):
    """Asana task completion status."""

    COMPLETED = "completed"
    INCOMPLETE = "incomplete"


class DigestSectionType(StrEnum):
    """Digest section categories."""

    OVERDUE = "overdue"
    TODAY = "today"
    THIS_WEEK = "this_week"
    LATER = "later"
    GMAIL = "gmail"


class ItemSource(StrEnum):
    """Origin source of a digest item."""

    ASANA = "asana"
    GMAIL = "gmail"


ASANA_NOTIFICATION_SENDER = "notifications@asana.com"
