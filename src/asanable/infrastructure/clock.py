"""Clock abstraction — centralizes date logic for testability."""

from datetime import date, timedelta

DAYS_IN_WEEK = 7


def today() -> date:
    """Return today's date. Mock this function in tests for deterministic behavior."""
    return date.today()


def is_due_today(due_on: date | None) -> bool:
    """Check if a date is today."""
    return due_on == today()


def is_due_this_week(due_on: date | None) -> bool:
    """Check if a date falls within the next 7 days (excluding today)."""
    if due_on is None:
        return False
    now = today()
    return now < due_on <= now + timedelta(days=DAYS_IN_WEEK)
