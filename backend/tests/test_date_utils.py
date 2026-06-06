"""Tests for date_utils module."""

from datetime import date

from app.utils.date_utils import upcoming_sunday, week_range


def test_upcoming_sunday_from_monday():
    # Mon Jun 2 2025 (weekday=0) → Sun Jun 8
    today = date(2025, 6, 2)
    assert upcoming_sunday(today) == date(2025, 6, 8)


def test_upcoming_sunday_from_saturday():
    # Sat Jun 7 2025 (weekday=5) → Sun Jun 8
    today = date(2025, 6, 7)
    assert upcoming_sunday(today) == date(2025, 6, 8)


def test_upcoming_sunday_from_sunday():
    # Sun Jun 8 2025 (weekday=6) → skip to next week: Sun Jun 15
    today = date(2025, 6, 8)
    assert upcoming_sunday(today) == date(2025, 6, 15)


def test_week_range_returns_sunday_to_saturday():
    # Mon Jun 2 2025 → Sun Jun 8 .. Sat Jun 14
    today = date(2025, 6, 2)
    start, end = week_range(today)
    assert start == date(2025, 6, 8)
    assert end == date(2025, 6, 14)
    assert (end - start).days == 6


def test_upcoming_sunday_with_explicit_date():
    # Tue Jun 3 2025 (weekday=1) → Sun Jun 8
    today = date(2025, 6, 3)
    assert upcoming_sunday(today) == date(2025, 6, 8)