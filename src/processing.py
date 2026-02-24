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
    Это более надежный способ, так как учитывает реальные даты, а не строки.

    Args:
        operations: Список словарей с данными операций
        reverse: Порядок сортировки (True - по убыванию, False - по возрастанию)

    Returns:
        Отсортированный список словарей
    """
    def get_date(operation: Dict[str, Any]) -> datetime:
        """Извлекает дату из операции и преобразует в datetime."""
        return datetime.fromisoformat(operation["date"].replace("Z", "+00:00"))

    return sorted(operations, key=get_date, reverse=reverse)
