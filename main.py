import re
import json
import csv
from typing import List, Dict, Any, Optional
from collections import Counter
from datetime import datetime
import os

# Импорт функций из сервисного модуля
from services.transaction_utils import (
    filter_transactions_by_status,
    sort_transactions_by_date,
    filter_ruble_transactions,
    filter_by_description,
    format_transaction_for_display,
    count_transactions_by_categories
)


def load_transactions_from_json(file_path: str) -> List[Dict[str, Any]]:
    """Загружает транзакции из JSON-файла."""
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
    """Загружает транзакции из CSV-файла."""
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден.")
        return []

    transactions = []

    with open(file_path, 'r', encoding='utf-8-sig') as file:
        # Пробуем определить разделитель
        first_line = file.readline()
        delimiter = ';' if ';' in first_line else ','
        file.seek(0)

        reader = csv.DictReader(file, delimiter=delimiter)
        for row in reader:
            # Очищаем ключи от пробелов
            row = {key.strip(): value for key, value in row.items()}

            # Преобразуем amount в число
            if 'amount' in row and row['amount']:
                try:
                    amount_str = row['amount'].replace(',', '.')
                    row['amount'] = float(amount_str)
                except (ValueError, TypeError):
                    pass
            transactions.append(row)

    return transactions


def load_transactions_from_xlsx(file_path: str) -> List[Dict[str, Any]]:
    """Загружает транзакции из XLSX-файла."""
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
        headers.append(cell.value if cell.value else "")

    transactions = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        transaction = {}
        for i, header in enumerate(headers):
            if i < len(row):
                transaction[header] = row[i]
        if any(transaction.values()):
            transactions.append(transaction)

    return transactions


def get_valid_status() -> str:
    """Запрашивает у пользователя статус операции."""
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
    """Запрашивает у пользователя ответ Да/Нет."""
    while True:
        answer = input(f"{prompt} Да/Нет\n").strip().lower()
        if answer in ['да', 'yes', 'y', 'д']:
            return True
        elif answer in ['нет', 'no', 'n', 'н']:
            return False
        else:
            print("Пожалуйста, введите 'Да' или 'Нет'")


def main() -> None:
    """Главная функция программы."""
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    while True:
        choice = input().strip()
        if choice in ['1', '2', '3']:
            break
        print("Пожалуйста, введите 1, 2 или 3")

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

    status = get_valid_status()
    filtered_transactions = filter_transactions_by_status(transactions, status)

    if not filtered_transactions:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        return

    if get_yes_no("Отсортировать операции по дате?"):
        order = input("Отсортировать по возрастанию или по убыванию?\n").strip().lower()
        ascending = order in ['по возрастанию', 'возрастанию', 'asc', 'возрастания', 'возрастание']
        filtered_transactions = sort_transactions_by_date(filtered_transactions, ascending)

    if get_yes_no("Выводить только рублевые транзакции?"):
        filtered_transactions = filter_ruble_transactions(filtered_transactions)

    if get_yes_no("Отфильтровать список транзакций по определенному слову в описании?"):
        search_word = input("Введите слово для поиска: ").strip()
        filtered_transactions = filter_by_description(filtered_transactions, search_word)

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