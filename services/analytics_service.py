import re
from collections import Counter
from typing import List, Dict, Any, Union


def count_operations_by_categories(
        transactions: List[Dict[str, Any]],
        categories: List[str]
) -> Dict[str, int]:
    """
    Подсчитывает количество операций по заданным категориям.

    Категория определяется по наличию названия категории в поле description.
    Поиск выполняется без учёта регистра с использованием регулярных выражений.

    Parameters
    ----------
    transactions : List[Dict[str, Any]]
        Список словарей с данными о банковских операциях.
        Каждый словарь должен содержать ключ 'description' с описанием операции.
    categories : List[str]
        Список названий категорий для подсчёта операций.

    Returns
    -------
    Dict[str, int]
        Словарь, где ключи — названия категорий, значения — количество операций
        в каждой категории. Категории, по которым не найдено ни одной операции,
        возвращаются со значением 0.

    Examples
    --------
    >>> transactions = [
    ...     {"id": 1, "description": "Покупка в магазине", "amount": 100},
    ...     {"id": 2, "description": "Оплата интернета", "amount": 50},
    ...     {"id": 3, "description": "Перевод другу", "amount": 200},
    ...     {"id": 4, "description": "Покупка продуктов", "amount": 150},
    ...     {"id": 5, "description": "Оплата интернета", "amount": 30},
    ... ]
    >>> categories = ["покупка", "интернет", "перевод", "развлечения"]
    >>> count_operations_by_categories(transactions, categories)
    {'покупка': 2, 'интернет': 2, 'перевод': 1, 'развлечения': 0}
    """
    # Обработка пустых входных данных
    if not transactions:
        return {category: 0 for category in categories}

    if not categories:
        return {}

    # Создаём регулярное выражение для каждой категории
    category_patterns = {}
    for category in categories:
        # Экранируем спецсимволы и создаём паттерн без учёта регистра
        pattern = re.compile(re.escape(category), re.IGNORECASE)
        category_patterns[category] = pattern

    # Счётчик для результатов
    result_counter = Counter()

    # Обрабатываем каждую транзакцию
    for transaction in transactions:
        # Проверяем валидность транзакции
        if not isinstance(transaction, dict):
            continue

        # Получаем описание операции
        description = transaction.get('description')
        if not description or not isinstance(description, str):
            continue

        # Проверяем каждую категорию
        for category, pattern in category_patterns.items():
            if pattern.search(description):
                result_counter[category] += 1
                break  # Одна операция относится к первой подходящей категории

    # Добавляем категории с нулевым количеством
    for category in categories:
        if category not in result_counter:
            result_counter[category] = 0

    return dict(result_counter)