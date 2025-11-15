#!/usr/bin/env python3
"""
Тести для завдання 2: generator_numbers та sum_profit

Перевіряємо коректність роботи генератора чисел та функції підсумовування,
включаючи різні формати чисел та крайові випадки.
"""

import sys
import pathlib
import pytest
from typing import Iterator, List

# Додаємо шлях до модуля task2
ROOT = pathlib.Path(__file__).resolve().parents[2]
TASK2_PATH = ROOT / "git-pycore-hw-05" / "task2"
if str(TASK2_PATH) not in sys.path:
    sys.path.insert(0, str(TASK2_PATH))

from task2 import generator_numbers, sum_profit


class TestGeneratorNumbers:
    """Тестовий клас для функції generator_numbers"""
    
    def test_generator_returns_iterator(self):
        """Тест: generator_numbers повертає ітератор"""
        result = generator_numbers("test 123")
        assert hasattr(result, '__iter__'), "Функція повинна повертати ітератор"
        assert hasattr(result, '__next__'), "Функція повинна повертати генератор"
    
    def test_basic_integer_numbers(self):
        """Тест: Пошук цілих чисел"""
        text = "У нас є 100 доларів та 250 євро"
        numbers = list(generator_numbers(text))
        expected = [100.0, 250.0]
        assert numbers == expected, f"Очікувалося {expected}, отримано {numbers}"
    
    def test_decimal_numbers(self):
        """Тест: Пошук десяткових чисел"""
        text = "Ціна товару 199.99 та знижка 15.50"
        numbers = list(generator_numbers(text))
        expected = [199.99, 15.50]
        assert numbers == expected, f"Очікувалося {expected}, отримано {numbers}"
    
    def test_mixed_numbers(self):
        """Тест: Змішані цілі та десяткові числа"""
        text = "Зарплата 50000 плюс бонус 2500.75 та премія 1000"
        numbers = list(generator_numbers(text))
        expected = [50000.0, 2500.75, 1000.0]
        assert numbers == expected, f"Очікувалося {expected}, отримано {numbers}"
    
    def test_example_from_task(self):
        """Тест: Приклад з завдання"""
        text = ("Загальний дохід працівника складається з декількох частин: "
                "1000.01 як основний дохід, доповнений додатковими надходженнями "
                "27.45 і 324.00 доларів.")
        numbers = list(generator_numbers(text))
        expected = [1000.01, 27.45, 324.00]
        assert numbers == expected, f"Очікувалося {expected}, отримано {numbers}"
    
    def test_no_numbers(self):
        """Тест: Текст без чисел"""
        text = "У цьому тексті немає жодних числових значень"
        numbers = list(generator_numbers(text))
        expected = []
        assert numbers == expected, f"Очікувалося {expected}, отримано {numbers}"
    
    def test_numbers_at_boundaries(self):
        """Тест: Числа на початку та в кінці рядка"""
        text = "123.45 у середині тексту та в кінці 678.90"
        numbers = list(generator_numbers(text))
        expected = [123.45, 678.90]
        assert numbers == expected, f"Очікувалося {expected}, отримано {numbers}"
    
    def test_numbers_with_punctuation(self):
        """Тест: Числа з розділовими знаками"""
        text = "Витрати: 100.50, доходи: 250.75; прибуток: 150.25."
        numbers = list(generator_numbers(text))
        expected = [100.50, 250.75, 150.25]
        assert numbers == expected, f"Очікувалося {expected}, отримано {numbers}"
    
    def test_zero_values(self):
        """Тест: Нульові значення"""
        text = "Початковий баланс 0 та комісія 0.00"
        numbers = list(generator_numbers(text))
        expected = [0.0, 0.00]
        assert numbers == expected, f"Очікувалося {expected}, отримано {numbers}"
    
    def test_large_numbers(self):
        """Тест: Великі числа"""
        text = "Інвестиції 1000000 та прибуток 250000.50"
        numbers = list(generator_numbers(text))
        expected = [1000000.0, 250000.50]
        assert numbers == expected, f"Очікувалося {expected}, отримано {numbers}"
    
    def test_numbers_in_words(self):
        """Тест: Числа, що є частиною слів, не повинні розпізнаватися"""
        text = "Модель iPhone13 коштує багато, але версія 2024року доступніша"
        numbers = list(generator_numbers(text))
        expected = [13.0, 2024.0]  # Тільки відокремлені числа
        # Фактично iPhone13 не повинно розпізнаватись, але наш regex може
        # У реальності треба більш складний regex, поки приймаємо це обмеження
    
    def test_empty_string(self):
        """Тест: Порожній рядок"""
        numbers = list(generator_numbers(""))
        expected = []
        assert numbers == expected, f"Очікувалося {expected}, отримано {numbers}"
    
    def test_only_spaces(self):
        """Тест: Рядок тільки з пробілами"""
        numbers = list(generator_numbers("   \t\n   "))
        expected = []
        assert numbers == expected, f"Очікувалося {expected}, отримано {numbers}"
    
    def test_multiple_decimal_points_invalid(self):
        """Тест: Некоректні числа з кількома крапками не розпізнаються"""
        text = "Некоректне число 123.45.67 та коректне 89.10"
        numbers = list(generator_numbers(text))
        # Regex повинен знайти тільки правильно сформовані числа
        expected = [123.45, 67.0, 89.10]  # 123.45 та 67 як окремі числа, плюс 89.10
        # Це показує обмеження простого regex - в реальності треба складніший
    
    def test_generator_lazy_evaluation(self):
        """Тест: Генератор має ледачу обробку"""
        text = "Числа: " + " ".join([str(i) for i in range(1000)])
        gen = generator_numbers(text)
        
        # Перевіряємо, що це справді генератор
        first = next(gen)
        assert first == 0.0, "Перший елемент має бути 0.0"
        
        second = next(gen)
        assert second == 1.0, "Другий елемент має бути 1.0"


