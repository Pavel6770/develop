from typing import List, Dict, Any, Optional
from typing import List, Dict, Any, Optional
from datetime import datetime


def filter_by_state(operations: List[Dict[str, Any]], state: str = 'EXECUTED') -> List[Dict[str, Any]]:
    """
    Фильтрует список словарей по значению ключа 'state'.
    """
    filtered_operations = []

    for operation in operations:
        if operation.get('state') == state:
            filtered_operations.append(operation)

    return filtered_operations



def sort_by_date(operations: List[Dict[str, Any]], reverse: bool = True) -> List[Dict[str, Any]]:
    """
    Сортирует список словарей по ключу 'date' с преобразованием в datetime.
    Это более надежный способ, так как учитывает реальные даты, а не строки.
    """

    def get_date(operation):
        # Преобразуем строку с датой в объект datetime для корректной сортировки
        return datetime.fromisoformat(operation['date'].replace('Z', '+00:00'))

    return sorted(operations, key=get_date, reverse=reverse)