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
    try:
        # Открываем и читаем файл
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Проверяем, не пустой ли файл (проверка после загрузки)
        # Файл может быть пустым, но json.load() выбросит исключение
        # Эта проверка уже не нужна, но оставим для явности
        if not data and isinstance(data, list):
            return []

        # Проверяем, является ли загруженные данные списком
        if not isinstance(data, list):
            print(f"Ошибка: данные в файле {file_path} не являются списком")
            return []

        return data

    except FileNotFoundError:
        # Явно отлавливаем ошибку отсутствия файла
        print(f"Файл не найден: {file_path}")
        return []

    except json.JSONDecodeError as e:
        # Ошибка парсинга JSON (включая случай с пустым файлом)
        print(f"Ошибка парсинга JSON в файле {file_path}: {e}")
        return []

    except (IOError, OSError) as e:
        # Ошибки ввода-вывода (нет прав, диск занят и т.д.)
        print(f"Ошибка при чтении файла {file_path}: {e}")
        return []

    except Exception as e:
        # Любые другие неожиданные ошибки
        print(f"Неожиданная ошибка при чтении файла {file_path}: {e}")
        return []