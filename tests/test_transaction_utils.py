import pytest
import sys
import os
from typing import List, Dict, Any


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем тестируемую функцию
from services.transaction_utils import count_transactions_by_categories


# Тест 1: Проверка нормальной работы
def test_normal_case():
    """Тест 1: Проверка корректного подсчёта транзакций по категориям."""
    transactions = [
        {"id": 1, "description": "Покупка в магазине", "amount": -100},
        {"id": 2, "description": "Оплата интернета", "amount": -500},
        {"id": 3, "description": "Перевод другу", "amount": -1000},
        {"id": 4, "description": "Покупка продуктов", "amount": -300},
    ]

    categories = {
        "shopping": ["магазин", "продукты"],
        "utilities": ["интернет", "коммунальные"],
        "transfers": ["перевод"]
    }

    expected = {'shopping': 2, 'utilities': 1, 'transfers': 1}

    result = count_transactions_by_categories(transactions, categories)

    assert result == expected


# Тест 2: Проверка игнорирования регистра
def test_case_insensitive():
    """Тест 2: Проверка, что функция игнорирует регистр символов."""
    transactions = [
        {"id": 1, "description": "ПОКУПКА В МАГАЗИНЕ", "amount": -100},
        {"id": 2, "description": "Оплата Интернета", "amount": -500},
        {"id": 3, "description": "покупка продуктов", "amount": -300},
        {"id": 4, "description": "ПЕРЕВОД другу", "amount": -1000},
    ]

    categories = {
        "shopping": ["покупка"],
        "utilities": ["интернет"],
        "transfers": ["перевод"]
    }

    result = count_transactions_by_categories(transactions, categories)

    assert result['shopping'] == 2
    assert result['utilities'] == 1
    assert result['transfers'] == 1


# Тест 3: Проверка пограничных случаев
def test_edge_cases():
    """Тест 3: Проверка работы функции с пограничными случаями."""
    categories = {"shopping": ["покупка"]}

    # Пустой список транзакций
    result_empty = count_transactions_by_categories([], categories)
    assert result_empty == {"shopping": 0}

    # Пустой словарь категорий
    transactions = [{"id": 1, "description": "Покупка", "amount": -100}]
    result_empty_cat = count_transactions_by_categories(transactions, {})
    assert result_empty_cat == {}

    # Отсутствие поля description
    transactions_missing = [
        {"id": 1, "amount": -100},  # нет поля description
        {"id": 2, "description": "Покупка", "amount": -200},
    ]
    result_missing = count_transactions_by_categories(transactions_missing, categories)
    assert result_missing["shopping"] == 1

    # Некорректный тип транзакции
    transactions_invalid = [
        {"id": 1, "description": "Покупка", "amount": -100},
        "invalid string",  # не словарь
        {"id": 2, "description": "Покупка", "amount": -200},
    ]
    result_invalid = count_transactions_by_categories(transactions_invalid, categories)
    assert result_invalid["shopping"] == 2


# Дополнительные тесты (опционально)
def test_multiple_keywords():
    """Тест: Проверка работы с несколькими ключевыми словами."""
    transactions = [
        {"id": 1, "description": "Покупка в магазине", "amount": -100},
        {"id": 2, "description": "Заказ товаров", "amount": -200},
        {"id": 3, "description": "Приобретение продуктов", "amount": -300},
    ]

    categories = {
        "shopping": ["магазин", "товары", "продукты"]
    }

    result = count_transactions_by_categories(transactions, categories)

    assert result['shopping'] == 3


def test_special_characters():
    """Тест: Проверка работы со специальными символами."""
    transactions = [
        {"id": 1, "description": "Оплата (интернет)", "amount": -500},
        {"id": 2, "description": "Покупка + доставка", "amount": -300},
    ]

    categories = {
        "utilities": ["(интернет)"],
        "shopping": ["+ доставка"]
    }

    result = count_transactions_by_categories(transactions, categories)

    assert result['utilities'] == 1
    assert result['shopping'] == 1


def test_no_matches():
    """Тест: Проверка ситуации без совпадений."""
    transactions = [
        {"id": 1, "description": "Пополнение счета", "amount": 1000},
        {"id": 2, "description": "Снятие наличных", "amount": -500},
    ]

    categories = {
        "shopping": ["магазин"],
        "utilities": ["интернет"]
    }

    result = count_transactions_by_categories(transactions, categories)

    assert result['shopping'] == 0
    assert result['utilities'] == 0