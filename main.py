import re
import json
import csv
from typing import List, Dict, Any, Optional
from collections import Counter
from datetime import datetime
import os


# Предполагаем, что функции из предыдущих заданий находятся в модуле services.transaction_utils
# Если их нет, раскомментируйте и используйте локальные версии


def load_transactions_from_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает транзакции из JSON-файла.

    Parameters
    ----------
    file_path : str
        Путь к JSON-файлу.

    Returns
    -------
    List[Dict[str, Any]]
        Список транзакций.
    """
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден.")
        return []

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'transactions' in data:
            return data['transactions']
        else:
            print("Неверный формат JSON-файла")
            return []


def load_transactions_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает транзакции из CSV-файла.

    Parameters
    ----------
    file_path : str
        Путь к CSV-файлу.

    Returns
    -------
    List[Dict[str, Any]]
        Список транзакций.
    """
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден.")
        return []

    transactions = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Преобразуем числовые значения
            if 'amount' in row:
                try:
                    row['amount'] = float(row['amount'])
                except ValueError:
                    pass
            transactions.append(row)

    return transactions


def load_transactions_from_xlsx(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает транзакции из XLSX-файла.
    Требуется установка библиотеки openpyxl: pip install openpyxl

    Parameters
    ----------
    file_path : str
        Путь к XLSX-файлу.

    Returns
    -------
    List[Dict[str, Any]]
        Список транзакций.
    """
    try:
        import openpyxl
    except ImportError:
        print("Для работы с XLSX-файлами установите библиотеку openpyxl: pip install openpyxl")
        return []

    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден.")
        return []

    workbook = openpyxl.load_workbook(file_path, data_only=True)
    sheet = workbook.active

    # Получаем заголовки из первой строки
    headers = []
    for cell in sheet[1]:
        headers.append(cell.value)

    transactions = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        transaction = {}
        for i, header in enumerate(headers):
            if i < len(row):
                transaction[header] = row[i]
        if any(transaction.values()):  # Добавляем только непустые строки
            transactions.append(transaction)

    return transactions


def filter_transactions_by_status(
        transactions: List[Dict[str, Any]],
        status: str
) -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции по статусу.
    """
    if not isinstance(status, str):
        return []

    status_upper = status.upper()
    result = []
    for t in transactions:
        if isinstance(t, dict):
            status_value = t.get('status')
            if isinstance(status_value, str):
                if status_value.upper() == status_upper:
                    result.append(t)
    return result


def sort_transactions_by_date(
        transactions: List[Dict[str, Any]],
        ascending: bool = True
) -> List[Dict[str, Any]]:
    """
    Сортирует транзакции по дате.

    Parameters
    ----------
    transactions : List[Dict[str, Any]]
        Список транзакций.
    ascending : bool, default=True
        True - по возрастанию, False - по убыванию.

    Returns
    -------
    List[Dict[str, Any]]
        Отсортированный список транзакций.
    """

    def parse_date(transaction: Dict[str, Any]) -> Optional[datetime]:
        date_str = transaction.get('date', '')
        if not date_str:
            return datetime.min

        # Пробуем разные форматы дат
        formats = [
            '%Y-%m-%d',
            '%d.%m.%Y',
            '%Y/%m/%d',
            '%d/%m/%Y',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except (ValueError, TypeError):
                continue

        return datetime.min

    return sorted(
        transactions,
        key=parse_date,
        reverse=not ascending
    )


def filter_ruble_transactions(
        transactions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Фильтрует только рублевые транзакции.

    Parameters
    ----------
    transactions : List[Dict[str, Any]]
        Список транзакций.

    Returns
    -------
    List[Dict[str, Any]]
        Список рублевых транзакций.
    """
    ruble_keywords = ['руб', 'rub', 'rur', '₽']

    def is_ruble(transaction: Dict[str, Any]) -> bool:
        currency = transaction.get('currency', {}).get('code', '')
        if currency:
            return currency.upper() in ['RUB', 'RUR']

        amount_str = str(transaction.get('amount', ''))
        description = transaction.get('description', '')

        combined = f"{amount_str} {description}".lower()
        return any(keyword in combined for keyword in ruble_keywords)

    return [t for t in transactions if is_ruble(t)]


def filter_by_description(
        transactions: List[Dict[str, Any]],
        search_string: str
) -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции по строке в описании.

    Parameters
    ----------
    transactions : List[Dict[str, Any]]
        Список транзакций.
    search_string : str
        Строка для поиска.

    Returns
    -------
    List[Dict[str, Any]]
        Отфильтрованный список транзакций.
    """
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

    Parameters
    ----------
    transaction : Dict[str, Any]
        Словарь с данными транзакции.

    Returns
    -------
    str
        Отформатированная строка для вывода.
    """
    # Получаем дату
    date = transaction.get('date', '')
    if date and len(date) > 10:
        date = date[:10]
    if date:
        parts = date.split('-')
        if len(parts) == 3:
            date = f"{parts[2]}.{parts[1]}.{parts[0]}"

    # Получаем описание
    description = transaction.get('description', 'Операция')

    # Получаем сумму и валюту
    amount = transaction.get('amount', 0)
    currency = transaction.get('currency', {}).get('code', '')

    if not currency:
        # Пытаемся определить валюту из amount
        if isinstance(amount, str):
            if 'USD' in amount:
                amount = amount.replace('USD', '').strip()
                currency = 'USD'
            elif 'EUR' in amount:
                amount = amount.replace('EUR', '').strip()
                currency = 'EUR'
            else:
                currency = 'руб.'
        else:
            currency = 'руб.'

    # Получаем информацию о счетах
    from_account = transaction.get('from', '')
    to_account = transaction.get('to', '')

    # Форматируем номера счетов
    def mask_card(card: str) -> str:
        """Маскирует номер карты или счета."""
        if not card:
            return ''

        # Обработка счета
        if 'Счет' in card or 'счет' in card:
            if len(card) > 4:
                return 'Счет **' + card[-4:]
            return card

        # Обработка карты
        # Разделяем на части (название карты и номер)
        parts = card.split()
        if len(parts) >= 2:
            # Номер карты - последняя часть
            card_number = parts[-1].replace(' ', '')

            # Проверяем, что это номер карты (16 и более цифр)
            if len(card_number) >= 16:
                # Маскируем: первые 6 цифр видны, остальные скрыты
                # Формат: XXXX XX** **** XXXX
                masked_number = f"{card_number[:4]} {card_number[4:6]}** **** {card_number[-4:]}"
                parts[-1] = masked_number
                return ' '.join(parts)

        return card


def get_valid_status() -> str:
    """
    Запрашивает у пользователя статус операции до тех пор,
    пока не будет введён корректный статус.

    Returns
    -------
    str
        Корректный статус операции.
    """
    valid_statuses = ['EXECUTED', 'CANCELED', 'PENDING']

    while True:
        print("\nВведите статус, по которому необходимо выполнить фильтрацию.")
        print("Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING")

        status = input().strip()

        if status.upper() in valid_statuses:
            print(f"Операции отфильтрованы по статусу \"{status.upper()}\"")
            return status.upper()
        else:
            print(f"Статус операции \"{status}\" недоступен.")


def get_yes_no(prompt: str) -> bool:
    """
    Запрашивает у пользователя ответ Да/Нет.

    Parameters
    ----------
    prompt : str
        Текст приглашения.

    Returns
    -------
    bool
        True если пользователь ответил "да", False если "нет".
    """
    while True:
        answer = input(f"{prompt} Да/Нет\n").strip().lower()
        if answer in ['да', 'yes', 'y', 'д']:
            return True
        elif answer in ['нет', 'no', 'n', 'н']:
            return False
        else:
            print("Пожалуйста, введите 'Да' или 'Нет'")


def main() -> None:
    """
    Главная функция программы, объединяющая всю логику работы
    с банковскими транзакциями.
    """
    # Приветствие
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    # Выбор источника данных
    while True:
        choice = input().strip()
        if choice in ['1', '2', '3']:
            break
        print("Пожалуйста, введите 1, 2 или 3")

    # Загрузка данных
    transactions = []

    if choice == '1':
        file_path = input("Введите путь к JSON-файлу: ").strip()
        print("Для обработки выбран JSON-файл.")
        transactions = load_transactions_from_json(file_path)
    elif choice == '2':
        file_path = input("Введите путь к CSV-файлу: ").strip()
        print("Для обработки выбран CSV-файл.")
        transactions = load_transactions_from_csv(file_path)
    elif choice == '3':
        file_path = input("Введите путь к XLSX-файлу: ").strip()
        print("Для обработки выбран XLSX-файл.")
        transactions = load_transactions_from_xlsx(file_path)

    if not transactions:
        print("Не удалось загрузить транзакции. Программа завершает работу.")
        return

    print(f"Загружено {len(transactions)} транзакций.")

    # Фильтрация по статусу
    status = get_valid_status()
    filtered_transactions = filter_transactions_by_status(transactions, status)

    if not filtered_transactions:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        return

    # Сортировка по дате
    if get_yes_no("Отсортировать операции по дате?"):
        order = input("Отсортировать по возрастанию или по убыванию?\n").strip().lower()
        ascending = order in ['по возрастанию', 'возрастанию', 'asc', 'возрастания', 'возрастание']
        filtered_transactions = sort_transactions_by_date(filtered_transactions, ascending)

    # Фильтрация рублевых транзакций
    if get_yes_no("Выводить только рублевые транзакции?"):
        filtered_transactions = filter_ruble_transactions(filtered_transactions)

    # Фильтрация по описанию
    if get_yes_no("Отфильтровать список транзакций по определенному слову в описании?"):
        search_word = input("Введите слово для поиска: ").strip()
        filtered_transactions = filter_by_description(filtered_transactions, search_word)

    # Вывод результатов
    print("\nРаспечатываю итоговый список транзакций...\n")

    if not filtered_transactions:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        return

    print(f"Всего банковских операций в выборке: {len(filtered_transactions)}\n")

    for transaction in filtered_transactions:
        print(format_transaction_for_display(transaction))
        print()


if __name__ == "__main__":
    main()