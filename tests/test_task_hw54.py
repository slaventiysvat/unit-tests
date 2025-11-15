#!/usr/bin/env python3
"""
Тести для завдання 4: Консольний бот з декораторами для обробки помилок

Перевіряємо коректність роботи декоратора input_error та обробку всіх типів помилок:
KeyError, ValueError, IndexError
"""

import sys
import pathlib
import builtins
from io import StringIO
from unittest.mock import patch
import pytest

# Додаємо шлях до модуля task4
ROOT = pathlib.Path(__file__).resolve().parents[2]
TASK4_PATH = ROOT / "git-pycore-hw-05" / "task4"
if str(TASK4_PATH) not in sys.path:
    sys.path.insert(0, str(TASK4_PATH))

from task4 import (
    input_error,
    parse_input,
    add_contact,
    change_contact,
    show_phone,
    show_all,
    delete_contact,
    search_contacts,
    show_help
)


class TestInputErrorDecorator:
    """Тести декоратора input_error"""
    
    def test_decorator_preserves_function_metadata(self):
        """Тест: Декоратор зберігає метадані функції"""
        @input_error
        def test_func():
            """Test function"""
            pass
        
        assert test_func.__name__ == "test_func"
        assert test_func.__doc__ == "Test function"
    
    def test_keyerror_handling(self):
        """Тест: Обробка KeyError"""
        @input_error
        def func_with_keyerror():
            raise KeyError("test_name")
        
        result = func_with_keyerror()
        assert "Contact 'test_name' not found." in result
    
    def test_valueerror_handling_not_enough_values(self):
        """Тест: Обробка ValueError - недостатньо аргументів"""
        @input_error
        def func_with_valueerror():
            raise ValueError("not enough values to unpack (expected 2, got 1)")
        
        result = func_with_valueerror()
        assert result == "Enter the argument for the command"
    
    def test_valueerror_handling_phone(self):
        """Тест: Обробка ValueError з phone"""
        @input_error
        def func_with_phone_error():
            raise ValueError("Give me name and phone please.")
        
        result = func_with_phone_error()
        assert result == "Give me name and phone please."
    
    def test_valueerror_handling_name(self):
        """Тест: Обробка ValueError з name"""
        @input_error
        def func_with_name_error():
            raise ValueError("Enter user name")
        
        result = func_with_name_error()
        assert result == "Enter user name"
    
    def test_indexerror_handling(self):
        """Тест: Обробка IndexError"""
        @input_error
        def func_with_indexerror():
            raise IndexError("list index out of range")
        
        result = func_with_indexerror()
        assert result == "Enter the argument for the command"
    
    def test_general_exception_handling(self):
        """Тест: Обробка загальних винятків"""
        @input_error
        def func_with_general_error():
            raise RuntimeError("Something went wrong")
        
        result = func_with_general_error()
        assert "An error occurred: Something went wrong" in result
    
    def test_successful_execution(self):
        """Тест: Успішне виконання без помилок"""
        @input_error
        def successful_func():
            return "Success!"
        
        result = successful_func()
        assert result == "Success!"


class TestParseInput:
    """Тести функції parse_input"""
    
    @pytest.mark.parametrize("raw,expected", [
        ("hello", ("hello",)),
        ("  HeLLo  ", ("hello",)),
        ("add John 123456", ("add", "John", "123456")),
        ("change   John   987", ("change", "John", "987")),
        ("phone John", ("phone", "John")),
        ("", ("",)),
        ("   ", ("",)),
        ("ADD Alice 555", ("add", "Alice", "555")),
        ("delete Bob", ("delete", "Bob")),
        ("search 050", ("search", "050")),
    ])
    def test_parse_input_cases(self, raw, expected):
        """Тест: Різні випадки парсингу введення"""
        assert parse_input(raw) == expected
    
    def test_parse_input_invalid_type(self):
        """Тест: Некоректний тип введення"""
        assert parse_input(None) == ("",)
        assert parse_input(123) == ("",)


class TestAddContact:
    """Тести функції add_contact з декоратором"""
    
    def test_add_contact_success(self):
        """Тест: Успішне додавання контакту"""
        contacts = {}
        result = add_contact(("John", "123456"), contacts)
        
        assert result == "Contact added."
        assert contacts == {"John": "123456"}
    
    def test_add_contact_insufficient_args(self):
        """Тест: Недостатньо аргументів"""
        contacts = {}
        
        # Один аргумент
        result = add_contact(("John",), contacts)
        assert result == "Give me name and phone please."
        assert contacts == {}
        
        # Без аргументів
        result = add_contact((), contacts)
        assert result == "Give me name and phone please."
        assert contacts == {}
    
    def test_add_contact_empty_values(self):
        """Тест: Порожні значення"""
        contacts = {}
        
        result = add_contact(("", "123"), contacts)
        assert result == "Give me name and phone please."
        assert contacts == {}
        
        result = add_contact(("John", ""), contacts)
        assert result == "Give me name and phone please."
        assert contacts == {}
    
    def test_add_contact_already_exists(self):
        """Тест: Контакт уже існує"""
        contacts = {"John": "123456"}
        
        result = add_contact(("John", "789"), contacts)
        assert "already exists" in result
        assert contacts["John"] == "123456"  # Не змінився


