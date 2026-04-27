import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.transaction_utils import count_transactions_by_categories


def test_normal_case():
    """Тест 1: Нормальная работа"""
    transactions = [
        {"id": 1, "description": "Покупка в магазине", "amount": -100},
        {"id": 2, "description": "Оплата интернета", "amount": -500},
        {"id": 3, "description": "Перевод другу", "amount": -1000},
        {"id": 4, "description": "Покупка продуктов", "amount": -300},
    ]
    categories = {
        "shopping": ["магазин", "продукты", "продуктов"],  # Добавили "продуктов"
        "utilities": ["интернет"],
        "transfers": ["перевод"]
    }
    result = count_transactions_by_categories(transactions, categories)
    expected = {'shopping': 2, 'utilities': 1, 'transfers': 1}
    assert result == expected


def test_case_insensitive():
    """Тест 2: Игнорирование регистра"""
    transactions = [
        {"id": 1, "description": "ПОКУПКА В МАГАЗИНЕ", "amount": -100},
        {"id": 2, "description": "покупка продуктов", "amount": -300},
    ]
    categories = {"shopping": ["покупка"]}
    result = count_transactions_by_categories(transactions, categories)
    assert result['shopping'] == 2


def test_edge_cases():
    """Тест 3: Пограничные случаи"""
    categories = {"shopping": ["покупка"]}
    
    # Пустой список транзакций
    result_empty = count_transactions_by_categories([], categories)
    assert result_empty == {"shopping": 0}
    
    # Пустой словарь категорий
    transactions = [{"id": 1, "description": "Покупка", "amount": -100}]
    result_empty_cat = count_transactions_by_categories(transactions, {})
    assert result_empty_cat == {}