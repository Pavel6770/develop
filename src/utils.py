import json
import logging
from pathlib import Path
from typing import Any, Dict, List

# Создаём папку logs в корне проекта (если её нет)
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

# Создаём объект логера для модуля utils
logger = logging.getLogger(__name__)

# Устанавливаем уровень логирования не ниже DEBUG
logger.setLevel(logging.DEBUG)

# Создаём file_handler для записи логов в файл
log_file = log_dir / 'utils.log'
file_handler = logging.FileHandler(log_file, encoding='utf-8')

# Создаём file_formatter с нужным форматом
# Формат: метка времени, название модуля, уровень серьезности, сообщение
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Устанавливаем форматер для file_handler
file_handler.setFormatter(file_formatter)

# Добавляем handler к логеру
logger.addHandler(file_handler)

# Опционально: добавляем вывод в консоль для удобства отладки
console_handler = logging.StreamHandler()
console_handler.setFormatter(file_formatter)
logger.addHandler(console_handler)


def load_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает данные о финансовых транзакциях из JSON-файла.

    Args:
        file_path (str): Путь к JSON-файлу

    Returns:
        List[Dict[str, Any]]: Список словарей с транзакциями.
                              При ошибках возвращает пустой список.
    """
    logger.debug(f"Вызов load_transactions с параметром file_path: {file_path}")

    try:
        # Открываем и читаем файл
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        logger.debug(f"Файл {file_path} успешно прочитан, тип данных: {type(data).__name__}")

        # Проверяем, не пустой ли файл
        if not data and isinstance(data, list):
            logger.warning(f"Файл {file_path} содержит пустой список")
            return []

        # Проверяем, является ли загруженные данные списком
        if not isinstance(data, list):
            logger.error(f"Данные в файле {file_path} не являются списком. Тип: {type(data).__name__}")
            return []

        logger.info(f"Успешно загружено {len(data)} транзакций из файла {file_path}")
        logger.debug(f"Загруженные данные: {data[:2] if len(data) > 2 else data}")

        return data

    except FileNotFoundError:
        logger.error(f"Файл не найден: {file_path}")
        return []

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON в файле {file_path}: {e}")
        return []

    except (IOError, OSError) as e:
        logger.error(f"Ошибка ввода-вывода при чтении файла {file_path}: {e}")
        return []

    except Exception as e:
        logger.error(f"Неожиданная ошибка при чтении файла {file_path}: {e}", exc_info=True)
        return []


def get_transactions_count(file_path: str) -> int:
    """
    Возвращает количество транзакций в файле.

    Args:
        file_path (str): Путь к JSON-файлу

    Returns:
        int: Количество транзакций или 0 при ошибке
    """
    logger.debug(f"Вызов get_transactions_count с параметром file_path: {file_path}")

    transactions = load_transactions(file_path)
    count = len(transactions)

    if count > 0:
        logger.info(f"В файле {file_path} найдено {count} транзакций")
    else:
        logger.warning(f"В файле {file_path} нет транзакций или произошла ошибка")

    return count


if __name__ == "__main__":
    # Успешный случай
    print("=== Успешный случай ===")
    transactions = load_transactions("data/operations.json")
    print(f"Загружено транзакций: {len(transactions)}")

    # Ошибочные случаи
    print("\n=== Ошибочные случаи ===")
    load_transactions("data/nonexistent.json")
    load_transactions("data/empty.json")
    load_transactions("data/invalid.json")
