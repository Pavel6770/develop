import json
import os
from typing import List, Dict, Any


def load_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает данные о финансовых транзакциях из JSON-файла.

    Args:
        file_path (str): Путь к JSON-файлу

    Returns:
        List[Dict[str, Any]]: Список словарей с транзакциями.
                              При ошибках возвращает пустой список.
    """
    # Проверяем, существует ли файл
    if not os.path.exists(file_path):
        return []

    # Проверяем, не пустой ли файл
    if os.path.getsize(file_path) == 0:
        return []

    try:
        # Открываем и читаем файл
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Проверяем, является ли загруженные данные списком
        if not isinstance(data, list):
            return []

        return data

    except (json.JSONDecodeError, IOError, OSError):
        # Возвращаем пустой список при любой ошибке чтения или парсинга
        return []