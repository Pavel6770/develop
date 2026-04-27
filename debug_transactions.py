def count_transactions_by_categories(transactions, categories):
    result = {category: 0 for category in categories}
    
    for transaction in transactions:
        description = transaction.get('description', '')
        print(f"\nОбработка: {description}")
        if not description:
            continue
        
        desc_lower = description.lower()
        
        for category, keywords in categories.items():
            for keyword in keywords:
                print(f"  Проверка: {category} -> '{keyword}' в '{desc_lower}'")
                if keyword.lower() in desc_lower:
                    print(f"    -> СОВПАДЕНИЕ! {category} +1")
                    result[category] += 1
                    break
            # break  # ← НЕ ДОЛЖНО БЫТЬ break здесь!
    
    return result

transactions = [
    {"id": 1, "description": "Покупка в магазине", "amount": -100},
    {"id": 4, "description": "Покупка продуктов", "amount": -300},
]
categories = {
    "shopping": ["магазин", "продукты"],
}

result = count_transactions_by_categories(transactions, categories)
print(f"\nИтог: {result}")