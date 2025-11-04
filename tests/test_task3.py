import sys
import re
import pathlib
import pytest

# --- make git-pycore-hw-03 importable without packaging ---
ROOT = pathlib.Path(__file__).resolve().parents[2]  # .../GoITHomeworkPython
HW03 = ROOT / "git-pycore-hw-03"
if str(HW03) not in sys.path:
    sys.path.insert(0, str(HW03))

from task3 import normalize_phone


def only_plus_digits(s: str) -> bool:
    return re.fullmatch(r"\+\d+", s) is not None


def test_examples_from_prompt():
    raw_numbers = [
        "067\t123 4567",
        "(095) 234-5678\n",
        "+380 44 123 4567",
        "380501234567",
        "    +38(050)123-32-34",
        "     0503451234",
        "(050)8889900",
        "38050-111-22-22",
        "38050 111 22 11   ",
    ]
    expected = [
        "+380671234567",
        "+380952345678",
        "+380441234567",
        "+380501234567",
        "+380501233234",
        "+380503451234",
        "+380508889900",
        "+380501112222",
        "+380501112211",
    ]
    assert [normalize_phone(n) for n in raw_numbers] == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("+380501234567", "+380501234567"),  # already normalized
        ("380441112233", "+380441112233"),   # add missing '+'
        ("0501234567", "+380501234567"),     # local -> add +38
        ("  (044) 321-00-00 ", "+380443210000"),
        ("++380501234567", "+380501234567"), # collapse multiple '+' to one
    ],
)
def test_various_normalizations(raw, expected):
    assert normalize_phone(raw) == expected


@pytest.mark.parametrize("bad", [None, 12345, 38.0, [], {}])
def test_non_string_raises(bad):
    with pytest.raises(ValueError):
        normalize_phone(bad)  # type: ignore[arg-type]


def test_only_plus_and_digits_in_output():
    samples = [
        "067 000 00 00",
        "+380 67 000 00 01",
        "380-67-000-00-02",
        "(067)0000003",
        "    +38(067)000-00-04  ",
    ]
    for s in samples:
        out = normalize_phone(s)
        assert only_plus_digits(out), f"Output contains invalid characters: {out}"
