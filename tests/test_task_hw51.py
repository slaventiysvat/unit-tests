#!/usr/bin/env python3
"""
Тести для завдання 1: caching_fibonacci

Перевіряємо коректність реалізації функції fibonacci(n) з кешуванням,
ефективність використання кешу та обробку крайових випадків.
"""

import sys
import pathlib
import pytest
import time
from unittest.mock import patch

# Додаємо шлях до модуля task1
ROOT = pathlib.Path(__file__).resolve().parents[2]
TASK1_PATH = ROOT / "git-pycore-hw-05" / "task1"
if str(TASK1_PATH) not in sys.path:
    sys.path.insert(0, str(TASK1_PATH))

from task1 import caching_fibonacci


class TestCachingFibonacci:
    """Тестовий клас для функції caching_fibonacci"""
    
    def test_function_returns_callable(self):
        """Тест: caching_fibonacci повертає функцію"""
        fib = caching_fibonacci()
        assert callable(fib), "caching_fibonacci повинна повертати функцію"
    
    def test_basic_fibonacci_values(self):
        """Тест: Перевірка базових значень послідовності Фібоначчі"""
        fib = caching_fibonacci()
        
        # Перевіряємо перші 15 чисел Фібоначчі
        expected_values = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
        
        for i, expected in enumerate(expected_values):
            result = fib(i)
            assert result == expected, f"F({i}) повинно дорівнювати {expected}, отримано {result}"
    
    def test_zero_and_one_cases(self):
        """Тест: Базові випадки F(0) = 0 і F(1) = 1"""
        fib = caching_fibonacci()
        
        assert fib(0) == 0, "F(0) повинно дорівнювати 0"
        assert fib(1) == 1, "F(1) повинно дорівнювати 1"
    
    def test_larger_values(self):
        """Тест: Перевірка більших значень"""
        fib = caching_fibonacci()
        
        # F(30) = 832040
        assert fib(30) == 832040, "F(30) повинно дорівнювати 832040"
        
        # F(35) = 9227465
        assert fib(35) == 9227465, "F(35) повинно дорівнювати 9227465"
    
    def test_negative_input(self):
        """Тест: Обробка від'ємних значень"""
        fib = caching_fibonacci()
        
        with pytest.raises(ValueError, match="не може бути від'ємним"):
            fib(-1)
        
        with pytest.raises(ValueError, match="не може бути від'ємним"):
            fib(-5)
    
    def test_caching_effectiveness(self):
        """Тест: Перевірка ефективності кешування"""
        fib = caching_fibonacci()
        
        # Створюємо новий екземпляр для чистого тесту
        fib_without_cache = caching_fibonacci()
        
        # Перший виклик - обчислення з нуля
        start_time = time.perf_counter()
        result1 = fib(40)  # Збільшуємо число для більш помітної різниці
        first_call_time = time.perf_counter() - start_time
        
        # Другий виклик - має бути з кешу
        start_time = time.perf_counter()
        result2 = fib(40)
        second_call_time = time.perf_counter() - start_time
        
        # Третій виклик без кешу для порівняння
        start_time = time.perf_counter()
        result3 = fib_without_cache(40)
        third_call_time = time.perf_counter() - start_time
        
        assert result1 == result2 == result3, "Усі результати повинні бути однакові"
        
        # Другий виклик має бути значно швидшим (принаймні в 10 разів)
        # або час другого виклику має бути мінімальним
        speed_improvement = second_call_time == 0 or first_call_time / second_call_time >= 10
        assert speed_improvement or second_call_time < 0.001, f"Кешування має покращити продуктивність. Перший: {first_call_time:.6f}s, другий: {second_call_time:.6f}s"
    
    def test_independent_instances(self):
        """Тест: Незалежність різних екземплярів функції"""
        fib1 = caching_fibonacci()
        fib2 = caching_fibonacci()
        
        # Обчислюємо значення в першому екземплярі
        result1_10 = fib1(10)
        
        # Обчислюємо значення в другому екземплярі
        result2_10 = fib2(10)
        
        # Результати повинні бути однакові
        assert result1_10 == result2_10 == 55, "Обидва екземпляри повинні давати однаковий результат"
        
        # Але кеші повинні бути незалежні (це важко перевірити напряму, 
        # але ми перевіряємо, що функції працюють незалежно)
        assert fib1(15) == fib2(15) == 610, "Функції повинні працювати незалежно"
    
    def test_sequential_calls(self):
        """Тест: Послідовні виклики з різними значеннями"""
        fib = caching_fibonacci()
        
        # Обчислюємо послідовність
        sequence = []
        for i in range(10):
            sequence.append(fib(i))
        
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        assert sequence == expected, f"Послідовність повинна бути {expected}, отримано {sequence}"
    
    def test_type_consistency(self):
        """Тест: Перевірка типів значень, що повертаються"""
        fib = caching_fibonacci()
        
        for i in range(20):
            result = fib(i)
            assert isinstance(result, int), f"F({i}) повинно бути типу int, отримано {type(result)}"
    
    def test_closure_persistence(self):
        """Тест: Перевірка збереження стану кешу в замиканні"""
        fib = caching_fibonacci()
        
        # Обчислюємо F(20)
        result_20 = fib(20)
        
        # Обчислюємо F(18) - має використати кешовані значення
        result_18 = fib(18)
        
        # Обчислюємо F(21) - має використати кешоване F(20)
        result_21 = fib(21)
        
        assert result_18 == 2584, "F(18) повинно дорівнювати 2584"
        assert result_20 == 6765, "F(20) повинно дорівнювати 6765"
        assert result_21 == 10946, "F(21) повинно дорівнювати 10946"
        assert result_21 == result_20 + fib(19), "F(21) = F(20) + F(19)"


class TestPerformanceAndOptimization:
    """Тести продуктивності та оптимізації"""
    
    def test_large_fibonacci_computation(self):
        """Тест: Обчислення великих чисел Фібоначчі"""
        fib = caching_fibonacci()
        
        # F(100) - досить велике число для перевірки
        result = fib(100)
        expected = 354224848179261915075  # F(100)
        
        assert result == expected, f"F(100) повинно дорівнювати {expected}"
    
    def test_time_complexity_improvement(self):
        """Тест: Перевірка покращення часової складності через кешування"""
        fib = caching_fibonacci()
        
        # Обчислюємо F(30) декілька разів
        times = []
        for _ in range(5):
            start = time.time()
            result = fib(30)
            end = time.time()
            times.append(end - start)
        
        # Перший виклик може бути повільнішим, наступні - швидшими
        assert result == 832040, "Результат повинен бути правильним"
        
        # Останні виклики повинні бути швидшими за перший
        if len(times) > 1:
            assert times[-1] <= times[0], "Повторні виклики повинні бути швидшими"


if __name__ == "__main__":
    # Запуск тестів з детальним виводом
    pytest.main([__file__, "-v", "--tb=short"])
