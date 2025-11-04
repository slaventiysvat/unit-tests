import sys
import pathlib
from datetime import datetime, timedelta
import pytest

# --- make git-pycore-hw-03 importable without packaging ---
ROOT = pathlib.Path(__file__).resolve().parents[2]  # .../GoITHomeworkPython
HW03 = ROOT / "git-pycore-hw-03"
if str(HW03) not in sys.path:
    sys.path.insert(0, str(HW03))

from task1 import get_days_from_today


def test_today_returns_zero():
    today_str = datetime.today().strftime("%Y-%m-%d")
    assert get_days_from_today(today_str) == 0


@pytest.mark.parametrize("days", [1, 30, 100, 365, 366, 730])
def test_past_dates_positive(days):
    """If date is in the past by N days -> result is +N"""
    target_date = (datetime.today().date() - timedelta(days=days))
    assert get_days_from_today(target_date.strftime("%Y-%m-%d")) == days


@pytest.mark.parametrize("days", [1, 30, 100, 365, 366, 730])
def test_future_dates_negative(days):
    """If date is in the future by N days -> result is -N"""
    target_date = (datetime.today().date() + timedelta(days=days))
    assert get_days_from_today(target_date.strftime("%Y-%m-%d")) == -days


@pytest.mark.parametrize(
    "bad",
    [
        "2021/10/09",     # wrong separator
        "21-10-09",       # wrong year width
        "2021-13-01",     # invalid month
        "2021-00-10",     # invalid month
        "2021-02-30",     # invalid day
        "not-a-date",     # garbage
        "",               # empty
        "2021-1-1",       # not zero-padded
    ],
)
def test_invalid_format_raises_value_error(bad):
    with pytest.raises(ValueError):
        get_days_from_today(bad)
