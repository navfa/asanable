"""Clock abstraction — centralizes date.today() for testability."""

from datetime import date


def today() -> date:
    """Return today's date. Mock this function in tests for deterministic behavior."""
    return date.today()
