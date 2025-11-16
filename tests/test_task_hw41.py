import sys
import pathlib
import pytest

# --- make git-pycore-hw-04 importable without packaging ---
ROOT = pathlib.Path(__file__).resolve().parents[2]  # .../GoITHomeworkPython
HW04 = ROOT / "git-pycore-hw-4/task1"
if str(HW04) not in sys.path:
    sys.path.insert(0, str(HW04))

from task1 import total_salary


def write_file(p: pathlib.Path, content: str) -> pathlib.Path:
    p.write_text(content, encoding="utf-8")
    return p


def test_basic_three_records(tmp_path: pathlib.Path):
    f = write_file(
        tmp_path / "devs.txt",
        "Alex Korp,3000\nNikita Borisenko,2000\nSitarama Raju,1000\n",
    )
    total, avg = total_salary(str(f))
    assert total == 6000
    assert avg == 2000.0


def test_ignores_empty_and_malformed_lines(tmp_path: pathlib.Path):
    # Bad lines should be skipped silently
    f = write_file(
        tmp_path / "mixed.txt",
        "\n"                         # empty
        "BadLineWithoutComma\n"      # malformed
        "John Doe,\n"                # no salary
        "Jane,abc\n"                 # non-numeric salary
        "Dev One,1000\n"             # valid
        "Dev Two,2000\n"             # valid
    )
    total, avg = total_salary(str(f))
    assert total == 3000
    assert avg == 1500.0


def test_empty_file_returns_zeroes(tmp_path: pathlib.Path):
    f = write_file(tmp_path / "empty.txt", "")
    assert total_salary(str(f)) == (0, 0.0)


def test_missing_file_returns_zeroes(tmp_path: pathlib.Path):
    missing = tmp_path / "no_such_file.txt"
    assert not missing.exists()
    assert total_salary(str(missing)) == (0, 0.0)


def test_average_rounding_two_decimals(tmp_path: pathlib.Path):
    # 10 + 11 + 11 = 32; avg = 10.666..., rounded to 10.67
    f = write_file(
        tmp_path / "round.txt",
        "A,10\nB,11\nC,11\n",
    )
    total, avg = total_salary(str(f))
    assert total == 32
    assert avg == 10.67


def test_unicode_names_and_utf8(tmp_path: pathlib.Path):
    f = write_file(
        tmp_path / "utf8.txt",
        "Свят,2500\nВалерія,3500\n",
    )
    total, avg = total_salary(str(f))
    assert total == 6000
    assert avg == 3000.0
