def count_transactions_by_categories(transactions, categories):
    result = {category: 0 for category in categories}
    
    for transaction in transactions:
        description = transaction.get('description', '')
        print(f"\n--- Обработка: {description} ---")
        
        desc_lower = description.lower()
        
        for category, keywords in categories.items():
            print(f"  Категория: {category}")
            for keyword in keywords:
                keyword_lower = keyword.lower()
                print(f"    Проверка: '{keyword_lower}' в '{desc_lower}'")
                if keyword_lower in desc_lower:
                    print(f"      -> НАЙДЕНО! {category} +1")
                    result[category] += 1
                    break
            else:
                continue
            break
    
    return result

# Тест
print("=" * 60)
print("ДИАГНОСТИКА ФУНКЦИИ")
print("=" * 60)

transactions = [
    {"id": 1, "description": "Покупка в магазине", "amount": -100},
    {"id": 2, "description": "Оплата интернета", "amount": -500},
    {"id": 3, "description": "Перевод другу", "amount": -1000},
    {"id": 4, "description": "Покупка продуктов", "amount": -300},
]

categories = {
    "shopping": ["магазин", "продукты", "продуктов", "продукт"],
    "utilities": ["интернет"],
    "transfers": ["перевод"]
}

result = count_transactions_by_categories(transactions, categories)
print("\n" + "=" * 60)
print(f"ИТОГОВЫЙ РЕЗУЛЬТАТ: {result}")
print(f"ОЖИДАЛОСЬ: {{'shopping': 2, 'utilities': 1, 'transfers': 1}}")