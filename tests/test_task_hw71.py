"""
Comprehensive tests for git-pycore-hw-07: Enhanced Assistant Bot with Birthday Management

This test suite covers all enhanced functionality including:
- Birthday field with DD.MM.YYYY validation
- Enhanced Record class with birthday management
- AddressBook with upcoming birthdays functionality
- Complete bot command system with error handling
- Enhanced validation and user experience

Test Categories:
- Unit tests for new Birthday class
- Enhanced Record tests with birthday functionality  
- AddressBook tests with upcoming birthdays
- Bot command tests for all supported operations
- Integration tests and edge cases
- Error handling and validation testing
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add the git-pycore-hw-07 directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'git-pycore-hw-07'))

from task1 import (
    Field, Name, Phone, Birthday, Record, AddressBook,
    input_error, parse_input,
    add_contact, change_contact, show_phone, show_all,
    add_birthday, show_birthday, birthdays
)


class TestBirthday:
    """Test cases for the Birthday class."""
    
    def test_birthday_valid_format(self):
        """Test birthday creation with valid DD.MM.YYYY format."""
        birthday = Birthday("15.06.1990")
        assert birthday.value == "15.06.1990"
        assert isinstance(birthday.date, datetime)
        assert birthday.date.day == 15
        assert birthday.date.month == 6
        assert birthday.date.year == 1990
    
    def test_birthday_invalid_format_raises_error(self):
        """Test birthday with invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
            Birthday("1990-06-15")  # Wrong format
        
        with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
            Birthday("15/06/1990")  # Wrong separator
        
        with pytest.raises(ValueError, match="Invalid date format. Use DD.MM.YYYY"):
            Birthday("invalid")
    
    def test_birthday_edge_dates(self):
        """Test birthday with edge cases."""
        # Leap year
        birthday = Birthday("29.02.2000")
        assert birthday.value == "29.02.2000"
        
        # End of year
        birthday = Birthday("31.12.1999")
        assert birthday.value == "31.12.1999"
        
        # Start of year
        birthday = Birthday("01.01.2000")
        assert birthday.value == "01.01.2000"
    
    def test_birthday_invalid_dates(self):
        """Test birthday with invalid dates."""
        with pytest.raises(ValueError):
            Birthday("32.01.1990")  # Invalid day
        
        with pytest.raises(ValueError):
            Birthday("15.13.1990")  # Invalid month
        
        with pytest.raises(ValueError):
            Birthday("29.02.1999")  # Invalid leap year


class TestEnhancedRecord:
    """Test cases for the enhanced Record class with birthday functionality."""
    
    def test_record_initialization_with_birthday_none(self):
        """Test record initialization has birthday as None."""
        record = Record("John")
        assert record.name.value == "John"
        assert record.phones == []
        assert record.birthday is None
    
    def test_record_add_birthday(self):
        """Test adding birthday to record."""
        record = Record("John")
        record.add_birthday("15.06.1990")
        assert record.birthday is not None
        assert record.birthday.value == "15.06.1990"
    
    def test_record_add_birthday_invalid_format(self):
        """Test adding invalid birthday raises error."""
        record = Record("John")
        with pytest.raises(ValueError, match="Invalid date format"):
            record.add_birthday("invalid")
    
    def test_record_days_to_birthday_no_birthday(self):
        """Test days_to_birthday returns None when no birthday set."""
        record = Record("John")
        assert record.days_to_birthday() is None
    
    def test_record_days_to_birthday_calculation(self):
        """Test days_to_birthday calculation."""
        record = Record("John")
        
        # Set birthday to tomorrow
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
        record.add_birthday(tomorrow)
        
        days = record.days_to_birthday()
        assert days == 1
    
    def test_record_days_to_birthday_next_year(self):
        """Test days_to_birthday when birthday is next year."""
        record = Record("John")
        
        # Set birthday to yesterday (so it's next year)
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")
        record.add_birthday(yesterday)
        
        days = record.days_to_birthday()
        # Should be around 364 days (depends on exact date)
        assert 360 <= days <= 370
    
    def test_record_str_with_birthday(self):
        """Test string representation includes birthday."""
        record = Record("John")
        record.add_phone("1234567890")
        record.add_birthday("15.06.1990")
        
        expected = "Contact name: John, phones: 1234567890, birthday: 15.06.1990"
        assert str(record) == expected
    
    def test_record_str_without_birthday(self):
        """Test string representation without birthday."""
        record = Record("John")
        record.add_phone("1234567890")
        
        expected = "Contact name: John, phones: 1234567890"
        assert str(record) == expected


