import re
from collections import Counter
from typing import List, Dict, Any

def count_transactions_by_categories(
        transactions: List[Dict[str, Any]],
        categories: Dict[str, List[str]]
) -> Dict[str, int]:
    if not transactions or not categories:
        return {category: 0 for category in categories}

    category_patterns = {}
    for category, keywords in categories.items():
        # Экранируем ключевые слова для безопасного использования в regex
        escaped_keywords = [re.escape(keyword) for keyword in keywords]
        pattern = re.compile('|'.join(escaped_keywords), re.IGNORECASE)
        category_patterns[category] = pattern

    result_counter = Counter()

    for transaction in transactions:
        if not isinstance(transaction, dict):
            continue
        description = transaction.get('description')
        if not isinstance(description, str):
            continue
        
        # Проверяем каждую категорию
        for category, pattern in category_patterns.items():
            if pattern.search(description):
                result_counter[category] += 1
                break  # Одна транзакция - одна категория

    # Добавляем категории с нулевым значением
    for category in categories:
        if category not in result_counter:
            result_counter[category] = 0

    return dict(result_counter)


def test_normal_case():
    print("Тест 1: Нормальная работа...")
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
    result = count_transactions_by_categories(transactions, categories)
    expected = {'shopping': 2, 'utilities': 1, 'transfers': 1}
    
    print(f"  Результат: {result}")
    print(f"  Ожидалось: {expected}")
    
    assert result == expected, f"Ожидалось {expected}, получено {result}"
    print("  ✓ OK")


def test_case_insensitive():
    print("\nТест 2: Игнорирование регистра...")
    transactions = [
        {"id": 1, "description": "ПОКУПКА В МАГАЗИНЕ", "amount": -100},
        {"id": 2, "description": "покупка продуктов", "amount": -300},
    ]
    categories = {"shopping": ["покупка"]}
    result = count_transactions_by_categories(transactions, categories)
    
    print(f"  Результат: {result}")
    
    assert result['shopping'] == 2, f"Ожидалось 2, получено {result['shopping']}"
    print("  ✓ OK")


def test_edge_cases():
    print("\nТест 3: Пограничные случаи...")
    categories = {"shopping": ["покупка"]}
    categories2 = {"shopping": ["покупка"], "other": ["другое"]}
    
    # Пустой список транзакций
    result_empty = count_transactions_by_categories([], categories)
    assert result_empty == {"shopping": 0}
    print("  ✓ Пустой список транзакций")
    
    # Пустой словарь категорий
    transactions = [{"id": 1, "description": "Покупка", "amount": -100}]
    result_empty_cat = count_transactions_by_categories(transactions, {})
    assert result_empty_cat == {}
    print("  ✓ Пустой словарь категорий")
    
    # Отсутствие поля description
    transactions_missing = [
        {"id": 1, "amount": -100},
        {"id": 2, "description": "Покупка", "amount": -200},
    ]
    result_missing = count_transactions_by_categories(transactions_missing, categories)
    assert result_missing["shopping"] == 1
    print("  ✓ Отсутствие поля description")
    
    # Все категории с нулями
    result_with_zeros = count_transactions_by_categories([], categories2)
    assert result_with_zeros == {"shopping": 0, "other": 0}
    print("  ✓ Все категории возвращаются с нулями")
    
    print("  ✓ OK")


def test_single_match():
    print("\nТест 4: Одна транзакция - одна категория (первое совпадение)...")
    transactions = [
        {"id": 1, "description": "Перевод в магазин", "amount": -100},
    ]
    categories = {
        "shopping": ["магазин"],
        "transfers": ["перевод"]
    }
    result = count_transactions_by_categories(transactions, categories)
    
    print(f"  Результат: {result}")
    
    # Транзакция должна попасть только в одну категорию (первую)
    # Из-за break в цикле - это будет "shopping"
    assert result['shopping'] == 1, f"shopping: ожидалось 1, получено {result['shopping']}"
    assert result['transfers'] == 0, f"transfers: ожидалось 0, получено {result['transfers']}"
    print("  ✓ OK")


def test_partial_match():
    print("\nТест 5: Частичное совпадение...")
    transactions = [
        {"id": 1, "description": "Оплата интернета и телефона", "amount": -500},
    ]
    categories = {
        "utilities": ["интернет", "телефон"]
    }
    result = count_transactions_by_categories(transactions, categories)
    
    print(f"  Результат: {result}")
    
    assert result['utilities'] == 1
    print("  ✓ OK")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("ЗАПУСК ТЕСТОВ ДЛЯ ФУНКЦИИ count_transactions_by_categories")
    print("="*50)
    
    try:
        test_normal_case()
        test_case_insensitive()
        test_edge_cases()
        test_single_match()
        test_partial_match()
        
        print("\n" + "="*50)
        print("🎉 ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
        print("="*50)
    except AssertionError as e:
        print(f"\n❌ Тест не пройден: {e}")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")