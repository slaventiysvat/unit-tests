import sys
import pathlib
from datetime import date as _real_date

import pytest

# --- make git-pycore-hw-03 importable without packaging ---
ROOT = pathlib.Path(__file__).resolve().parents[2]  # .../GoITHomeworkPython
HW03 = ROOT / "git-pycore-hw-03"
if str(HW03) not in sys.path:
    sys.path.insert(0, str(HW03))

import task4


def set_today(monkeypatch, y, m, d):
    """Monkeypatch task4.date.today() to a fixed date (y-m-d)."""
    class FixedDate(_real_date):
        @classmethod
        def today(cls):
            return cls(y, m, d)
    monkeypatch.setattr(task4, "date", FixedDate)


def test_includes_today_no_shift(monkeypatch):
    # Today = 2024-01-23 (Tue). Birthday exactly today -> included, no shift.
    set_today(monkeypatch, 2024, 1, 23)
    users = [{"name": "John", "birthday": "1990.01.23"}]
    out = task4.get_upcoming_birthdays(users)
    assert out == [{"name": "John", "congratulation_date": "2024.01.23"}]


def test_weekend_shift_saturday(monkeypatch):
    # Today = 2024-01-23 (Tue). Birthday on Sat 2024-01-27 -> shift to Mon 2024-01-29.
    set_today(monkeypatch, 2024, 1, 23)
    users = [{"name": "Jane", "birthday": "1988.01.27"}]
    out = task4.get_upcoming_birthdays(users)
    assert out == [{"name": "Jane", "congratulation_date": "2024.01.29"}]


def test_weekend_shift_sunday(monkeypatch):
    # Today = 2024-01-23 (Tue). Birthday on Sun 2024-01-28 -> shift to Mon 2024-01-29.
    set_today(monkeypatch, 2024, 1, 23)
    users = [{"name": "Max", "birthday": "1995.01.28"}]
    out = task4.get_upcoming_birthdays(users)
    assert out == [{"name": "Max", "congratulation_date": "2024.01.29"}]


def test_excludes_past_birthdays_this_year(monkeypatch):
    # Today = 2024-01-23; a birthday on 2024-01-22 already passed -> next occurrence 2025-01-22 (not in window).
    set_today(monkeypatch, 2024, 1, 23)
    users = [{"name": "Kate", "birthday": "1992.01.22"}]
    out = task4.get_upcoming_birthdays(users)
    assert out == []


def test_cross_year_window_includes_next_year(monkeypatch):
    # Today = 2024-12-30; birthday Jan 02 -> next occurrence 2025-01-02 within next 7 days
    set_today(monkeypatch, 2024, 12, 30)
    users = [{"name": "Oleg", "birthday": "1991.01.02"}]
    out = task4.get_upcoming_birthdays(users)
    assert out == [{"name": "Oleg", "congratulation_date": "2025.01.02"}]


def test_boundary_inclusive_today_plus_7(monkeypatch):
    # Today = 2024-01-23; today+7 = 2024-01-30. Birthday on 30th is included.
    set_today(monkeypatch, 2024, 1, 23)
    users = [{"name": "Ann", "birthday": "1980.01.30"}]
    out = task4.get_upcoming_birthdays(users)
    assert out == [{"name": "Ann", "congratulation_date": "2024.01.30"}]


def test_monday_shift_can_land_beyond_7_day_window(monkeypatch):
    # Inclusion uses the actual birthday date; shift may land beyond horizon.
    # Today = 2024-01-23 (Tue), birthday Sun 2024-01-28 is within 7 days,
    # but congratulation_date is Mon 2024-01-29 (still within here, but test documents behavior).
    set_today(monkeypatch, 2024, 1, 23)
    users = [{"name": "SunGuy", "birthday": "2000.01.28"}]
    out = task4.get_upcoming_birthdays(users)
    assert out == [{"name": "SunGuy", "congratulation_date": "2024.01.29"}]


def test_multiple_users_sorted_by_congrats_date(monkeypatch):
    set_today(monkeypatch, 2024, 1, 23)
    users = [
        {"name": "B", "birthday": "1990.01.27"},  # Sat -> 2024-01-29
        {"name": "A", "birthday": "1990.01.23"},  # Tue -> 2024-01-23
        {"name": "C", "birthday": "1990.01.28"},  # Sun -> 2024-01-29
    ]
    out = task4.get_upcoming_birthdays(users)
    assert out == [
        {"name": "A", "congratulation_date": "2024.01.23"},
        {"name": "B", "congratulation_date": "2024.01.29"},
        {"name": "C", "congratulation_date": "2024.01.29"},
    ]


def test_invalid_records_are_skipped(monkeypatch):
    set_today(monkeypatch, 2024, 1, 23)
    users = [
        {"name": "Valid1", "birthday": "2000.01.23"},
        {"name": "BadFmt", "birthday": "2000-01-23"},  # wrong format
        {"name": "NoBday"},                              # missing key
        {"birthday": "2001.01.23"},                      # missing name
        {"name": "Valid2", "birthday": "1999.01.27"},  # Sat -> shift
    ]
    out = task4.get_upcoming_birthdays(users)
    assert out == [
        {"name": "Valid1", "congratulation_date": "2024.01.23"},
        {"name": "Valid2", "congratulation_date": "2024.01.29"},
    ]
