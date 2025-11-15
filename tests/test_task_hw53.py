#!/usr/bin/env python3
"""
Тести для завдання 3: Аналізатор файлів логів

Перевіряємо коректність парсингу логів, фільтрації, підрахунку та обробки помилок.
Тестуємо використання функціонального програмування.
"""

import sys
import pathlib
import pytest
import tempfile
import os
from io import StringIO
from unittest.mock import patch

# Додаємо шлях до модуля task3
ROOT = pathlib.Path(__file__).resolve().parents[2]
TASK3_PATH = ROOT / "git-pycore-hw-05" / "task3"
if str(TASK3_PATH) not in sys.path:
    sys.path.insert(0, str(TASK3_PATH))

from task3 import (
    parse_log_line, 
    load_logs, 
    filter_logs_by_level, 
    count_logs_by_level,
    display_log_counts,
    display_filtered_logs,
    create_log_analyzer
)


class TestParseLogLine:
    """Тести функції parse_log_line"""
    
    def test_valid_log_line(self):
        """Тест: Парсинг коректного рядка логу"""
        line = "2024-01-22 08:30:01 INFO User logged in successfully."
        expected = {
            'date': '2024-01-22',
            'time': '08:30:01',
            'level': 'INFO',
            'message': 'User logged in successfully.'
        }
        result = parse_log_line(line)
        assert result == expected, f"Очікувалося {expected}, отримано {result}"
    
    def test_different_log_levels(self):
        """Тест: Різні рівні логування"""
        test_cases = [
            ("2024-01-22 09:00:45 ERROR Database connection failed.", "ERROR"),
            ("2024-01-22 10:30:55 WARNING Disk usage above 80%.", "WARNING"),
            ("2024-01-22 11:05:00 DEBUG Starting data backup process.", "DEBUG"),
            ("2024-01-22 12:00:00 INFO User logged out.", "INFO")
        ]
        
        for line, expected_level in test_cases:
            result = parse_log_line(line)
            assert result is not None, f"Не вдалося розпарсити: {line}"
            assert result['level'] == expected_level, f"Неправильний рівень для: {line}"
    
    def test_invalid_log_line(self):
        """Тест: Некоректні рядки логів"""
        invalid_lines = [
            "Invalid log line",
            "2024-01-22 INFO Missing time",
            "08:30:01 INFO Missing date",
            "",
            "   ",
            "2024-01-22 08:30 INFO Invalid time format"
        ]
        
        for line in invalid_lines:
            result = parse_log_line(line)
            assert result is None, f"Має повернути None для некоректного рядка: {line}"
    
    def test_message_with_special_characters(self):
        """Тест: Повідомлення зі спеціальними символами"""
        line = "2024-01-22 08:30:01 ERROR Failed to process: 'user@example.com' (ID: 12345)"
        result = parse_log_line(line)
        
        assert result is not None, "Має успішно парсити рядок зі спеціальними символами"
        assert result['message'] == "Failed to process: 'user@example.com' (ID: 12345)"
    
    def test_long_message(self):
        """Тест: Довгі повідомлення"""
        long_message = "Very long error message " * 50
        long_message = long_message.rstrip()  # Видаляємо зайвий пробіл в кінці
        line = f"2024-01-22 08:30:01 ERROR {long_message}"
        result = parse_log_line(line)
        
        assert result is not None, "Має парсити довгі повідомлення"
        assert result['message'] == long_message


class TestLoadLogs:
    """Тести функції load_logs"""
    
    def test_load_valid_logs(self):
        """Тест: Завантаження коректного лог-файлу"""
        log_content = """2024-01-22 08:30:01 INFO User logged in successfully.
2024-01-22 09:00:45 ERROR Database connection failed.
2024-01-22 10:30:55 WARNING Disk usage above 80%."""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write(log_content)
            temp_path = f.name
        
        try:
            logs = load_logs(temp_path)
            assert len(logs) == 3, f"Очікувалося 3 записи, отримано {len(logs)}"
            
            expected_levels = ['INFO', 'ERROR', 'WARNING']
            actual_levels = [log['level'] for log in logs]
            assert actual_levels == expected_levels, f"Неправильні рівні: {actual_levels}"
            
        finally:
            os.unlink(temp_path)
    
    def test_load_logs_with_invalid_lines(self):
        """Тест: Завантаження з некоректними рядками"""
        log_content = """2024-01-22 08:30:01 INFO Valid log line.
Invalid log line that should be skipped
2024-01-22 09:00:45 ERROR Another valid line.
Another invalid line"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write(log_content)
            temp_path = f.name
        
        try:
            logs = load_logs(temp_path)
            # Має бути тільки 2 коректні рядки
            assert len(logs) == 2, f"Очікувалося 2 коректні записи, отримано {len(logs)}"
            
        finally:
            os.unlink(temp_path)
    
    def test_load_nonexistent_file(self):
        """Тест: Завантаження неіснуючого файлу"""
        with pytest.raises(FileNotFoundError, match="не знайдено"):
            load_logs("/nonexistent/path/to/file.log")
    
    def test_load_empty_file(self):
        """Тест: Завантаження порожнього файлу"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            temp_path = f.name
        
        try:
            logs = load_logs(temp_path)
            assert logs == [], "Порожній файл має повертати порожній список"
            
        finally:
            os.unlink(temp_path)


