"""
Тесты для модуля excel_reader.

Проверяют корректность чтения Excel-файлов с финансовыми операциями.
"""
import unittest
import os
import sys
import tempfile
from pathlib import Path

import pandas as pd

# Добавляем путь к родительской папке для импорта модуля
sys.path.insert(0, str(Path(__file__).parent.parent))

from financial_transactions.excel_reader import read_financial_operations_from_excel


class TestExcelReader(unittest.TestCase):
    """
    Набор тестов для функции read_financial_operations_from_excel.
    """

    def setUp(self):
        """
        Создаёт временные Excel-файлы перед каждым тестом.
        """
        self.temp_files = []

    def tearDown(self):
        """
        Удаляет временные файлы после каждого теста.
        """
        for file_path in self.temp_files:
            if os.path.exists(file_path):
                os.remove(file_path)

    def _create_temp_excel(self, data: list[dict], sheet_name: str = "Sheet1") -> str:
        """
        Создаёт временный Excel-файл из списка словарей.

        Аргументы:
            data: список словарей с данными.
            sheet_name: имя листа в Excel.

        Возвращает:
            str: путь к созданному временному файлу.
        """
        temp_file = tempfile.NamedTemporaryFile(
            mode='wb',
            suffix='.xlsx',
            delete=False
        )
        temp_file.close()

        df = pd.DataFrame(data)
        df.to_excel(temp_file.name, sheet_name=sheet_name, index=False, engine='openpyxl')

        self.temp_files.append(temp_file.name)
        return temp_file.name

    # ==================== ТЕСТ №1: Обычные данные ====================
    def test_normal_excel_reading(self):
        """
        Тест 1: Проверка чтения обычного Excel с разными типами данных.
        """
        # Подготовка тестовых данных
        test_data = [
            {
                'date': '2024-01-15',
                'description': 'Покупка продуктов',
                'amount': -1500.50,
                'category': 'Еда'
            },
            {
                'date': '2024-01-16',
                'description': 'Зарплата',
                'amount': 50000,
                'category': 'Доход'
            },
            {
                'date': '2024-01-17',
                'description': 'Такси',
                'amount': -500,
                'category': 'Транспорт'
            }
        ]

        file_path = self._create_temp_excel(test_data)
        result = read_financial_operations_from_excel(file_path)

        # Проверки
        self.assertEqual(len(result), 3, "Должно быть 3 транзакции")
        self.assertEqual(result[0]['description'], 'Покупка продуктов')
        self.assertEqual(result[0]['amount'], -1500.50)
        self.assertEqual(result[1]['amount'], 50000)
        self.assertEqual(result[1]['category'], 'Доход')
        self.assertEqual(result[2]['amount'], -500)

    # ==================== ТЕСТ №2: Пустые значения ====================
    def test_empty_values(self):
        """
        Тест 2: Проверка обработки пустых значений (NaN, None, пустые строки).
        """
        test_data = [
            {
                'id': 1,
                'description': 'Транзакция с суммой',
                'amount': 1000.50,
                'note': 'Обычная заметка'
            },
            {
                'id': 2,
                'description': 'Транзакция без суммы',
                'amount': None,
                'note': ''
            },
            {
                'id': 3,
                'description': 'Пустая заметка',
                'amount': 500,
                'note': None
            }
        ]

        file_path = self._create_temp_excel(test_data)
        result = read_financial_operations_from_excel(file_path)

        self.assertEqual(len(result), 3)

        # Первая транзакция — всё нормально
        self.assertEqual(result[0]['amount'], 1000.50)
        self.assertEqual(result[0]['note'], 'Обычная заметка')

        # Вторая транзакция — amount = None или NaN (но не число)
        # Проверяем, что значение не число (оно должно быть None или NaN)
        self.assertIsNone(result[1]['amount'], "None должно стать None")

        # Третья транзакция — note должен быть None
        self.assertEqual(result[2]['amount'], 500)
        self.assertIsNone(result[2]['note'], "None должно стать None")

    # ==================== ТЕСТ №3: Файл не найден ====================
    def test_file_not_found(self):
        """
        Тест 3: Проверка поведения при отсутствии файла.
        """
        non_existent_path = "C:/Users/NonExistentUser_12345/fake_file_that_does_not_exist.xlsx"

        result = read_financial_operations_from_excel(non_existent_path)

        self.assertEqual(result, [], "Функция должна вернуть пустой список при отсутствии файла")

    # ==================== ТЕСТ №4: Разные типы данных ====================
    def test_data_types_conversion(self):
        """
        Тест 4: Проверка преобразования типов данных.
        """
        test_data = [
            {
                'integer_col': 42,
                'float_col': 3.14159,
                'string_col': 'Просто текст',
                'negative_number': -999,
                'zero': 0
            },
            {
                'integer_col': -17,
                'float_col': 0.01,
                'string_col': 'Ещё текст',
                'negative_number': -0.001,
                'zero': 0.0
            }
        ]

        file_path = self._create_temp_excel(test_data)
        result = read_financial_operations_from_excel(file_path)

        # ИСПРАВЛЕНО: допускаем, что int может стать float
        self.assertIsInstance(result[0]['integer_col'], (int, float))
        self.assertEqual(result[0]['integer_col'], 42)  # значение то же

        self.assertIsInstance(result[0]['float_col'], float)
        self.assertEqual(result[0]['float_col'], 3.14159)

        self.assertIsInstance(result[0]['string_col'], str)

        self.assertIsInstance(result[0]['negative_number'], (int, float))
        self.assertEqual(result[0]['negative_number'], -999)

        self.assertEqual(result[0]['zero'], 0)


# ==================== ЗАПУСК ТЕСТОВ ====================
if __name__ == '__main__':
    unittest.main()