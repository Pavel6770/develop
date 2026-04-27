import pytest
import sys
import os
from typing import List, Dict, Any


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем тестируемую функцию
from services.transaction_utils import count_transactions_by_categories


# Тест 1: Проверка нормальной работы
def count_transactions_by_categories(
        transactions: List[Dict[str, Any]],
        categories: Dict[str, List[str]]
) -> Dict[str, int]:
    """Подсчитывает количество транзакций по категориям"""
    result = {category: 0 for category in categories}

    if not transactions or not categories:
        return result

    for transaction in transactions:
        description = transaction.get('description', '')
        if not description or not isinstance(description, str):
            continue

        desc_lower = description.lower()

        for category, keywords in categories.items():
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Прямое вхождение
                if keyword_lower in desc_lower:
                    result[category] += 1
                    break
                # Проверяем основу слова (без последней буквы)
                elif len(keyword_lower) >= 4 and keyword_lower[:-1] in desc_lower:
                    result[category] += 1
                    break
            else:
                continue
            break

    return result


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
def count_transactions_by_categories(
        transactions: List[Dict[str, Any]],
        categories: Dict[str, List[str]]
) -> Dict[str, int]:
    """Подсчитывает количество транзакций по категориям"""
    result = {category: 0 for category in categories}

    if not transactions or not categories:
        return result

    for transaction in transactions:
        # Проверка 1: транзакция должна быть словарём
        if not isinstance(transaction, dict):
            continue

        # Проверка 2: поле description должно существовать и быть строкой
        description = transaction.get('description')
        if not description or not isinstance(description, str):
            continue

        desc_lower = description.lower()

        # Поиск категории
        for category, keywords in categories.items():
            for keyword in keywords:
                keyword_lower = keyword.lower()

                # Прямое вхождение
                if keyword_lower in desc_lower:
                    result[category] += 1
                    break

                # Проверка основы слова (для падежей)
                elif len(keyword_lower) >= 4:
                    # Проверяем без последней буквы
                    base = keyword_lower[:-1]
                    if base in desc_lower:
                        result[category] += 1
                        break

                    # Для слов длиннее 5 букв, проверяем без двух последних
                    if len(keyword_lower) >= 5:
                        base2 = keyword_lower[:-2]
                        if base2 in desc_lower:
                            result[category] += 1
                            break
            else:
                continue
            break

    return result


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