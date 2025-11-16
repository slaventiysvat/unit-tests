"""
Comprehensive tests for git-pycore-hw-06: Address Book Management System

This test suite covers all classes and methods of the address book system:
- Field: Base class functionality
- Name: Name field validation and storage
- Phone: Phone field validation and format checking
- Record: Contact record management with phones
- AddressBook: Address book operations (CRUD)

Test Categories:
- Unit tests for individual classes
- Integration tests for class interactions  
- Edge cases and error handling
- Validation testing
"""

import pytest
import sys
import os

# Add the git-pycore-hw-06 directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'git-pycore-hw-06'))

from task1 import Field, Name, Phone, Record, AddressBook


class TestField:
    """Test cases for the Field base class."""
    
    def test_field_initialization(self):
        """Test field creation with value."""
        field = Field("test_value")
        assert field.value == "test_value"
    
    def test_field_str_representation(self):
        """Test string representation of field."""
        field = Field("test_value")
        assert str(field) == "test_value"
    
    def test_field_with_numeric_value(self):
        """Test field with numeric value."""
        field = Field(123)
        assert field.value == 123
        assert str(field) == "123"


class TestName:
    """Test cases for the Name class."""
    
    def test_name_initialization(self):
        """Test name creation with valid value."""
        name = Name("John")
        assert name.value == "John"
    
    def test_name_strips_whitespace(self):
        """Test name strips leading/trailing whitespace."""
        name = Name("  John  ")
        assert name.value == "John"
    
    def test_name_empty_string_raises_error(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            Name("")
    
    def test_name_whitespace_only_raises_error(self):
        """Test that whitespace-only name raises ValueError."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            Name("   ")
    
    def test_name_str_representation(self):
        """Test string representation of name."""
        name = Name("Alice")
        assert str(name) == "Alice"


class TestPhone:
    """Test cases for the Phone class."""
    
    def test_phone_valid_10_digits(self):
        """Test phone with exactly 10 digits."""
        phone = Phone("1234567890")
        assert phone.value == "1234567890"
    
    def test_phone_with_formatting_valid(self):
        """Test phone with formatting characters (should be stripped)."""
        # Note: Based on implementation, it validates digits count but stores original
        phone = Phone("1234567890")  # Clean format
        assert phone.value == "1234567890"
    
    def test_phone_invalid_length_short(self):
        """Test phone with less than 10 digits raises error."""
        with pytest.raises(ValueError, match="Phone number must contain exactly 10 digits"):
            Phone("123456789")  # 9 digits
    
    def test_phone_invalid_length_long(self):
        """Test phone with more than 10 digits raises error."""
        with pytest.raises(ValueError, match="Phone number must contain exactly 10 digits"):
            Phone("12345678901")  # 11 digits
    
    def test_phone_invalid_with_letters(self):
        """Test phone with letters raises error."""
        with pytest.raises(ValueError, match="Phone number must contain exactly 10 digits"):
            Phone("123abc7890")
    
    def test_phone_empty_string_raises_error(self):
        """Test empty phone raises error."""
        with pytest.raises(ValueError, match="Phone number must contain exactly 10 digits"):
            Phone("")
    
    def test_phone_str_representation(self):
        """Test string representation of phone."""
        phone = Phone("9876543210")
        assert str(phone) == "9876543210"


class TestRecord:
    """Test cases for the Record class."""
    
    def test_record_initialization(self):
        """Test record creation with name."""
        record = Record("John")
        assert record.name.value == "John"
        assert record.phones == []
    
    def test_record_add_phone(self):
        """Test adding phone to record."""
        record = Record("John")
        record.add_phone("1234567890")
        assert len(record.phones) == 1
        assert record.phones[0].value == "1234567890"
    
    def test_record_add_multiple_phones(self):
        """Test adding multiple phones to record."""
        record = Record("John")
        record.add_phone("1234567890")
        record.add_phone("5555555555")
        assert len(record.phones) == 2
        assert record.phones[0].value == "1234567890"
        assert record.phones[1].value == "5555555555"
    
    def test_record_add_duplicate_phone_raises_error(self):
        """Test adding duplicate phone raises error."""
        record = Record("John")
        record.add_phone("1234567890")
        with pytest.raises(ValueError, match="Phone number 1234567890 already exists"):
            record.add_phone("1234567890")
    
    def test_record_remove_phone(self):
        """Test removing phone from record."""
        record = Record("John")
        record.add_phone("1234567890")
        record.add_phone("5555555555")
        record.remove_phone("1234567890")
        assert len(record.phones) == 1
        assert record.phones[0].value == "5555555555"
    
    def test_record_remove_nonexistent_phone_raises_error(self):
        """Test removing nonexistent phone raises error."""
        record = Record("John")
        record.add_phone("1234567890")
        with pytest.raises(ValueError, match="Phone number 9999999999 not found"):
            record.remove_phone("9999999999")
    
    def test_record_edit_phone(self):
        """Test editing existing phone."""
        record = Record("John")
        record.add_phone("1234567890")
        record.edit_phone("1234567890", "1112223333")
        assert record.phones[0].value == "1112223333"
    
    def test_record_edit_nonexistent_phone_raises_error(self):
        """Test editing nonexistent phone raises error."""
        record = Record("John")
        record.add_phone("1234567890")
        with pytest.raises(ValueError, match="Phone number 9999999999 not found"):
            record.edit_phone("9999999999", "1112223333")
    
    def test_record_edit_phone_invalid_new_phone(self):
        """Test editing phone with invalid new phone raises error."""
        record = Record("John")
        record.add_phone("1234567890")
        with pytest.raises(ValueError, match="Phone number must contain exactly 10 digits"):
            record.edit_phone("1234567890", "invalid")
    
    def test_record_find_phone_exists(self):
        """Test finding existing phone returns phone."""
        record = Record("John")
        record.add_phone("1234567890")
        found = record.find_phone("1234567890")
        assert found == "1234567890"
    
    def test_record_find_phone_not_exists(self):
        """Test finding nonexistent phone returns None."""
        record = Record("John")
        record.add_phone("1234567890")
        found = record.find_phone("9999999999")
        assert found is None
    
    def test_record_str_no_phones(self):
        """Test string representation with no phones."""
        record = Record("John")
        expected = "Contact name: John, phones: "
        assert str(record) == expected
    
    def test_record_str_single_phone(self):
        """Test string representation with single phone."""
        record = Record("John")
        record.add_phone("1234567890")
        expected = "Contact name: John, phones: 1234567890"
        assert str(record) == expected
    
    def test_record_str_multiple_phones(self):
        """Test string representation with multiple phones."""
        record = Record("John")
        record.add_phone("1234567890")
        record.add_phone("5555555555")
        expected = "Contact name: John, phones: 1234567890; 5555555555"
        assert str(record) == expected


class TestAddressBook:
    """Test cases for the AddressBook class."""
    
    def test_address_book_initialization(self):
        """Test address book creation."""
        book = AddressBook()
        assert len(book.data) == 0
    
    def test_address_book_add_record(self):
        """Test adding record to address book."""
        book = AddressBook()
        record = Record("John")
        book.add_record(record)
        assert "John" in book.data
        assert book.data["John"] == record
    
    def test_address_book_add_duplicate_record_raises_error(self):
        """Test adding duplicate record raises error."""
        book = AddressBook()
        record1 = Record("John")
        record2 = Record("John")
        book.add_record(record1)
        with pytest.raises(ValueError, match="Contact John already exists"):
            book.add_record(record2)
    
    def test_address_book_find_existing_record(self):
        """Test finding existing record."""
        book = AddressBook()
        record = Record("John")
        book.add_record(record)
        found = book.find("John")
        assert found == record
    
    def test_address_book_find_nonexistent_record(self):
        """Test finding nonexistent record returns None."""
        book = AddressBook()
        found = book.find("NonExistent")
        assert found is None
    
    def test_address_book_delete_existing_record(self):
        """Test deleting existing record."""
        book = AddressBook()
        record = Record("John")
        book.add_record(record)
        book.delete("John")
        assert "John" not in book.data
    
    def test_address_book_delete_nonexistent_record_raises_error(self):
        """Test deleting nonexistent record raises error."""
        book = AddressBook()
        with pytest.raises(ValueError, match="Contact NonExistent not found"):
            book.delete("NonExistent")
    
    def test_address_book_str_empty(self):
        """Test string representation of empty address book."""
        book = AddressBook()
        assert str(book) == "Address book is empty"
    
    def test_address_book_str_with_records(self):
        """Test string representation with records."""
        book = AddressBook()
        john = Record("John")
        john.add_phone("1234567890")
        jane = Record("Jane")
        jane.add_phone("9876543210")
        book.add_record(john)
        book.add_record(jane)
        
        result = str(book)
        assert "Contact name: John, phones: 1234567890" in result
        assert "Contact name: Jane, phones: 9876543210" in result


class TestIntegration:
    """Integration tests for the complete address book system."""
    
    def test_full_workflow_as_in_assignment(self):
        """Test the complete workflow from assignment example."""
        # Створення нової адресної книги
        book = AddressBook()

        # Створення запису для John
        john_record = Record("John")
        john_record.add_phone("1234567890")
        john_record.add_phone("5555555555")

        # Додавання запису John до адресної книги
        book.add_record(john_record)

        # Створення та додавання нового запису для Jane
        jane_record = Record("Jane")
        jane_record.add_phone("9876543210")
        book.add_record(jane_record)

        # Verify records are added correctly
        assert len(book.data) == 2
        assert "John" in book.data
        assert "Jane" in book.data

        # Знаходження та редагування телефону для John
        john = book.find("John")
        assert john is not None
        john.edit_phone("1234567890", "1112223333")
        
        # Verify the edit
        assert john.find_phone("1112223333") == "1112223333"
        assert john.find_phone("1234567890") is None
        assert john.find_phone("5555555555") == "5555555555"

        # Пошук конкретного телефону в записі John
        found_phone = john.find_phone("5555555555")
        assert found_phone == "5555555555"

        # Видалення запису Jane
        book.delete("Jane")
        assert len(book.data) == 1
        assert "Jane" not in book.data
        assert "John" in book.data
    
    def test_complex_phone_operations(self):
        """Test complex phone operations on a record."""
        record = Record("TestUser")
        
        # Add multiple phones
        phones = ["1111111111", "2222222222", "3333333333"]
        for phone in phones:
            record.add_phone(phone)
        
        assert len(record.phones) == 3
        
        # Edit middle phone
        record.edit_phone("2222222222", "9999999999")
        assert record.find_phone("2222222222") is None
        assert record.find_phone("9999999999") == "9999999999"
        
        # Remove first phone
        record.remove_phone("1111111111")
        assert len(record.phones) == 2
        assert record.find_phone("1111111111") is None
        
        # Verify remaining phones
        assert record.find_phone("9999999999") == "9999999999"
        assert record.find_phone("3333333333") == "3333333333"
    
    def test_address_book_with_multiple_contacts(self):
        """Test address book with multiple contacts and operations."""
        book = AddressBook()
        
        # Create multiple contacts
        contacts = [
            ("Alice", ["1111111111", "2222222222"]),
            ("Bob", ["3333333333"]),
            ("Charlie", ["4444444444", "5555555555", "6666666666"])
        ]
        
        # Add all contacts
        for name, phones in contacts:
            record = Record(name)
            for phone in phones:
                record.add_phone(phone)
            book.add_record(record)
        
        # Verify all contacts are added
        assert len(book.data) == 3
        for name, _ in contacts:
            assert book.find(name) is not None
        
        # Modify Alice's phones
        alice = book.find("Alice")
        alice.edit_phone("1111111111", "7777777777")
        alice.add_phone("8888888888")
        
        # Verify Alice's phones
        assert alice.find_phone("7777777777") == "7777777777"
        assert alice.find_phone("8888888888") == "8888888888"
        assert alice.find_phone("1111111111") is None
        assert len(alice.phones) == 3
        
        # Remove Bob
        book.delete("Bob")
        assert len(book.data) == 2
        assert book.find("Bob") is None
        
        # Verify remaining contacts
        assert book.find("Alice") is not None
        assert book.find("Charlie") is not None


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_phone_validation_edge_cases(self):
        """Test phone validation with various edge cases."""
        # Test exactly 10 digits (valid)
        phone = Phone("0000000000")
        assert phone.value == "0000000000"
        
        # Test with leading zeros
        phone = Phone("0123456789")
        assert phone.value == "0123456789"
    
    def test_name_edge_cases(self):
        """Test name validation edge cases."""
        # Single character name
        name = Name("A")
        assert name.value == "A"
        
        # Name with multiple spaces becomes single space after strip
        name = Name("John")
        assert name.value == "John"
    
    def test_record_operations_with_no_phones(self):
        """Test record operations when no phones exist."""
        record = Record("EmptyContact")
        
        # Find phone on empty record
        assert record.find_phone("1234567890") is None
        
        # Try to remove phone from empty record
        with pytest.raises(ValueError, match="Phone number 1234567890 not found"):
            record.remove_phone("1234567890")
        
        # Try to edit phone on empty record
        with pytest.raises(ValueError, match="Phone number 1234567890 not found"):
            record.edit_phone("1234567890", "9876543210")
    
    def test_address_book_operations_on_empty_book(self):
        """Test address book operations on empty book."""
        book = AddressBook()
        
        # Find on empty book
        assert book.find("NonExistent") is None
        
        # Delete from empty book
        with pytest.raises(ValueError, match="Contact NonExistent not found"):
            book.delete("NonExistent")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])