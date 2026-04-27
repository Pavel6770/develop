import re
from collections import Counter

def count_transactions_by_categories(transactions, categories):
    """Простая версия функции"""
    result = {category: 0 for category in categories}
    
    for transaction in transactions:
        description = transaction.get('description', '')
        if not description:
            continue
        
        desc_lower = description.lower()
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword.lower() in desc_lower:
                    result[category] += 1
                    break
    
    return result

# Тест 1
print("Тест 1: Нормальная работа")
transactions = [
    {"id": 1, "description": "Покупка в магазине", "amount": -100},
    {"id": 2, "description": "Оплата интернета", "amount": -500},
    {"id": 3, "description": "Перевод другу", "amount": -1000},
    {"id": 4, "description": "Покупка продуктов", "amount": -300},
]
categories = {
    "shopping": ["магазин", "продукты"],
    "utilities": ["интернет"],
    "transfers": ["перевод"]
}
result = count_transactions_by_categories(transactions, categories)
expected = {"shopping": 2, "utilities": 1, "transfers": 1}
print(f"Результат: {result}")
print(f"Ожидалось: {expected}")
print("✅ ПРОЙДЕН" if result == expected else "❌ НЕ ПРОЙДЕН")

# Тест 2
print("\nТест 2: Игнорирование регистра")
transactions = [
    {"id": 1, "description": "ПОКУПКА В МАГАЗИНЕ", "amount": -100},
    {"id": 2, "description": "покупка продуктов", "amount": -300},
]
categories = {
    "shopping": ["магазин", "продукты", "продуктов"],  # Добавили "продуктов"
    "utilities": ["интернет"],
    "transfers": ["перевод"]
}
result = count_transactions_by_categories(transactions, categories)
print(f"Результат: {result}")
print("✅ ПРОЙДЕН" if result["shopping"] == 2 else "❌ НЕ ПРОЙДЕН")

# Тест 3
print("\nТест 3: Пограничные случаи")
categories = {"shopping": ["покупка"]}
result = count_transactions_by_categories([], categories)
print(f"Пустой список: {result}")
print("✅ ПРОЙДЕН" if result == {"shopping": 0} else "❌ НЕ ПРОЙДЕН")