from datetime import datetime
from typing import Any, Dict, List, Optional


def filter_by_state(
        operations: List[Dict[str, Any]], state: str = "EXECUTED"
) -> List[Dict[str, Any]]:
    """
    Фильтрует список словарей по значению ключа 'state'.

    Args:
        operations: Список словарей с данными операций
        state: Значение для фильтрации по ключу 'state' (по умолчанию 'EXECUTED')

    Returns:
        Отфильтрованный список словарей
    """
    filtered_operations = [
        operation for operation in operations if operation.get("state") == state
    ]
    return filtered_operations


def sort_by_date(
        operations: List[Dict[str, Any]], reverse: bool = True
) -> List[Dict[str, Any]]:
    """
    Сортирует список словарей по ключу 'date' с преобразованием в datetime.
    Более надежный способ, учитывающий реальные даты.

    Args:
        operations: Список словарей с данными операций
        reverse: Порядок сортировки (True - по убыванию, False - по возрастанию)

    Returns:
        Отсортированный список словарей

    Raises:
        KeyError: Если в операции отсутствует ключ 'date'
        ValueError: Если формат даты не соответствует ISO формату
    """

    def get_date(operation: Dict[str, Any]) -> datetime:
        """Извлекает дату из операции и преобразует в datetime."""
        date_str = operation.get("date")
        if date_str is None:
            raise KeyError(f"Отсутствует ключ 'date' в операции: {operation}")

        try:
            # Пробуем стандартный ISO формат
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError as e:
            # Если не получилось, пробуем другие распространенные форматы
            try:
                # Пробуем формат без времени (YYYY-MM-DD)
                return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Некорректный формат даты '{date_str}': {e}")

    return sorted(operations, key=get_date, reverse=reverse)