class TestEnhancedAddressBook:
    """Test cases for the enhanced AddressBook class with birthday functionality."""
    
    def test_get_upcoming_birthdays_empty(self):
        """Test upcoming birthdays with empty address book."""
        book = AddressBook()
        upcoming = book.get_upcoming_birthdays()
        assert upcoming == []
    
    def test_get_upcoming_birthdays_no_birthdays(self):
        """Test upcoming birthdays with contacts but no birthdays."""
        book = AddressBook()
        record = Record("John")
        record.add_phone("1234567890")
        book.add_record(record)
        
        upcoming = book.get_upcoming_birthdays()
        assert upcoming == []
    
    def test_get_upcoming_birthdays_within_week(self):
        """Test upcoming birthdays within next 7 days."""
        book = AddressBook()
        
        # Add contact with birthday in 3 days
        record = Record("John")
        future_date = (datetime.now() + timedelta(days=3)).strftime("%d.%m.%Y")
        record.add_birthday(future_date)
        book.add_record(record)
        
        upcoming = book.get_upcoming_birthdays()
        assert len(upcoming) == 1
        assert upcoming[0]["name"] == "John"
    
    def test_get_upcoming_birthdays_weekend_adjustment(self):
        """Test birthday on weekend gets moved to Monday."""
        book = AddressBook()
        
        # Find next Saturday
        today = datetime.now().date()
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:  # Today is Saturday
            days_until_saturday = 7
        saturday = today + timedelta(days=days_until_saturday)
        
        # Only test if Saturday is within next 7 days
        if (saturday - today).days <= 7:
            record = Record("John")
            record.add_birthday(saturday.strftime("%d.%m.%Y"))
            book.add_record(record)
            
            upcoming = book.get_upcoming_birthdays()
            if upcoming:  # Only assert if we got results
                # Should be moved to Monday
                congratulation_date = datetime.strptime(upcoming[0]["congratulation_date"], "%d.%m.%Y").date()
                assert congratulation_date.weekday() == 0  # Monday
    
    def test_get_upcoming_birthdays_sorting(self):
        """Test upcoming birthdays are sorted by date."""
        book = AddressBook()
        
        # Add contacts with different upcoming birthdays
        record1 = Record("John")
        date1 = (datetime.now() + timedelta(days=5)).strftime("%d.%m.%Y")
        record1.add_birthday(date1)
        book.add_record(record1)
        
        record2 = Record("Jane")
        date2 = (datetime.now() + timedelta(days=2)).strftime("%d.%m.%Y")
        record2.add_birthday(date2)
        book.add_record(record2)
        
        upcoming = book.get_upcoming_birthdays()
        assert len(upcoming) == 2
        # Jane should come first (earlier date)
        assert upcoming[0]["name"] == "Jane"
        assert upcoming[1]["name"] == "John"


class TestInputErrorDecorator:
    """Test cases for the input_error decorator."""
    
    def test_input_error_catches_key_error(self):
        """Test decorator catches KeyError and formats message."""
        @input_error
        def test_func():
            raise KeyError("TestContact")
        
        result = test_func()
        assert "Contact not found: TestContact" in result
    
    def test_input_error_catches_value_error(self):
        """Test decorator catches ValueError and formats message."""
        @input_error
        def test_func():
            raise ValueError("Invalid input provided")
        
        result = test_func()
        assert "Invalid input: Invalid input provided" in result
    
    def test_input_error_catches_index_error(self):
        """Test decorator catches IndexError and formats message."""
        @input_error
        def test_func():
            raise IndexError()
        
        result = test_func()
        assert "Not enough arguments provided" in result
    
    def test_input_error_successful_execution(self):
        """Test decorator doesn't interfere with successful execution."""
        @input_error
        def test_func():
            return "Success"
        
        result = test_func()
        assert result == "Success"


