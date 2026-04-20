import json
import os
import tempfile
import unittest
from typing import List, Dict, Any
from src.utils import load_transactions


class TestLoadTransactions(unittest.TestCase):
    """Тесты для функции load_transactions"""

    def setUp(self):
        """Создает временные файлы для каждого теста"""
        self.temp_files = []

    def tearDown(self):
        """Удаляет временные файлы после каждого теста"""
        for file_path in self.temp_files:
            if os.path.exists(file_path):
                os.unlink(file_path)

    def _create_temp_file(self, content: str) -> str:
        """Создает временный файл с заданным содержимым"""
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            suffix='.json',
            delete=False
        ) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        self.temp_files.append(temp_file_path)
        return temp_file_path

    def test_load_valid_transactions_returns_list_of_dicts(self):
        """
        Тест 1: Проверяет, что функция корректно загружает валидный JSON-файл
        со списком транзакций и возвращает список словарей
        """
        # Arrange: Подготовка тестовых данных
        test_data = [
            {"id": 1, "amount": 1000, "currency": "RUB", "type": "income"},
            {"id": 2, "amount": 500, "currency": "USD", "type": "expense"},
            {"id": 3, "amount": 750, "currency": "EUR", "type": "expense"}
        ]
        json_content = json.dumps(test_data, ensure_ascii=False)
        file_path = self._create_temp_file(json_content)

        # Act: Вызов тестируемой функции
        result = load_transactions(file_path)

        # Assert: Проверка результата
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], dict)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[0]["amount"], 1000)
        self.assertEqual(result[1]["currency"], "USD")
        self.assertEqual(result[2]["type"], "expense")

    def test_load_empty_file_returns_empty_list(self):
        """
        Тест 2: Проверяет, что функция возвращает пустой список,
        когда файл существует, но пустой
        """
        # Arrange: Создание пустого файла
        file_path = self._create_temp_file("")

        # Act: Вызов тестируемой функции
        result = load_transactions(file_path)

        # Assert: Проверка результата
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)

    def test_load_nonexistent_file_returns_empty_list(self):
        """
        Тест 3: Проверяет, что функция возвращает пустой список,
        когда файл не существует
        """
        # Arrange: Использование несуществующего пути
        non_existent_path = "/tmp/nonexistent_file_12345.json"
        if os.path.exists(non_existent_path):
            os.unlink(non_existent_path)

        # Act: Вызов тестируемой функции
        result = load_transactions(non_existent_path)

        # Assert: Проверка результата
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()