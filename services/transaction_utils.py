from typing import List, Dict, Any

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
                if keyword_lower in desc_lower:
                    result[category] += 1
                    break
            else:
                continue
            break
    
    return result