class TestParseInput:
    """Test cases for the parse_input function."""
    
    def test_parse_input_basic_command(self):
        """Test parsing basic command."""
        command, args = parse_input("hello")
        assert command == "hello"
        assert args == []
    
    def test_parse_input_command_with_args(self):
        """Test parsing command with arguments."""
        command, args = parse_input("add John 1234567890")
        assert command == "add"
        assert args == ["John", "1234567890"]
    
    def test_parse_input_empty_string(self):
        """Test parsing empty string."""
        command, args = parse_input("")
        assert command == ""
        assert args == []
    
    def test_parse_input_whitespace_handling(self):
        """Test parsing with extra whitespace."""
        command, args = parse_input("  add   John   1234567890  ")
        assert command == "add"
        assert args == ["John", "1234567890"]


class TestBotCommands:
    """Test cases for bot command functions."""
    
    def test_add_contact_new_contact(self):
        """Test adding new contact."""
        book = AddressBook()
        result = add_contact(["John", "1234567890"], book)
        
        assert result == "Contact added."
        assert "John" in book.data
        assert book.data["John"].phones[0].value == "1234567890"
    
    def test_add_contact_existing_contact(self):
        """Test adding phone to existing contact."""
        book = AddressBook()
        # First add contact
        add_contact(["John", "1234567890"], book)
        # Then add another phone
        result = add_contact(["John", "0987654321"], book)
        
        assert result == "Contact updated."
        assert len(book.data["John"].phones) == 2
    
    def test_add_contact_insufficient_args(self):
        """Test add_contact with insufficient arguments."""
        book = AddressBook()
        result = add_contact(["John"], book)
        
        assert "Not enough arguments provided" in result
    
    def test_change_contact_success(self):
        """Test changing contact phone successfully."""
        book = AddressBook()
        add_contact(["John", "1234567890"], book)
        
        result = change_contact(["John", "1234567890", "0987654321"], book)
        
        assert result == "Contact updated."
        assert book.data["John"].phones[0].value == "0987654321"
    
    def test_change_contact_not_found(self):
        """Test changing phone for non-existent contact."""
        book = AddressBook()
        
        result = change_contact(["John", "1234567890", "0987654321"], book)
        
        assert "Contact not found: John" in result
    
    def test_show_phone_success(self):
        """Test showing phone for existing contact."""
        book = AddressBook()
        add_contact(["John", "1234567890"], book)
        
        result = show_phone(["John"], book)
        
        assert result == "John: 1234567890"
    
    def test_show_phone_multiple_phones(self):
        """Test showing multiple phones for contact."""
        book = AddressBook()
        add_contact(["John", "1234567890"], book)
        add_contact(["John", "0987654321"], book)
        
        result = show_phone(["John"], book)
        
        assert "1234567890" in result
        assert "0987654321" in result
    
    def test_show_phone_not_found(self):
        """Test showing phone for non-existent contact."""
        book = AddressBook()
        
        result = show_phone(["John"], book)
        
        assert "Contact not found: John" in result
    
    def test_show_all_empty(self):
        """Test showing all contacts when book is empty."""
        book = AddressBook()
        
        result = show_all([], book)
        
        assert result == "No contacts in address book."
    
    def test_show_all_with_contacts(self):
        """Test showing all contacts with data."""
        book = AddressBook()
        add_contact(["John", "1234567890"], book)
        add_contact(["Jane", "0987654321"], book)
        
        result = show_all([], book)
        
        assert "John" in result
        assert "Jane" in result
        assert "1234567890" in result
        assert "0987654321" in result
    
    def test_add_birthday_success(self):
        """Test adding birthday successfully."""
        book = AddressBook()
        add_contact(["John", "1234567890"], book)
        
        result = add_birthday(["John", "15.06.1990"], book)
        
        assert result == "Birthday added for John."
        assert book.data["John"].birthday.value == "15.06.1990"
    
    def test_add_birthday_contact_not_found(self):
        """Test adding birthday to non-existent contact."""
        book = AddressBook()
        
        result = add_birthday(["John", "15.06.1990"], book)
        
        assert "Contact not found: John" in result
    
    def test_add_birthday_invalid_format(self):
        """Test adding birthday with invalid format."""
        book = AddressBook()
        add_contact(["John", "1234567890"], book)
        
        result = add_birthday(["John", "invalid"], book)
        
        assert "Invalid input" in result
    
    def test_show_birthday_success(self):
        """Test showing birthday successfully."""
        book = AddressBook()
        add_contact(["John", "1234567890"], book)
        add_birthday(["John", "15.06.1990"], book)
        
        result = show_birthday(["John"], book)
        
        assert result == "John's birthday: 15.06.1990"
    
    def test_show_birthday_no_birthday(self):
        """Test showing birthday when none set."""
        book = AddressBook()
        add_contact(["John", "1234567890"], book)
        
        result = show_birthday(["John"], book)
        
        assert result == "No birthday set for John"
    
    def test_show_birthday_contact_not_found(self):
        """Test showing birthday for non-existent contact."""
        book = AddressBook()
        
        result = show_birthday(["John"], book)
        
        assert "Contact not found: John" in result
    
    def test_birthdays_command_no_upcoming(self):
        """Test birthdays command with no upcoming birthdays."""
        book = AddressBook()
        
        result = birthdays([], book)
        
        assert result == "No upcoming birthdays in the next week."
    
    def test_birthdays_command_with_upcoming(self):
        """Test birthdays command with upcoming birthdays."""
        book = AddressBook()
        add_contact(["John", "1234567890"], book)
        
        # Add birthday in 3 days
        future_date = (datetime.now() + timedelta(days=3)).strftime("%d.%m.%Y")
        add_birthday(["John", future_date], book)
        
        result = birthdays([], book)
        
        assert "Upcoming birthdays:" in result
        assert "John:" in result


