from typing import List, Dict, Any, Generator



def filter_by_currency(transactions: List[Dict[str, Any]], currency: str) -> Generator[Dict[str, Any], None, None]:
    """
    Фильтрует транзакции по заданной валюте.

    Args:
        transactions: Список словарей с данными о транзакциях
        currency: Код валюты для фильтрации (например, 'USD', 'EUR')

    Returns:
        Генератор, который поочередно выдает транзакции с указанной валютой
    """
    for transaction in transactions:
        try:
            # Безопасно получаем код валюты
            transaction_currency = transaction["operationAmount"]["currency"]["code"]
            if transaction_currency == currency:
                yield transaction
        except (KeyError, TypeError):
            # Пропускаем транзакции с некорректной структурой
            continue


def transaction_descriptions(transactions: List[Dict[str, Any]]) -> Generator[str, None, None]:
    """
    Генератор, возвращающий описания транзакций по очереди.

    Args:
        transactions: Список словарей с данными о транзакциях

    Returns:
        Генератор строк с описаниями транзакций

    Raises:
        TypeError: Если транзакция не является словарем
    """
    for transaction in transactions:
        if not isinstance(transaction, dict):
            raise TypeError(f"Каждая транзакция должна быть словарем, получено: {type(transaction)}")

        description = transaction.get("description")

        if description is None:
            yield "Описание отсутствует"
        else:
            yield description


def card_number_generator(start: int, end: int) -> Generator[str, None, None]:
    """
    Генератор номеров банковских карт в заданном диапазоне.

    Args:
        start: Начальное значение диапазона (1-9999999999999999)
        end: Конечное значение диапазона (1-9999999999999999)

    Returns:
        Генератор строк с номерами карт в формате "XXXX XXXX XXXX XXXX"

    Examples:
        >>> for card in card_number_generator(1, 5):
        ...     print(card)
        0000 0000 0000 0001
        0000 0000 0000 0002
        0000 0000 0000 0003
        0000 0000 0000 0004
        0000 0000 0000 0005
    """
    for number in range(start, end + 1):
        # Форматируем число в строку с 16 цифрами, дополняя нулями слева
        card_number_str = f"{number:016d}"

        # Разбиваем на группы по 4 цифры и объединяем пробелами
        formatted_card = " ".join([
            card_number_str[0:4],
            card_number_str[4:8],
            card_number_str[8:12],
            card_number_str[12:16]
        ])

        yield formatted_card