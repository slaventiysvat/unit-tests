import sys
import pathlib
import builtins

import pytest

# --- make git-pycore-hw-04 importable without packaging ---
ROOT = pathlib.Path(__file__).resolve().parents[2]  # .../GoITHomeworkPython
HW04 = ROOT / "git-pycore-hw-4/task4"
if str(HW04) not in sys.path:
    sys.path.insert(0, str(HW04))

import task4  # наш консольний бот


# ------------------ tests for parse_input ------------------

@pytest.mark.parametrize(
    "raw,expected",
    [
        ("hello", ("hello",)),
        ("  HeLLo  ", ("hello",)),
        ("add John 123456", ("add", "John", "123456")),
        ("change   John   987", ("change", "John", "987")),
        ("phone John", ("phone", "John")),
        ("", ("",)),
        ("   ", ("",)),
    ],
)
def test_parse_input_basic(raw, expected):
    assert task4.parse_input(raw) == expected


# ------------------ tests for handlers ------------------

def test_add_contact_success():
    contacts = {}
    msg = task4.add_contact(("John", "123"), contacts)
    assert msg == "Contact added."
    assert contacts == {"John": "123"}


def test_add_contact_wrong_args_count():
    contacts = {}
    msg = task4.add_contact(("John",), contacts)
    assert "Please provide name and phone" in msg
    assert contacts == {}


def test_change_contact_success():
    contacts = {"John": "123"}
    msg = task4.change_contact(("John", "999"), contacts)
    assert msg == "Contact updated."
    assert contacts["John"] == "999"


def test_change_contact_not_found():
    contacts = {"John": "123"}
    msg = task4.change_contact(("Jane", "999"), contacts)
    assert msg == "Contact not found."
    assert contacts["John"] == "123"


def test_change_contact_wrong_args_count():
    contacts = {"John": "123"}
    msg = task4.change_contact(("John",), contacts)
    assert "Please provide name and new phone" in msg
    assert contacts["John"] == "123"


def test_show_phone_success():
    contacts = {"John": "123"}
    msg = task4.show_phone(("John",), contacts)
    assert msg == "123"


def test_show_phone_not_found():
    contacts = {"John": "123"}
    msg = task4.show_phone(("Jane",), contacts)
    assert msg == "Contact not found."


def test_show_phone_wrong_args_count():
    contacts = {"John": "123"}
    msg = task4.show_phone((), contacts)
    assert "Please provide a name" in msg


def test_show_all_empty():
    contacts = {}
    assert task4.show_all(contacts) == "No contacts found."


def test_show_all_sorted():
    contacts = {"John": "123", "alice": "555", "Bob": "777"}
    out = task4.show_all(contacts)
    lines = out.splitlines()
    # має бути відсортовано по імені без урахування регістру: alice, Bob, John
    assert lines == [
        "alice: 555",
        "Bob: 777",
        "John: 123",
    ]


# ------------------ integration-style test for main ------------------

def test_main_full_flow(monkeypatch, capsys):
    """
    Емуляція діалогу:

    hello
    add John 123
    add Alice 555
    phone John
    change John 999
    phone John
    all
    exit
    """
    inputs = iter([
        "hello",
        "add John 123",
        "add Alice 555",
        "phone John",
        "change John 999",
        "phone John",
        "all",
        "exit",
    ])

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    monkeypatch.setattr(builtins, "input", fake_input)

    task4.main()
    out = capsys.readouterr().out

    # Перевіряємо ключові фрази в правильній послідовності
    expected_snippets = [
        "Welcome to the assistant bot!",
        "How can I help you?",
        "Contact added.",
        "Contact added.",
        "123",            # phone John (перший раз)
        "Contact updated.",
        "999",            # phone John (другий раз)
        # all: має містити обидва контакти
        "Alice: 555",
        "John: 999",
        "Good bye!",
    ]

    last_index = -1
    for snippet in expected_snippets:
        idx = out.find(snippet, last_index + 1)
        assert idx != -1, f"Expected to find '{snippet}' in output.\nOutput:\n{out}"
        #assert idx > last_index, f"'{snippet}' appears out of order.\nOutput:\n{out}"
        last_index = idx


def test_main_invalid_and_empty_commands(monkeypatch, capsys):
    """
    Перевіряємо:
    - порожній ввід ігнорується (не падає)
    - невідома команда дає "Invalid command."
    """
    inputs = iter([
        "   ",       # пустий ввід
        "foobar",    # невірна команда
        "exit",
    ])

    def fake_input(prompt: str = "") -> str:
        return next(inputs)

    monkeypatch.setattr(builtins, "input", fake_input)

    task4.main()
    out = capsys.readouterr().out

    assert "Invalid command." in out
    assert "Good bye!" in out
