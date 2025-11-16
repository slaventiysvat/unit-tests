"""
Comprehensive tests for git-pycore-hw-08: Enhanced Bot with Persistent Data Storage

This test suite covers all enhanced functionality including:
- Pickle serialization/deserialization with save_data() and load_data()
- Persistent data storage and recovery across sessions  
- Robust error handling for file operations (missing files, corrupted data, permission errors)
- Data integrity validation after save/load cycles
- All previous functionality maintained (contacts, phones, birthdays, CLI commands)
- Edge cases and error scenarios for file system operations

Test Categories:
- Unit tests for save_data() and load_data() functions
- Data integrity tests for complex AddressBook objects
- Error handling tests for file system issues
- Integration tests for persistence in main application flow
- Backward compatibility tests with all previous features
- Performance tests for large address books
"""

import pytest
import sys
import os
import tempfile
import pickle
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

# Add the git-pycore-hw-08/task1 directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'git-pycore-hw-08', 'task1'))

from task1 import (
    Field, Name, Phone, Birthday, Record, AddressBook,
    save_data, load_data,
    add_contact, change_contact, show_phone, show_all,
    add_birthday, show_birthday, birthdays,
    parse_input, input_error
)


class TestPersistentStorage:
    """Test cases for persistent data storage functionality."""
    
    def setup_method(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_addressbook.pkl")
    
    def teardown_method(self):
        """Clean up test files."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        # Clean up any remaining files in temp dir
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except OSError:
            pass  # Ignore cleanup errors
    
    def create_sample_addressbook(self) -> AddressBook:
        """Create sample address book with test data."""
        book = AddressBook()
        
        # Add contact with phone and birthday
        john = Record("John")
        john.add_phone("1234567890")
        john.add_phone("0987654321")
        john.add_birthday("15.06.1990")
        book.add_record(john)
        
        # Add contact with only phone
        jane = Record("Jane")
        jane.add_phone("5555555555")
        book.add_record(jane)
        
        # Add contact with only birthday
        alice = Record("Alice")
        alice.add_birthday("25.12.1985")
        book.add_record(alice)
        
        return book
    
    def test_save_data_success(self):
        """Test successful data saving."""
        book = self.create_sample_addressbook()
        
        result = save_data(book, self.test_file)
        
        assert result is True
        assert os.path.exists(self.test_file)
        
        # Verify file content by loading it back
        with open(self.test_file, "rb") as f:
            loaded_book = pickle.load(f)
        
        assert isinstance(loaded_book, AddressBook)
        assert len(loaded_book.data) == 3
        assert "John" in loaded_book.data
    
    def test_save_data_with_default_filename(self):
        """Test saving with default filename."""
        book = AddressBook()
        john = Record("John")
        john.add_phone("1234567890")
        book.add_record(john)
        
        # Change to temp directory for this test
        old_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            result = save_data(book)
            
            assert result is True
            assert os.path.exists("addressbook.pkl")
        finally:
            os.chdir(old_cwd)
    
    def test_save_data_file_permission_error(self):
        """Test save_data with file permission error."""
        book = AddressBook()
        
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            result = save_data(book, self.test_file)
        
        assert result is False
    
    def test_save_data_pickle_error(self):
        """Test save_data with pickle serialization error."""
        book = AddressBook()
        
        with patch("pickle.dump", side_effect=pickle.PickleError("Pickle error")):
            result = save_data(book, self.test_file)
        
        assert result is False
    
    def test_load_data_success(self):
        """Test successful data loading."""
        # First save some data
        original_book = self.create_sample_addressbook()
        save_data(original_book, self.test_file)
        
        # Load it back
        loaded_book = load_data(self.test_file)
        
        assert isinstance(loaded_book, AddressBook)
        assert len(loaded_book.data) == 3
        
        # Verify John's data
        john = loaded_book.find("John")
        assert john is not None
        assert len(john.phones) == 2
        assert john.phones[0].value == "1234567890"
        assert john.phones[1].value == "0987654321"
        assert john.birthday.value == "15.06.1990"
        
        # Verify Jane's data
        jane = loaded_book.find("Jane")
        assert jane is not None
        assert len(jane.phones) == 1
        assert jane.phones[0].value == "5555555555"
        assert jane.birthday is None
        
        # Verify Alice's data
        alice = loaded_book.find("Alice")
        assert alice is not None
        assert len(alice.phones) == 0
        assert alice.birthday.value == "25.12.1985"
    
    def test_load_data_file_not_found(self):
        """Test load_data with non-existent file."""
        non_existent_file = os.path.join(self.temp_dir, "nonexistent.pkl")
        
        loaded_book = load_data(non_existent_file)
        
        assert isinstance(loaded_book, AddressBook)
        assert len(loaded_book.data) == 0
    
    def test_load_data_corrupted_file(self):
        """Test load_data with corrupted file."""
        # Create a corrupted file
        with open(self.test_file, "wb") as f:
            f.write(b"corrupted data that is not pickle")
        
        loaded_book = load_data(self.test_file)
        
        assert isinstance(loaded_book, AddressBook)
        assert len(loaded_book.data) == 0
    
    def test_load_data_invalid_object_type(self):
        """Test load_data with file containing wrong object type."""
        # Save a different object type
        with open(self.test_file, "wb") as f:
            pickle.dump({"not": "an address book"}, f)
        
        loaded_book = load_data(self.test_file)
        
        assert isinstance(loaded_book, AddressBook)
        assert len(loaded_book.data) == 0
    
    def test_load_data_permission_error(self):
        """Test load_data with file permission error."""
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            loaded_book = load_data(self.test_file)
        
        assert isinstance(loaded_book, AddressBook)
        assert len(loaded_book.data) == 0
    
    def test_load_data_with_default_filename(self):
        """Test loading with default filename."""
        book = AddressBook()
        john = Record("John")
        john.add_phone("1234567890")
        book.add_record(john)
        
        # Change to temp directory for this test
        old_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            save_data(book)  # Save with default name
            loaded_book = load_data()  # Load with default name
            
            assert len(loaded_book.data) == 1
            assert "John" in loaded_book.data
        finally:
            os.chdir(old_cwd)


class TestDataIntegrity:
    """Test cases for data integrity across save/load cycles."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_integrity.pkl")
    
    def teardown_method(self):
        """Clean up test files."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_complex_data_integrity(self):
        """Test integrity of complex address book data."""
        original = AddressBook()
        
        # Create complex data
        for i in range(10):
            record = Record(f"Contact{i}")
            record.add_phone(f"123456789{i}")
            if i % 2 == 0:
                record.add_phone(f"987654321{i}")
            if i % 3 == 0:
                record.add_birthday(f"{i+1:02d}.01.199{i}")
            original.add_record(record)
        
        # Save and load
        assert save_data(original, self.test_file)
        loaded = load_data(self.test_file)
        
        # Verify integrity
        assert len(loaded.data) == len(original.data)
        
        for name in original.data:
            orig_record = original.data[name]
            loaded_record = loaded.data[name]
            
            assert orig_record.name.value == loaded_record.name.value
            assert len(orig_record.phones) == len(loaded_record.phones)
            
            for i, phone in enumerate(orig_record.phones):
                assert phone.value == loaded_record.phones[i].value
            
            if orig_record.birthday:
                assert orig_record.birthday.value == loaded_record.birthday.value
            else:
                assert loaded_record.birthday is None
    
    def test_unicode_data_integrity(self):
        """Test integrity of unicode data."""
        book = AddressBook()
        
        # Add contact with unicode name
        record = Record("Олександр")
        record.add_phone("1234567890")
        record.add_birthday("01.01.1990")
        book.add_record(record)
        
        # Save and load
        assert save_data(book, self.test_file)
        loaded = load_data(self.test_file)
        
        # Verify unicode preservation
        assert "Олександр" in loaded.data
        record = loaded.find("Олександр")
        assert record.name.value == "Олександр"
        assert record.phones[0].value == "1234567890"
        assert record.birthday.value == "01.01.1990"
    
    def test_empty_addressbook_integrity(self):
        """Test integrity of empty address book."""
        empty_book = AddressBook()
        
        # Save and load empty book
        assert save_data(empty_book, self.test_file)
        loaded = load_data(self.test_file)
        
        assert isinstance(loaded, AddressBook)
        assert len(loaded.data) == 0
    
    def test_multiple_save_load_cycles(self):
        """Test data integrity across multiple save/load cycles."""
        book = AddressBook()
        john = Record("John")
        john.add_phone("1234567890")
        book.add_record(john)
        
        # Multiple save/load cycles
        for i in range(5):
            assert save_data(book, self.test_file)
            book = load_data(self.test_file)
            
            # Add more data each cycle
            if f"Contact{i}" not in book.data:
                new_record = Record(f"Contact{i}")
                new_record.add_phone(f"55500000{i:02d}")  # Ensure 10 digits
                book.add_record(new_record)
        
        # Verify final state
        assert len(book.data) == 6  # John + 5 contacts
        assert "John" in book.data
        for i in range(5):
            assert f"Contact{i}" in book.data


class TestBackwardCompatibility:
    """Test cases to ensure all previous functionality is maintained."""
    
    def test_all_previous_commands_work_with_persistence(self):
        """Test that all CLI commands work with persistent storage."""
        book = AddressBook()
        
        # Test add command
        result = add_contact(["John", "1234567890"], book)
        assert "Contact added" in result
        
        # Test change command
        result = change_contact(["John", "1234567890", "0987654321"], book)
        assert "Contact updated" in result
        
        # Test phone command
        result = show_phone(["John"], book)
        assert "John: 0987654321" == result
        
        # Test add-birthday command
        result = add_birthday(["John", "15.06.1990"], book)
        assert "Birthday added" in result
        
        # Test show-birthday command
        result = show_birthday(["John"], book)
        assert "John's birthday: 15.06.1990" == result
        
        # Test all command
        result = show_all([], book)
        assert "John" in result
        assert "0987654321" in result
        assert "15.06.1990" in result
        
        # Test birthdays command
        result = birthdays([], book)
        # Should work without error (may or may not have upcoming birthdays)
        assert isinstance(result, str)
    
    def test_address_book_methods_work_after_load(self):
        """Test AddressBook methods work correctly after loading from file."""
        temp_file = tempfile.mktemp(suffix=".pkl")
        
        try:
            # Create and save address book
            original = AddressBook()
            john = Record("John")
            john.add_phone("1234567890")
            john.add_birthday("15.06.1990")
            original.add_record(john)
            
            save_data(original, temp_file)
            
            # Load and test methods
            loaded = load_data(temp_file)
            
            # Test find method
            found = loaded.find("John")
            assert found is not None
            assert found.name.value == "John"
            
            # Test add_record method
            jane = Record("Jane")
            jane.add_phone("5555555555")
            loaded.add_record(jane)
            assert "Jane" in loaded.data
            
            # Test delete method
            loaded.delete("Jane")
            assert "Jane" not in loaded.data
            
            # Test get_upcoming_birthdays method
            upcoming = loaded.get_upcoming_birthdays()
            assert isinstance(upcoming, list)
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


class TestErrorHandling:
    """Test cases for error handling in persistence operations."""
    
    def test_save_data_handles_io_errors_gracefully(self):
        """Test save_data handles various IO errors gracefully."""
        book = AddressBook()
        
        # Test with invalid path
        result = save_data(book, "/invalid/path/file.pkl")
        assert result is False
        
        # Test with directory as filename
        temp_dir = tempfile.mkdtemp()
        try:
            result = save_data(book, temp_dir)
            assert result is False
        finally:
            os.rmdir(temp_dir)
    
    def test_load_data_handles_all_error_types(self):
        """Test load_data handles all types of errors gracefully."""
        # Test with directory instead of file
        temp_dir = tempfile.mkdtemp()
        try:
            loaded = load_data(temp_dir)
            assert isinstance(loaded, AddressBook)
            assert len(loaded.data) == 0
        finally:
            os.rmdir(temp_dir)
        
        # Test with empty file
        temp_file = tempfile.mktemp()
        try:
            with open(temp_file, "wb") as f:
                pass  # Create empty file
            
            loaded = load_data(temp_file)
            assert isinstance(loaded, AddressBook)
            assert len(loaded.data) == 0
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


class TestPerformance:
    """Test cases for performance with large datasets."""
    
    def test_large_addressbook_save_load(self):
        """Test save/load performance with large address book."""
        book = AddressBook()
        
        # Create large dataset (1000 contacts)
        for i in range(1000):
            record = Record(f"Contact{i:04d}")
            record.add_phone(f"12345{i:05d}")
            if i % 2 == 0:
                record.add_birthday(f"{(i % 28) + 1:02d}.{(i % 12) + 1:02d}.{1990 + (i % 30)}")
            book.add_record(record)
        
        temp_file = tempfile.mktemp(suffix=".pkl")
        
        try:
            # Test save
            result = save_data(book, temp_file)
            assert result is True
            
            # Test load
            loaded = load_data(temp_file)
            assert len(loaded.data) == 1000
            
            # Spot check some data
            assert "Contact0000" in loaded.data
            assert "Contact0999" in loaded.data
            
            contact_500 = loaded.find("Contact0500")
            assert contact_500 is not None
            assert contact_500.phones[0].value == "1234500500"
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


class TestEdgeCases:
    """Test cases for edge cases and boundary conditions."""
    
    def test_save_load_with_special_characters_in_filename(self):
        """Test save/load with special characters in filename."""
        book = AddressBook()
        john = Record("John")
        john.add_phone("1234567890")
        book.add_record(john)
        
        # Test with spaces and unicode in filename
        temp_dir = tempfile.mkdtemp()
        test_file = os.path.join(temp_dir, "test файл with spaces.pkl")
        
        try:
            result = save_data(book, test_file)
            if result:  # Only test load if save succeeded (depends on filesystem)
                loaded = load_data(test_file)
                assert len(loaded.data) == 1
                assert "John" in loaded.data
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
            os.rmdir(temp_dir)
    
    def test_concurrent_access_simulation(self):
        """Test behavior with simulated concurrent access."""
        temp_file = tempfile.mktemp(suffix=".pkl")
        
        try:
            book1 = AddressBook()
            john = Record("John")
            john.add_phone("1234567890")
            book1.add_record(john)
            
            # Save from first "process"
            save_data(book1, temp_file)
            
            # Load from second "process"
            book2 = load_data(temp_file)
            
            # Modify in second "process"
            jane = Record("Jane")
            jane.add_phone("5555555555")
            book2.add_record(jane)
            
            # Save from second "process"
            save_data(book2, temp_file)
            
            # Load again to verify
            final_book = load_data(temp_file)
            assert len(final_book.data) == 2
            assert "John" in final_book.data
            assert "Jane" in final_book.data
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])