class TestChangeContact:
    """Тести функції change_contact з декоратором"""
    
    def test_change_contact_success(self):
        """Тест: Успішна зміна контакту"""
        contacts = {"John": "123456"}
        
        result = change_contact(("John", "789012"), contacts)
        assert "updated from 123456 to 789012" in result
        assert contacts["John"] == "789012"
    
    def test_change_contact_not_found(self):
        """Тест: Контакт не знайдено"""
        contacts = {"John": "123456"}
        
        result = change_contact(("Jane", "789"), contacts)
        assert "Contact 'Jane' not found." in result
        assert contacts == {"John": "123456"}
    
    def test_change_contact_insufficient_args(self):
        """Тест: Недостатньо аргументів"""
        contacts = {"John": "123456"}
        
        result = change_contact(("John",), contacts)
        assert result == "Give me name and phone please."
        
        result = change_contact((), contacts)
        assert result == "Give me name and phone please."
    
    def test_change_contact_empty_values(self):
        """Тест: Порожні значення"""
        contacts = {"John": "123456"}
        
        result = change_contact(("", "789"), contacts)
        assert result == "Give me name and phone please."
        
        result = change_contact(("John", ""), contacts)
        assert result == "Give me name and phone please."


class TestShowPhone:
    """Тести функції show_phone з декоратором"""
    
    def test_show_phone_success(self):
        """Тест: Успішне отримання телефону"""
        contacts = {"John": "123456"}
        
        result = show_phone(("John",), contacts)
        assert result == "John: 123456"
    
    def test_show_phone_not_found(self):
        """Тест: Контакт не знайдено"""
        contacts = {"John": "123456"}
        
        result = show_phone(("Jane",), contacts)
        assert "Contact 'Jane' not found." in result
    
    def test_show_phone_no_args(self):
        """Тест: Відсутні аргументи"""
        contacts = {"John": "123456"}
        
        result = show_phone((), contacts)
        assert result == "Enter user name"
    
    def test_show_phone_empty_name(self):
        """Тест: Порожнє ім'я"""
        contacts = {"John": "123456"}
        
        result = show_phone(("",), contacts)
        assert result == "Enter user name"


class TestShowAll:
    """Тести функції show_all з декоратором"""
    
    def test_show_all_empty(self):
        """Тест: Порожня адресна книга"""
        result = show_all({})
        assert result == "No contacts found."
    
    def test_show_all_single_contact(self):
        """Тест: Один контакт"""
        contacts = {"John": "123456"}
        result = show_all(contacts)
        assert result == "John: 123456"
    
    def test_show_all_multiple_contacts_sorted(self):
        """Тест: Множинні контакти, відсортовані"""
        contacts = {"John": "123", "alice": "555", "Bob": "777"}
        result = show_all(contacts)
        
        lines = result.split("\n")
        expected = ["alice: 555", "Bob: 777", "John: 123"]
        assert lines == expected


class TestDeleteContact:
    """Тести функції delete_contact з декоратором"""
    
    def test_delete_contact_success(self):
        """Тест: Успішне видалення контакту"""
        contacts = {"John": "123456", "Alice": "789012"}
        
        result = delete_contact(("John",), contacts)
        assert "Contact 'John' (123456) deleted." in result
        assert contacts == {"Alice": "789012"}
    
    def test_delete_contact_not_found(self):
        """Тест: Контакт не знайдено"""
        contacts = {"John": "123456"}
        
        result = delete_contact(("Jane",), contacts)
        assert "Contact 'Jane' not found." in result
        assert contacts == {"John": "123456"}
    
    def test_delete_contact_no_args(self):
        """Тест: Відсутні аргументи"""
        contacts = {"John": "123456"}
        
        result = delete_contact((), contacts)
        assert result == "Enter user name"
        assert contacts == {"John": "123456"}
    
    def test_delete_contact_empty_name(self):
        """Тест: Порожнє ім'я"""
        contacts = {"John": "123456"}
        
        result = delete_contact(("",), contacts)
        assert result == "Enter user name"
        assert contacts == {"John": "123456"}


