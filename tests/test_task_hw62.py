import sys
import pathlib
import pytest

# --- make git-pycore-hw-04 importable without packaging ---
ROOT = pathlib.Path(__file__).resolve().parents[2]  # .../GoITHomeworkPython
HW06 = ROOT / "git-pycore-hw-06/task2"
if str(HW06) not in sys.path:
    sys.path.insert(0, str(HW06))

from task2 import get_cats_info


def write_file(p: pathlib.Path, content: str, newline: str = "\n") -> pathlib.Path:
    # Python 3.9+: 
    with p.open("w", encoding="utf-8", newline=newline) as f:
        f.write(content)
    return p



def test_basic_five_records(tmp_path: pathlib.Path):
    f = write_file(
        tmp_path / "cats.txt",
        (
            "60b90c1c13067a15887e1ae1,Tayson,3\n"
            "60b90c2413067a15887e1ae2,Vika,1\n"
            "60b90c2e13067a15887e1ae3,Barsik,2\n"
            "60b90c3b13067a15887e1ae4,Simon,12\n"
            "60b90c4613067a15887e1ae5,Tessi,5\n"
        ),
    )
    out = get_cats_info(str(f))
    assert out == [
        {"id": "60b90c1c13067a15887e1ae1", "name": "Tayson", "age": "3"},
        {"id": "60b90c2413067a15887e1ae2", "name": "Vika", "age": "1"},
        {"id": "60b90c2e13067a15887e1ae3", "name": "Barsik", "age": "2"},
        {"id": "60b90c3b13067a15887e1ae4", "name": "Simon", "age": "12"},
        {"id": "60b90c4613067a15887e1ae5", "name": "Tessi", "age": "5"},
    ]


def test_whitespace_and_empty_lines_are_ignored(tmp_path: pathlib.Path):
    f = write_file(
        tmp_path / "cats2.txt",
        (
            "\n"
            "  1 ,  Murka  , 4  \n"
            "\t\n"
            "2,Bars , 3\n"
        ),
    )
    out = get_cats_info(str(f))
    assert out == [
        {"id": "1", "name": "Murka", "age": "4"},
        {"id": "2", "name": "Bars", "age": "3"},
    ]


def test_malformed_lines_are_skipped(tmp_path: pathlib.Path):
    f = write_file(
        tmp_path / "cats_bad.txt",
        (
            "id_only\n"                   # no commas
            "a,b\n"                       # not enough fields
            "x,y,z,extra\n"               # too many fields
            "10,Tom,7\n"                  # valid
            "11, Jerry ,  8 \n"           # valid with spaces
        ),
    )
    out = get_cats_info(str(f))
    assert out == [
        {"id": "10", "name": "Tom", "age": "7"},
        {"id": "11", "name": "Jerry", "age": "8"},
    ]


def test_empty_file_returns_empty_list(tmp_path: pathlib.Path):
    f = write_file(tmp_path / "empty.txt", "")
    assert get_cats_info(str(f)) == []


def test_missing_file_returns_empty_list(tmp_path: pathlib.Path):
    missing = tmp_path / "no_such.txt"
    assert not missing.exists()
    assert get_cats_info(str(missing)) == []


def test_unicode_and_utf8(tmp_path: pathlib.Path):
    f = write_file(
        tmp_path / "cats_utf8.txt",
        "укр-ід,Мурчик,2\nпес-ід,Барсик,5\n",  # just to check unicode in names/ids
    )
    out = get_cats_info(str(f))
    assert out == [
        {"id": "укр-ід", "name": "Мурчик", "age": "2"},
        {"id": "пес-ід", "name": "Барсик", "age": "5"},
    ]


def test_crlf_is_ok(tmp_path: pathlib.Path):
    p = tmp_path / "crlf.txt"
    write_file(p, "1,Tom,1\r\n2,Sam,2\r\n", newline="\r\n")
    out = get_cats_info(str(p))
    assert out == [
        {"id": "1", "name": "Tom", "age": "1"},
        {"id": "2", "name": "Sam", "age": "2"},
    ]

