"""Date utilities for the Week Workflow feature.

Guards always submit constraints for the upcoming Sunday through Saturday.
"""

from datetime import date, timedelta


def upcoming_sunday(today: date = None) -> date:
    """Return the next Sunday strictly in the future.

    If today is Sunday → return next week's Sunday (+7 days).

    Args:
        today: The reference date. Defaults to date.today().

    Returns:
        The next upcoming Sunday.
    """
    if today is None:
        today = date.today()

    days_ahead = (6 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7  # today is Sunday, skip to next
    return today + timedelta(days=days_ahead)


def week_range(today: date = None) -> tuple[date, date]:
    """Return the (sunday, saturday) tuple for the upcoming guard week.

    Args:
        today: The reference date. Defaults to date.today().

    Returns:
        A tuple of (upcoming_sunday, upcoming_saturday).
    """
    sunday = upcoming_sunday(today)
    return (sunday, sunday + timedelta(days=6))