class TestIntegrationScenarios:
    """Integration tests for complete bot workflows."""
    
    def test_complete_contact_lifecycle(self):
        """Test complete contact management lifecycle."""
        book = AddressBook()
        
        # Add contact
        result = add_contact(["John", "1234567890"], book)
        assert result == "Contact added."
        
        # Add birthday
        result = add_birthday(["John", "15.06.1990"], book)
        assert result == "Birthday added for John."
        
        # Add second phone
        result = add_contact(["John", "0987654321"], book)
        assert result == "Contact updated."
        
        # Change first phone
        result = change_contact(["John", "1234567890", "5555555555"], book)
        assert result == "Contact updated."
        
        # Show contact info
        result = show_phone(["John"], book)
        assert "5555555555" in result
        assert "0987654321" in result
        
        # Show birthday
        result = show_birthday(["John"], book)
        assert result == "John's birthday: 15.06.1990"
    
    def test_error_handling_scenarios(self):
        """Test various error handling scenarios."""
        book = AddressBook()
        
        # Try to change non-existent contact
        result = change_contact(["NonExistent", "1234567890", "0987654321"], book)
        assert "Contact not found" in result
        
        # Try to show phone for non-existent contact
        result = show_phone(["NonExistent"], book)
        assert "Contact not found" in result
        
        # Try to add birthday to non-existent contact
        result = add_birthday(["NonExistent", "15.06.1990"], book)
        assert "Contact not found" in result
        
        # Try to add invalid phone
        result = add_contact(["John", "invalid"], book)
        assert "Invalid input" in result
        
        # Try to add invalid birthday
        add_contact(["John", "1234567890"], book)
        result = add_birthday(["John", "invalid"], book)
        assert "Invalid input" in result


class TestValidationAndEdgeCases:
    """Test validation and edge cases."""
    
    def test_phone_validation_in_commands(self):
        """Test phone validation in bot commands."""
        book = AddressBook()
        
        # Invalid phone formats
        result = add_contact(["John", "123"], book)
        assert "Invalid input" in result
        
        result = add_contact(["John", "12345678901"], book)
        assert "Invalid input" in result
        
        result = add_contact(["John", "abc1234567"], book)
        assert "Invalid input" in result
    
    def test_birthday_validation_in_commands(self):
        """Test birthday validation in bot commands."""
        book = AddressBook()
        add_contact(["John", "1234567890"], book)
        
        # Invalid birthday formats
        result = add_birthday(["John", "1990-06-15"], book)
        assert "Invalid input" in result
        
        result = add_birthday(["John", "15/06/1990"], book)
        assert "Invalid input" in result
        
        result = add_birthday(["John", "32.01.1990"], book)
        assert "Invalid input" in result
    
    def test_empty_arguments_handling(self):
        """Test handling of empty arguments."""
        book = AddressBook()
        
        # Empty arguments for various commands
        result = add_contact([], book)
        assert "Not enough arguments" in result
        
        result = change_contact(["John"], book)
        assert "Not enough arguments" in result
        
        result = show_phone([], book)
        assert "Not enough arguments" in result
        
        result = add_birthday(["John"], book)
        assert "Not enough arguments" in result
        
        result = show_birthday([], book)
        assert "Not enough arguments" in result


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])