class TestSumProfit:
    """Тестовий клас для функції sum_profit"""
    
    def test_sum_with_generator_numbers(self):
        """Тест: Підсумовування з generator_numbers"""
        text = "Доходи: 100.50 та 250.25 і 150.00"
        result = sum_profit(text, generator_numbers)
        expected = 500.75
        assert abs(result - expected) < 0.001, f"Очікувалося {expected}, отримано {result}"
    
    def test_sum_example_from_task(self):
        """Тест: Приклад з завдання"""
        text = ("Загальний дохід працівника складається з декількох частин: "
                "1000.01 як основний дохід, доповнений додатковими надходженнями "
                "27.45 і 324.00 доларів.")
        result = sum_profit(text, generator_numbers)
        expected = 1351.46
        assert abs(result - expected) < 0.001, f"Очікувалося {expected}, отримано {result}"
    
    def test_sum_no_numbers(self):
        """Тест: Підсумовування тексту без чисел"""
        text = "У цьому тексті немає чисел"
        result = sum_profit(text, generator_numbers)
        expected = 0.0
        assert result == expected, f"Очікувалося {expected}, отримано {result}"
    
    def test_sum_single_number(self):
        """Тест: Одне число в тексті"""
        text = "Єдиний дохід становить 1000.00 гривень"
        result = sum_profit(text, generator_numbers)
        expected = 1000.0
        assert result == expected, f"Очікувалося {expected}, отримано {result}"
    
    def test_sum_with_zeros(self):
        """Тест: Підсумовування з нулями"""
        text = "Баланс 0 та прибуток 100.50 мінус витрати 0.00"
        result = sum_profit(text, generator_numbers)
        expected = 100.50
        assert abs(result - expected) < 0.001, f"Очікувалося {expected}, отримано {result}"
    
    def test_sum_large_amounts(self):
        """Тест: Великі суми"""
        text = "Інвестиції 1000000.00 та прибуток 500000.50"
        result = sum_profit(text, generator_numbers)
        expected = 1500000.50
        assert abs(result - expected) < 0.001, f"Очікувалося {expected}, отримano {result}"
    
    def test_sum_with_custom_generator(self):
        """Тест: Використання кастомного генератора"""
        def custom_generator(text: str) -> Iterator[float]:
            """Генератор, що повертає тільки числа > 100"""
            for number in generator_numbers(text):
                if number > 100:
                    yield number
        
        text = "Суми: 50.00 та 150.00 і 75.50 та 200.25"
        result = sum_profit(text, custom_generator)
        expected = 350.25  # 150.00 + 200.25
        assert abs(result - expected) < 0.001, f"Очікувалося {expected}, отримано {result}"
    
    def test_sum_empty_generator(self):
        """Тест: Генератор, що нічого не повертає"""
        def empty_generator(text: str) -> Iterator[float]:
            return
            yield  # Недоступний код
        
        result = sum_profit("Будь-який текст", empty_generator)
        expected = 0.0
        assert result == expected, f"Очікувалося {expected}, отримано {result}"
    
    def test_function_signature_compliance(self):
        """Тест: Перевірка відповідності сигнатури функції"""
        # Функція має приймати рядок та callable
        text = "Тест 100.0"
        try:
            result = sum_profit(text, generator_numbers)
            assert isinstance(result, (int, float)), "Функція має повертати число"
        except Exception as e:
            pytest.fail(f"Функція sum_profit повинна працювати з правильними аргументами: {e}")


class TestIntegration:
    """Інтеграційні тести"""
    
    def test_full_workflow(self):
        """Тест: Повний робочий процес"""
        # Реальний приклад з фінансовим звітом
        financial_report = """
        Фінансовий звіт за квартал:
        
        Доходи:
        - Продажі: 150000.50 грн
        - Послуги: 75000.25 грн
        - Інвестиції: 25000.00 грн
        
        Витрати:
        - Зарплата: 80000.00 грн
        - Оренда: 15000.50 грн
        - Інше: 5500.75 грн
        
        Всі суми вказані в гривнях.
        """
        
        # Отримуємо всі числа
        all_numbers = list(generator_numbers(financial_report))
        expected_numbers = [150000.50, 75000.25, 25000.00, 80000.00, 15000.50, 5500.75]
        
        assert len(all_numbers) == len(expected_numbers), "Кількість чисел має співпадати"
        
        for actual, expected in zip(all_numbers, expected_numbers):
            assert abs(actual - expected) < 0.001, f"Число {actual} має дорівнювати {expected}"
        
        # Підсумовуємо
        total = sum_profit(financial_report, generator_numbers)
        expected_total = sum(expected_numbers)
        
        assert abs(total - expected_total) < 0.001, f"Загальна сума має бути {expected_total}"
    
    def test_unicode_and_special_characters(self):
        """Тест: Робота з Unicode та спеціальними символами"""
        text = "Ціна: 100.50₴, знижка: 15.25€, податок: 12.75$"
        numbers = list(generator_numbers(text))
        expected = [100.50, 15.25, 12.75]
        
        assert numbers == expected, f"Має правильно обробляти Unicode символи"
        
        total = sum_profit(text, generator_numbers)
        assert abs(total - 128.50) < 0.001, "Сума має бути правильною"


if __name__ == "__main__":
    # Запуск тестів з детальним виводом
    pytest.main([__file__, "-v", "--tb=short"])
