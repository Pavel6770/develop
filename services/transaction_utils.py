from typing import List, Dict, Any
import re
from collections import Counter
from datetime import datetime
from typing import Optional

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


def filter_transactions_by_status(
        transactions: List[Dict[str, Any]],
        status: str
) -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции по статусу.
    Поддерживает поля 'state' (из JSON) и 'status'.
    """
    if not isinstance(status, str):
        return []

    status_upper = status.upper()
    result = []

    for t in transactions:
        if not isinstance(t, dict):
            continue

        # Пробуем получить статус из полей state или status
        status_value = t.get('state') or t.get('status')

        if isinstance(status_value, str):
            if status_value.upper() == status_upper:
                result.append(t)

    return result


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


def sort_transactions_by_date(
        transactions: List[Dict[str, Any]],
        ascending: bool = True
) -> List[Dict[str, Any]]:
    """Сортирует транзакции по дате."""

    def parse_date(transaction: Dict[str, Any]) -> Optional[datetime]:
        date_str = transaction.get('date', '')
        if not date_str:
            return datetime.min

        formats = ['%Y-%m-%d', '%d.%m.%Y', '%Y/%m/%d', '%d/%m/%Y']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except (ValueError, TypeError):
                continue
        return datetime.min

    return sorted(transactions, key=parse_date, reverse=not ascending)


def filter_ruble_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Фильтрует только рублевые транзакции."""
    ruble_keywords = ['руб', 'rub', 'rur', '₽']

    def is_ruble(transaction: Dict[str, Any]) -> bool:
        # Вариант 1: JSON формат
        if 'operationAmount' in transaction:
            currency_info = transaction['operationAmount'].get('currency', {})
            currency_code = currency_info.get('code', '')
            if currency_code:
                return currency_code.upper() in ['RUB', 'RUR']
            currency_name = currency_info.get('name', '')
            return any(keyword in currency_name.lower() for keyword in ruble_keywords)

        # Вариант 2: CSV/Excel формат
        currency_code = transaction.get('currency_code', '')
        if currency_code:
            return currency_code.upper() in ['RUB', 'RUR']

        currency_name = transaction.get('currency_name', '')
        if currency_name:
            return any(keyword in currency_name.lower() for keyword in ruble_keywords)

        # Вариант 3: проверяем описание и сумму
        amount_str = str(transaction.get('amount', ''))
        description = transaction.get('description', '')
        combined = f"{amount_str} {description}".lower()
        return any(keyword in combined for keyword in ruble_keywords)

    return [t for t in transactions if is_ruble(t)]


def filter_by_description(
        transactions: List[Dict[str, Any]],
        search_string: str
) -> List[Dict[str, Any]]:
    """Фильтрует транзакции по строке в описании."""
    if not search_string:
        return transactions

    pattern = re.compile(re.escape(search_string), re.IGNORECASE)
    return [
        t for t in transactions
        if isinstance(t, dict)
           and 'description' in t
           and isinstance(t['description'], str)
           and pattern.search(t['description'])
    ]


def format_transaction_for_display(transaction: Dict[str, Any]) -> str:
    """
    Форматирует транзакцию для вывода в консоль.
    Поддерживает как JSON формат (с operationAmount), так и CSV/Excel формат.
    """
    # Форматируем дату
    date = transaction.get('date', '')
    if date and len(date) > 10:
        date = date[:10]
    if date and '-' in date:
        parts = date.split('-')
        if len(parts) == 3:
            date = f"{parts[2]}.{parts[1]}.{parts[0]}"

    description = transaction.get('description', 'Операция')

    # Получаем сумму и валюту (универсальный способ)
    amount = None
    currency = None

    # Вариант 1: JSON формат (с operationAmount)
    if 'operationAmount' in transaction:
        op_amount = transaction['operationAmount']
        amount = op_amount.get('amount', 0)
        currency_info = op_amount.get('currency', {})
        currency = currency_info.get('name') or currency_info.get('code')

    # Вариант 2: CSV/Excel формат (прямые поля)
    elif 'amount' in transaction:
        amount = transaction.get('amount', 0)
        currency = transaction.get('currency_name') or transaction.get('currency_code')

    # Если ничего не нашли, ставим значения по умолчанию
    if amount is None:
        amount = 0
    if not currency:
        currency = 'руб.'

    # Преобразуем amount в число, если это строка
    if isinstance(amount, str):
        try:
            amount = float(amount)
        except ValueError:
            pass

    # Получаем информацию о счетах
    from_account = transaction.get('from', '')
    to_account = transaction.get('to', '')

    # Маскировка карт и счетов
    def mask_card(card: str) -> str:
        if not card:
            return ""
        if "Счет" in card:
            if len(card) > 4:
                return "Счет **" + card[-4:]
            return card

        parts = card.split()
        card_number = ""
        for part in parts:
            clean_part = "".join(filter(str.isdigit, part))
            if len(clean_part) >= 16:
                card_number = clean_part
                break

        if not card_number:
            return card

        first_six = card_number[:6]
        last_four = card_number[-4:]
        masked_number = f"{first_six[:4]} {first_six[4:6]}** **** {last_four}"

        result_parts = []
        for part in parts:
            clean_part = "".join(filter(str.isdigit, part))
            if len(clean_part) < 16:
                result_parts.append(part)

        result_parts.append(masked_number)
        return " ".join(result_parts)

    from_masked = mask_card(from_account)
    to_masked = mask_card(to_account)

    # Формируем строку перевода
    if from_masked and to_masked:
        transfer_info = f"{from_masked} -> {to_masked}"
    elif to_masked:
        transfer_info = to_masked
    else:
        transfer_info = ""

    # Собираем итоговую строку
    result = f"{date} {description}\n"
    if transfer_info:
        result += f"{transfer_info}\n"
    result += f"Сумма: {amount} {currency}"
    return result