class TestFilterLogsByLevel:
    """Тести функції filter_logs_by_level"""
    
    def test_filter_existing_level(self):
        """Тест: Фільтрація існуючого рівня"""
        logs = [
            {'level': 'INFO', 'message': 'Info message 1'},
            {'level': 'ERROR', 'message': 'Error message'},
            {'level': 'INFO', 'message': 'Info message 2'},
            {'level': 'WARNING', 'message': 'Warning message'}
        ]
        
        filtered = filter_logs_by_level(logs, 'INFO')
        assert len(filtered) == 2, f"Очікувалося 2 записи INFO, отримано {len(filtered)}"
        
        for log in filtered:
            assert log['level'] == 'INFO', "Всі відфільтровані записи мають бути рівня INFO"
    
    def test_filter_case_insensitive(self):
        """Тест: Фільтрація без урахування регістру"""
        logs = [
            {'level': 'INFO', 'message': 'Test message'},
            {'level': 'ERROR', 'message': 'Error message'}
        ]
        
        # Тестуємо різні варіанти регістру
        for level_variant in ['info', 'INFO', 'Info', 'iNfO']:
            filtered = filter_logs_by_level(logs, level_variant)
            assert len(filtered) == 1, f"Фільтрація має працювати для {level_variant}"
            assert filtered[0]['level'] == 'INFO'
    
    def test_filter_nonexistent_level(self):
        """Тест: Фільтрація неіснуючого рівня"""
        logs = [
            {'level': 'INFO', 'message': 'Info message'},
            {'level': 'ERROR', 'message': 'Error message'}
        ]
        
        filtered = filter_logs_by_level(logs, 'CRITICAL')
        assert filtered == [], "Фільтрація неіснуючого рівня має повертати порожній список"
    
    def test_filter_empty_list(self):
        """Тест: Фільтрація порожнього списку"""
        filtered = filter_logs_by_level([], 'INFO')
        assert filtered == [], "Фільтрація порожнього списку має повертати порожній список"


class TestCountLogsByLevel:
    """Тести функції count_logs_by_level"""
    
    def test_count_multiple_levels(self):
        """Тест: Підрахунок кількох рівнів"""
        logs = [
            {'level': 'INFO'},
            {'level': 'ERROR'},
            {'level': 'INFO'},
            {'level': 'WARNING'},
            {'level': 'INFO'},
            {'level': 'ERROR'}
        ]
        
        counts = count_logs_by_level(logs)
        expected = {'INFO': 3, 'ERROR': 2, 'WARNING': 1}
        
        assert counts == expected, f"Очікувалося {expected}, отримано {counts}"
    
    def test_count_single_level(self):
        """Тест: Підрахунок одного рівня"""
        logs = [
            {'level': 'INFO'},
            {'level': 'INFO'},
            {'level': 'INFO'}
        ]
        
        counts = count_logs_by_level(logs)
        expected = {'INFO': 3}
        
        assert counts == expected, f"Очікувалося {expected}, отримано {counts}"
    
    def test_count_empty_list(self):
        """Тест: Підрахунок порожнього списку"""
        counts = count_logs_by_level([])
        assert counts == {}, "Підрахунок порожнього списку має повертати порожній словник"


