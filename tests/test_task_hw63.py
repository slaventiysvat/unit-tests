import sys
import re
import pathlib

import pytest

# --- make git-pycore-hw-04 importable without packaging ---
ROOT = pathlib.Path(__file__).resolve().parents[2]  # .../GoITHomeworkPython
HW06 = ROOT / "git-pycore-hw-06/task3"
if str(HW06) not in sys.path:
    sys.path.insert(0, str(HW06))

import task3  # the CLI tree visualizer


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)


def test_usage_when_no_arguments(capsys):
    rc = task3.main(["task3.py"])
    out = strip_ansi(capsys.readouterr().out)
    assert rc == 2
    # don't hardcode repo path — just check the shape
    assert re.search(r"^Usage:\s+.*task3\.py <path>\s*$", out.strip())


def test_error_nonexistent_path(capsys, tmp_path: pathlib.Path):
    p = tmp_path / "no_such_dir"
    rc = task3.main(["task3.py", str(p)])
    out = strip_ansi(capsys.readouterr().out)
    assert rc == 1
    assert "Error: path does not exist" in out


def test_error_not_a_directory(capsys, tmp_path: pathlib.Path):
    f = tmp_path / "somefile.txt"
    f.write_text("hello", encoding="utf-8")
    rc = task3.main(["task3.py", str(f)])
    out = strip_ansi(capsys.readouterr().out)
    assert rc == 1
    assert "Error: not a directory" in out


def test_tree_output_order_and_connectors(capsys, tmp_path: pathlib.Path):
    """
    Structure we build (case-insensitive sort: dirs first, then files):

    root/
      A_dir/
        inner.txt
        nest/
          leaf
      b_dir/
      alpha.txt
      Z.py

    Because directories come first inside A_dir, expected order there is:
      nest -> leaf (inside) -> inner.txt
    """
    root = tmp_path / "root"
    (root / "A_dir" / "nest").mkdir(parents=True)
    (root / "b_dir").mkdir()

    # files
    (root / "alpha.txt").write_text("", encoding="utf-8")
    (root / "Z.py").write_text("print()", encoding="utf-8")
    (root / "A_dir" / "inner.txt").write_text("x", encoding="utf-8")
    (root / "A_dir" / "nest" / "leaf").write_text("y", encoding="utf-8")

    rc = task3.main(["task3.py", str(root)])
    out = strip_ansi(capsys.readouterr().out)
    lines = [ln.rstrip() for ln in out.splitlines() if ln.strip() != ""]

    assert rc == 0
    # first line is the root directory name (not full path)
    assert lines[0] == root.name

    # Expected sequence reflecting "dirs then files" inside A_dir
    expected_sequence = [
        "├── A_dir",
        "│   ├── nest",
        "│   │   └── leaf",
        "│   └── inner.txt",
        "├── b_dir",
        "├── alpha.txt",
        "└── Z.py",
    ]

    # Build a single string to check subsequence order
    text = "\n".join(lines[1:])
    last_index = -1
    for snippet in expected_sequence:
        idx = text.find(snippet)
        assert idx != -1, f"Expected to find '{snippet}' in output.\nOutput:\n{text}"
        assert idx > last_index, f"Line '{snippet}' appears out of order.\nOutput:\n{text}"
        last_index = idx