class TestSearchContacts:
    """Тести функції search_contacts з декоратором"""
    
    def test_search_by_name(self):
        """Тест: Пошук за іменем"""
        contacts = {"John": "123456", "Jane": "789012", "Bob": "555111"}
        
        result = search_contacts(("jo",), contacts)
        assert "John: 123456" in result
        assert "Found 1 contact(s)" in result
    
    def test_search_by_phone(self):
        """Тест: Пошук за телефоном"""
        contacts = {"John": "123456", "Jane": "789012", "Bob": "555111"}
        
        result = search_contacts(("555",), contacts)
        assert "Bob: 555111" in result
        assert "Found 1 contact(s)" in result
    
    def test_search_multiple_matches(self):
        """Тест: Множинні збіги"""
        contacts = {"John": "123456", "Johnny": "789012", "Jane": "123999"}
        
        result = search_contacts(("123",), contacts)
        assert "Found 2 contact(s)" in result
        assert "John: 123456" in result
        assert "Jane: 123999" in result
    
    def test_search_no_matches(self):
        """Тест: Відсутні збіги"""
        contacts = {"John": "123456", "Jane": "789012"}
        
        result = search_contacts(("xyz",), contacts)
        assert "No contacts found matching 'xyz'" in result
    
    def test_search_no_args(self):
        """Тест: Відсутні аргументи"""
        contacts = {"John": "123456"}
        
        result = search_contacts((), contacts)
        assert result == "Enter search query"
    
    def test_search_empty_query(self):
        """Тест: Порожній пошуковий запит"""
        contacts = {"John": "123456"}
        
        result = search_contacts(("",), contacts)
        assert result == "Enter search query"


class TestShowHelp:
    """Тести функції show_help"""
    
    def test_show_help_content(self):
        """Тест: Зміст довідки"""
        result = show_help()
        
        expected_commands = ["hello", "add", "change", "phone", "delete", "search", "all", "help", "close", "exit"]
        
        for cmd in expected_commands:
            assert cmd in result
        
        assert "Examples:" in result
        assert "Available commands:" in result


class TestIntegration:
    """Інтеграційні тести"""
    
    def test_full_workflow_with_error_handling(self):
        """Тест: Повний робочий процес з обробкою помилок"""
        contacts = {}
        
        # Успішне додавання
        result = add_contact(("John", "123456"), contacts)
        assert result == "Contact added."
        
        # Помилка - недостатньо аргументів
        result = add_contact(("Alice",), contacts)
        assert result == "Give me name and phone please."
        
        # Успішна зміна
        result = change_contact(("John", "789012"), contacts)
        assert "updated" in result
        
        # Помилка - контакт не знайдено
        result = change_contact(("Bob", "555"), contacts)
        assert "not found" in result
        
        # Успішний пошук
        result = show_phone(("John",), contacts)
        assert "John: 789012" in result
        
        # Помилка - контакт не знайдено
        result = show_phone(("Alice",), contacts)
        assert "not found" in result
    
    def test_decorator_error_messages_consistency(self):
        """Тест: Консистентність повідомлень про помилки"""
        contacts = {}
        
        # Всі функції повинні однаково обробляти відсутність аргументів
        functions_needing_args = [
            (add_contact, "Give me name and phone please."),
            (change_contact, "Give me name and phone please."),
            (show_phone, "Enter user name"),
            (delete_contact, "Enter user name"),
            (search_contacts, "Enter search query")
        ]
        
        for func, expected_msg in functions_needing_args:
            result = func((), contacts)
            assert result == expected_msg, f"Function {func.__name__} returned: {result}"


class TestMainFunction:
    """Тести головної функції (інтеграційні)"""
    
    def test_main_with_valid_commands(self, monkeypatch, capsys):
        """Тест: Головна функція з коректними командами"""
        inputs = iter([
            "hello",
            "add John 123456",
            "phone John",
            "all",
            "exit"
        ])
        
        def fake_input(prompt=""):
            return next(inputs)
        
        monkeypatch.setattr(builtins, "input", fake_input)
        
        # Імпортуємо main тут, щоб уникнути конфліктів
        from task4 import main
        main()
        
        output = capsys.readouterr().out
        
        expected_snippets = [
            "Welcome to the assistant bot!",
            "How can I help you?",
            "Contact added.",
            "John: 123456",
            "John: 123456",  # В результаті all
            "Good bye!"
        ]
        
        for snippet in expected_snippets:
            assert snippet in output, f"Expected '{snippet}' in output"
    
    def test_main_with_error_handling(self, monkeypatch, capsys):
        """Тест: Головна функція з обробкою помилок"""
        inputs = iter([
            "add",               # Недостатньо аргументів
            "phone",             # Недостатньо аргументів
            "phone Unknown",     # Контакт не знайдено
            "invalid_command",   # Невідома команда
            "",                  # Порожній ввід
            "exit"
        ])
        
        def fake_input(prompt=""):
            return next(inputs)
        
        monkeypatch.setattr(builtins, "input", fake_input)
        
        from task4 import main
        main()
        
        output = capsys.readouterr().out
        
        # Перевіряємо, що помилки обробляються коректно
        assert "Give me name and phone please." in output
        assert "Enter user name" in output
        assert "not found" in output
        assert "Invalid command" in output
        assert "Good bye!" in output


if __name__ == "__main__":
    # Запуск тестів з детальним виводом
    pytest.main([__file__, "-v", "--tb=short"])
