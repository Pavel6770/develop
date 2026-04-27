import pytest
import re
from collections import Counter
from typing import List, Dict, Any


def count_operations_by_categories(
        transactions: List[Dict[str, Any]],
        categories: List[str]
) -> Dict[str, int]:
    """Тестируемая функция"""
    if not transactions:
        return {category: 0 for category in categories}

    if not categories:
        return {}

    category_patterns = {}
    for category in categories:
        pattern = re.compile(re.escape(category), re.IGNORECASE)
        category_patterns[category] = pattern

    result_counter = Counter()

    for transaction in transactions:
        if not isinstance(transaction, dict):
            continue

        description = transaction.get('description')
        if not description or not isinstance(description, str):
            continue

        for category, pattern in category_patterns.items():
            if pattern.search(description):
                result_counter[category] += 1
                break

    for category in categories:
        if category not in result_counter:
            result_counter[category] = 0

    return dict(result_counter)


# Тест 1: Нормальная работа
def test_normal_case():
    """Тест 1: Проверка корректного подсчёта операций по категориям"""
    transactions = [
        {"id": 1, "description": "Покупка в магазине", "amount": 100},
        {"id": 2, "description": "Оплата интернета", "amount": 50},
        {"id": 3, "description": "Перевод другу", "amount": 200},
        {"id": 4, "description": "Покупка продуктов", "amount": 150},
        {"id": 5, "description": "Оплата интернета", "amount": 30},
    ]

    categories = ["покупка", "интернет", "перевод", "развлечения"]

    result = count_operations_by_categories(transactions, categories)
    expected = {"покупка": 2, "интернет": 2, "перевод": 1, "развлечения": 0}

    assert result == expected
    assert result["покупка"] == 2
    assert result["интернет"] == 2
    assert result["развлечения"] == 0


# Тест 2: Игнорирование регистра
def test_case_insensitive():
    """Тест 2: Проверка, что функция игнорирует регистр символов"""
    transactions = [
        {"id": 1, "description": "ПОКУПКА В МАГАЗИНЕ", "amount": 100},
        {"id": 2, "description": "Оплата Интернета", "amount": 50},
        {"id": 3, "description": "Перевод другу", "amount": 200},
        {"id": 4, "description": "покупка продуктов", "amount": 150},
    ]

    categories = ["покупка", "интернет", "перевод"]

    result = count_operations_by_categories(transactions, categories)

    assert result["покупка"] == 2  # id 1 и 4
    assert result["интернет"] == 1  # id 2
    assert result["перевод"] == 1  # id 3


# Тест 3: Пограничные случаи
def test_edge_cases():
    """Тест 3: Проверка работы функции с пограничными случаями"""
    base_transactions = [
        {"id": 1, "description": "Покупка в магазине", "amount": 100},
    ]

    # Пустой список транзакций
    result_empty = count_operations_by_categories([], ["покупка"])
    assert result_empty == {"покупка": 0}

    # Пустой список категорий
    result_empty_cat = count_operations_by_categories(base_transactions, [])
    assert result_empty_cat == {}

    # Отсутствие поля description
    transactions_missing = [
        {"id": 1, "amount": 100},
        {"id": 2, "description": "Покупка", "amount": 200},
    ]
    result_missing = count_operations_by_categories(transactions_missing, ["покупка"])
    assert result_missing["покупка"] == 1

    # Некорректный тип транзакции
    transactions_invalid = [
        {"id": 1, "description": "Покупка", "amount": 100},
        "invalid string",
        {"id": 2, "description": "Покупка", "amount": 200},
    ]
    result_invalid = count_operations_by_categories(transactions_invalid, ["покупка"])
    assert result_invalid["покупка"] == 2


# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v"])