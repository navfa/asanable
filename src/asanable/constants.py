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

GMAIL_SCOPE_READONLY = "https://www.googleapis.com/auth/gmail.readonly"
GMAIL_USER_ME = "me"
GMAIL_LABEL_UNREAD = "UNREAD"
GMAIL_FORMAT_FULL = "full"

ASANA_TASK_URL_PATTERN = r"app\.asana\.com/\d+/\d+/(\d+)"

# Priority scores — higher = more urgent
SCORE_OVERDUE = 100
SCORE_TODAY = 80
SCORE_THIS_WEEK = 60
SCORE_UNREAD_EMAIL = 40
SCORE_LATER = 20
SCORE_NO_DATE = 10

# CLI display styles per section
SECTION_STYLES: dict[str, dict[str, str]] = {
    "overdue": {"color": "red", "title": "Overdue", "icon": "!"},
    "today": {"color": "yellow", "title": "Today", "icon": ">"},
    "this_week": {"color": "blue", "title": "This Week", "icon": "-"},
    "later": {"color": "dim", "title": "Later", "icon": " "},
    "gmail": {"color": "green", "title": "Gmail", "icon": "@"},
}

COLUMN_TITLE = "Title"
COLUMN_PROJECT = "Project"
COLUMN_DUE = "Due"
COLUMN_SOURCE = "Source"
NO_DATE_LABEL = "-"
NO_PROJECT_LABEL = "-"
