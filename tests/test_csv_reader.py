import unittest
import os
import csv
import tempfile
import sys
from pathlib import Path

# Добавляем путь к родительской папке, чтобы импортировать наш модуль
sys.path.insert(0, str(Path(__file__).parent.parent))

from financial_transactions.csv_reader import read_financial_operations_from_csv


class TestCsvReader(unittest.TestCase):

    def setUp(self):
        """Создаёт временные файлы для тестов"""
        self.temp_files = []

    def tearDown(self):
        """Удаляет временные файлы после каждого теста"""
        for file_path in self.temp_files:
            if os.path.exists(file_path):
                os.remove(file_path)

    def _create_temp_csv(self, data):
        """Создаёт временный CSV-файл"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', newline='', suffix='.csv', delete=False, encoding='utf-8')
        writer = csv.writer(temp_file)
        for row in data:
            writer.writerow(row)
        temp_file.close()
        self.temp_files.append(temp_file.name)
        return temp_file.name

    def test_normal_csv_reading(self):
        """Тест 1: Обычное чтение CSV"""
        test_data = [
            ['date', 'description', 'amount', 'category'],
            ['2024-01-15', 'Покупка продуктов', '-1500.50', 'Еда'],
            ['2024-01-16', 'Зарплата', '50000', 'Доход'],
            ['2024-01-17', 'Такси', '-500', 'Транспорт']
        ]

        file_path = self._create_temp_csv(test_data)
        result = read_financial_operations_from_csv(file_path)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['amount'], -1500.50)
        self.assertEqual(result[1]['amount'], 50000)
        self.assertEqual(result[2]['amount'], -500)

    def test_file_not_found(self):
        """Тест 2: Файл не найден"""
        result = read_financial_operations_from_csv("C:/fake_file_12345.csv")
        self.assertEqual(result, [])

    def test_different_numeric_formats(self):
        """Тест 3: Разные форматы чисел"""
        test_data = [
            ['id', 'amount'],
            ['1', '42'],
            ['2', '3.14'],
            ['3', '-7.77']
        ]

        file_path = self._create_temp_csv(test_data)
        result = read_financial_operations_from_csv(file_path)

        self.assertIsInstance(result[0]['amount'], int)
        self.assertIsInstance(result[1]['amount'], float)
        self.assertIsInstance(result[2]['amount'], float)


if __name__ == '__main__':
    unittest.main()