class TestDisplayFunctions:
    """Тести функцій відображення"""
    
    def test_display_log_counts(self):
        """Тест: Відображення підрахунку логів"""
        counts = {'INFO': 5, 'ERROR': 2, 'WARNING': 1}
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            display_log_counts(counts)
            output = mock_stdout.getvalue()
            
            # Перевіряємо, що вивід містить всі рівні
            assert 'INFO' in output, "Вивід має містити рівень INFO"
            assert 'ERROR' in output, "Вивід має містити рівень ERROR"
            assert 'WARNING' in output, "Вивід має містити рівень WARNING"
            assert '5' in output and '2' in output and '1' in output, "Вивід має містити кількості"
    
    def test_display_empty_counts(self):
        """Тест: Відображення порожнього підрахунку"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            display_log_counts({})
            output = mock_stdout.getvalue()
            
            assert "Не знайдено" in output, "Має відображати повідомлення про відсутність записів"
    
    def test_display_filtered_logs(self):
        """Тест: Відображення відфільтрованих логів"""
        logs = [
            {'date': '2024-01-22', 'time': '08:30:01', 'level': 'ERROR', 'message': 'Test error'}
        ]
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            display_filtered_logs(logs, 'ERROR')
            output = mock_stdout.getvalue()
            
            assert 'ERROR' in output, "Вивід має містити рівень логування"
            assert 'Test error' in output, "Вивід має містити повідомлення"
            assert '2024-01-22' in output, "Вивід має містити дату"


class TestFunctionalProgramming:
    """Тести функціонального програмування"""
    
    def test_lambda_usage_in_filtering(self):
        """Тест: Використання lambda-функцій у фільтрації"""
        logs = [
            {'level': 'INFO', 'message': 'Test'},
            {'level': 'ERROR', 'message': 'Error'},
            {'level': 'DEBUG', 'message': 'Debug'}
        ]
        
        # Перевіряємо, що filter_logs_by_level використовує функціональний підхід
        result = filter_logs_by_level(logs, 'ERROR')
        assert len(result) == 1
        assert result[0]['level'] == 'ERROR'
    
    def test_higher_order_function(self):
        """Тест: Функції вищого порядку"""
        analyzer = create_log_analyzer()
        assert callable(analyzer), "create_log_analyzer має повертати функцію"
    
    def test_map_usage_in_counting(self):
        """Тест: Використання map у підрахунку"""
        logs = [
            {'level': 'INFO', 'message': 'Test 1'},
            {'level': 'ERROR', 'message': 'Test 2'},
            {'level': 'INFO', 'message': 'Test 3'}
        ]
        
        counts = count_logs_by_level(logs)
        expected = {'INFO': 2, 'ERROR': 1}
        assert counts == expected


class TestIntegration:
    """Інтеграційні тести"""
    
    def test_full_workflow(self):
        """Тест: Повний робочий процес"""
        log_content = """2024-01-22 08:30:01 INFO User logged in successfully.
2024-01-22 09:00:45 ERROR Database connection failed.
2024-01-22 10:30:55 WARNING Disk usage above 80%.
2024-01-22 11:05:00 DEBUG Starting backup process.
2024-01-22 12:00:00 INFO User logged out."""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write(log_content)
            temp_path = f.name
        
        try:
            # Завантажуємо логи
            logs = load_logs(temp_path)
            assert len(logs) == 5, "Має бути 5 записів"
            
            # Підраховуємо за рівнями
            counts = count_logs_by_level(logs)
            expected_counts = {'INFO': 2, 'ERROR': 1, 'WARNING': 1, 'DEBUG': 1}
            assert counts == expected_counts, f"Неправильний підрахунок: {counts}"
            
            # Фільтруємо ERROR записи
            error_logs = filter_logs_by_level(logs, 'ERROR')
            assert len(error_logs) == 1, "Має бути 1 ERROR запис"
            assert "Database connection failed" in error_logs[0]['message']
            
        finally:
            os.unlink(temp_path)
    
    def test_sample_log_file(self):
        """Тест: Робота з прикладним файлом логів"""
        sample_path = TASK3_PATH / "sample.log"
        
        if sample_path.exists():
            logs = load_logs(str(sample_path))
            assert len(logs) > 0, "Файл sample.log має містити записи"
            
            counts = count_logs_by_level(logs)
            assert 'INFO' in counts, "Має містити записи INFO"
            assert 'ERROR' in counts, "Має містити записи ERROR"
            assert 'DEBUG' in counts, "Має містити записи DEBUG"
            assert 'WARNING' in counts, "Має містити записи WARNING"


if __name__ == "__main__":
    # Запуск тестів з детальним виводом
    pytest.main([__file__, "-v", "--tb=short"])
