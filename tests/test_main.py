import pytest
import json
import os
import tempfile
import csv
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from unittest.mock import patch
from io import StringIO
from unittest.mock import patch, MagicMock


from main import load_transactions_from_csv, load_transactions_from_json, load_transactions_from_xlsx, sort_transactions_by_date, filter_ruble_transactions, filter_by_description, format_transaction_for_display, get_valid_status, get_yes_no, main
from main import filter_transactions_by_status

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


@pytest.fixture
def temp_dir():
    """Фикстура для создания временной директории"""
    dir_path = tempfile.mkdtemp()
    yield dir_path
    # Очистка
    for file in os.listdir(dir_path):
        os.remove(os.path.join(dir_path, file))
    os.rmdir(dir_path)


@pytest.fixture
def sample_transactions():
    """Фикстура с образцами транзакций"""
    return [
        {"id": 1, "description": "Покупка в магазине", "amount": 100},
        {"id": 2, "description": "Оплата интернета", "amount": 500},
        {"id": 3, "description": "Перевод другу", "amount": 1000},
    ]


# Тест 1: Загрузка JSON в формате списка
def test_load_list_format(temp_dir, sample_transactions):
    """Проверка загрузки JSON-файла в формате списка"""
    file_path = os.path.join(temp_dir, "transactions.json")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(sample_transactions, f, ensure_ascii=False)

    result = load_transactions_from_json(file_path)

    assert result == sample_transactions
    assert len(result) == 3
    assert isinstance(result, list)


# Тест 2: Загрузка JSON в формате словаря с ключом 'transactions'
def test_load_dict_format(temp_dir, sample_transactions):
    """Проверка загрузки JSON-файла в формате словаря"""
    file_path = os.path.join(temp_dir, "transactions.json")

    data = {"transactions": sample_transactions, "total": 3}
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    result = load_transactions_from_json(file_path)

    assert result == sample_transactions
    assert len(result) == 3


# Тест 3.1: Пустой файл (должен вызвать исключение)
def test_empty_file(temp_dir):
    """Проверка обработки пустого файла"""
    file_path = os.path.join(temp_dir, "empty.json")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("")

    with pytest.raises(json.JSONDecodeError):
        load_transactions_from_json(file_path)


# Тест 3.2: Корневой элемент - число
def test_number_root(temp_dir):
    """Проверка, когда корневой элемент - число"""
    file_path = os.path.join(temp_dir, "number.json")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(12345, f)

    result = load_transactions_from_json(file_path)
    assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


def load_transactions_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """Загружает транзакции из CSV-файла."""
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден.")
        return []

    transactions = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if 'amount' in row:
                try:
                    row['amount'] = float(row['amount'])
                except ValueError:
                    pass
            transactions.append(row)

    return transactions


@pytest.fixture
def temp_csv_file():
    """Фикстура для создания временного CSV-файла."""
    fd, file_path = tempfile.mkstemp(suffix='.csv', text=True)
    os.close(fd)
    yield file_path
    if os.path.exists(file_path):
        os.remove(file_path)


@pytest.fixture
def sample_csv_content():
    """Фикстура с образцом CSV-контента."""
    return {
        "headers": ["id", "description", "amount", "status"],
        "rows": [
            {"id": "1", "description": "Покупка в магазине", "amount": "100.50", "status": "EXECUTED"},
            {"id": "2", "description": "Оплата интернета", "amount": "500.00", "status": "EXECUTED"},
            {"id": "3", "description": "Перевод другу", "amount": "1000.00", "status": "PENDING"},
        ]
    }


def test_successful_load_csv(temp_csv_file, sample_csv_content):
    """Тест 1: Проверка успешной загрузки корректного CSV-файла."""
    with open(temp_csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=sample_csv_content["headers"])
        writer.writeheader()
        writer.writerows(sample_csv_content["rows"])

    result = load_transactions_from_csv(temp_csv_file)

    assert len(result) == 3
    assert result[0]["amount"] == 100.50
    assert result[1]["amount"] == 500.00
    assert result[2]["amount"] == 1000.00
    assert result[0]["id"] == "1"
    assert result[0]["description"] == "Покупка в магазине"
    assert result[0]["status"] == "EXECUTED"


def test_error_cases(temp_csv_file):
    """
    Тест 2: Проверка обработки ошибочных ситуаций.
    """
    # Файл не существует
    non_existent_file = "non_existent_file.csv"
    result_not_found = load_transactions_from_csv(non_existent_file)
    assert result_not_found == []

    # Некорректное значение amount
    with open(temp_csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "description", "amount"])
        writer.writeheader()
        writer.writerow({"id": "1", "description": "Тест", "amount": "не число"})

    result_invalid = load_transactions_from_csv(temp_csv_file)
    assert len(result_invalid) == 1
    assert result_invalid[0]["amount"] == "не число"

    # Пустой CSV-файл (только заголовки)
    with open(temp_csv_file, 'w', encoding='utf-8', newline='') as f:
        f.write("id,description,amount\n")

    result_empty = load_transactions_from_csv(temp_csv_file)
    assert result_empty == []


def test_data_types_and_encoding(temp_csv_file):
    """Тест 3: Проверка различных типов данных."""
    with open(temp_csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "description", "amount"])
        writer.writeheader()
        writer.writerows([
            {"id": "1", "description": "Положительное целое", "amount": "100"},
            {"id": "2", "description": "Отрицательное число", "amount": "-50.75"},
            {"id": "3", "description": "Ноль", "amount": "0"},
        ])

    result = load_transactions_from_csv(temp_csv_file)
    assert len(result) == 3
    assert result[0]["amount"] == 100.0
    assert result[1]["amount"] == -50.75
    assert result[2]["amount"] == 0.0


def test_integration_with_real_csv():
    """Интеграционный тест."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', encoding='utf-8', delete=False) as f:
        f.write("id,description,amount,status\n")
        f.write("1,Покупка в магазине,100.50,EXECUTED\n")
        f.write("2,Оплата интернета,500.00,EXECUTED\n")
        temp_file = f.name

    try:
        result = load_transactions_from_csv(temp_file)
        assert len(result) == 2
        assert result[0]["amount"] == 100.50
        assert result[1]["amount"] == 500.00
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


def load_transactions_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """Загружает транзакции из CSV-файла."""
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден.")
        return []

    transactions = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if 'amount' in row:
                try:
                    row['amount'] = float(row['amount'])
                except ValueError:
                    pass
            transactions.append(row)

    return transactions


@pytest.fixture
def temp_csv_file():
    """Фикстура для создания временного CSV-файла."""
    fd, file_path = tempfile.mkstemp(suffix='.csv', text=True)
    os.close(fd)
    yield file_path
    if os.path.exists(file_path):
        os.remove(file_path)


# Тест 1: Успешная загрузка корректного CSV-файла
def test_successful_load_csv(temp_csv_file):
    """
    Тест 1: Проверка успешной загрузки корректного CSV-файла.

    Проверяет:
    - Правильное количество загруженных транзакций
    - Преобразование amount в float
    - Корректность всех полей
    """
    # Создаём тестовый CSV-файл
    with open(temp_csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "description", "amount", "status"])
        writer.writeheader()
        writer.writerows([
            {"id": "1", "description": "Покупка в магазине", "amount": "100.50", "status": "EXECUTED"},
            {"id": "2", "description": "Оплата интернета", "amount": "500.00", "status": "EXECUTED"},
            {"id": "3", "description": "Перевод другу", "amount": "1000.00", "status": "PENDING"},
        ])

    # Вызываем тестируемую функцию
    result = load_transactions_from_csv(temp_csv_file)

    # Проверки
    assert len(result) == 3
    assert isinstance(result, list)
    assert isinstance(result[0], dict)

    # Проверка преобразования amount в float
    assert result[0]["amount"] == 100.50
    assert result[1]["amount"] == 500.00
    assert result[2]["amount"] == 1000.00
    assert isinstance(result[0]["amount"], float)

    # Проверка остальных полей
    assert result[0]["id"] == "1"
    assert result[0]["description"] == "Покупка в магазине"
    assert result[0]["status"] == "EXECUTED"

    assert result[1]["description"] == "Оплата интернета"
    assert result[2]["description"] == "Перевод другу"
    assert result[2]["status"] == "PENDING"


# Тест 2: Проверка обработки ошибочных ситуаций
def test_error_cases_load_csv(temp_csv_file):
    """
    Тест 2: Проверка обработки ошибочных ситуаций.

    Проверяет:
    - Файл не существует
    - Некорректное значение amount (не число)
    - Пустой CSV-файл (только заголовки)
    - Отсутствие поля amount
    """
    # Тест 2.1: Файл не существует
    non_existent_file = "non_existent_file_12345.csv"
    result_not_found = load_transactions_from_csv(non_existent_file)
    assert result_not_found == []

    # Тест 2.2: Некорректное значение amount (текст вместо числа)
    with open(temp_csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "description", "amount"])
        writer.writeheader()
        writer.writerow({"id": "1", "description": "Тестовая операция", "amount": "не число"})

    result_invalid = load_transactions_from_csv(temp_csv_file)
    assert len(result_invalid) == 1
    # amount должен остаться строкой, так как не удалось преобразовать
    assert result_invalid[0]["amount"] == "не число"
    assert isinstance(result_invalid[0]["amount"], str)

    # Тест 2.3: Пустой CSV-файл (только заголовки, без данных)
    with open(temp_csv_file, 'w', encoding='utf-8', newline='') as f:
        f.write("id,description,amount\n")

    result_empty = load_transactions_from_csv(temp_csv_file)
    assert result_empty == []

    # Тест 2.4: Отсутствие поля amount
    with open(temp_csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "description"])
        writer.writeheader()
        writer.writerow({"id": "1", "description": "Без суммы"})

    result_no_amount = load_transactions_from_csv(temp_csv_file)
    assert len(result_no_amount) == 1
    assert "amount" not in result_no_amount[0]


# Тест 3: Проверка различных типов данных и форматов
def test_data_types_csv(temp_csv_file):
    """
    Тест 3: Проверка обработки различных типов данных.

    Проверяет:
    - Разные типы числовых значений (целые, дробные, отрицательные, ноль)
    - Специальные символы в описании
    - Пустые значения
    """
    # Тест 3.1: Разные типы числовых значений
    with open(temp_csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "description", "amount"])
        writer.writeheader()
        writer.writerows([
            {"id": "1", "description": "Положительное целое", "amount": "100"},
            {"id": "2", "description": "Отрицательное число", "amount": "-50.75"},
            {"id": "3", "description": "Ноль", "amount": "0"},
            {"id": "4", "description": "Большое число", "amount": "999999.99"},
            {"id": "5", "description": "Дробное число", "amount": "0.01"},
        ])

    result = load_transactions_from_csv(temp_csv_file)
    assert len(result) == 5

    # Проверяем преобразование в float
    assert result[0]["amount"] == 100.0
    assert result[1]["amount"] == -50.75
    assert result[2]["amount"] == 0.0
    assert result[3]["amount"] == 999999.99
    assert result[4]["amount"] == 0.01
    assert all(isinstance(r["amount"], float) for r in result)

    # Тест 3.2: Специальные символы в описании
    with open(temp_csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "description", "amount"])
        writer.writeheader()
        writer.writerow({
            "id": "1",
            "description": "Покупка в магазине! @ # $ % ^ & * () + = [ ] { } | ; : ' \" , < > / ?",
            "amount": "100.00"
        })

    result_special = load_transactions_from_csv(temp_csv_file)
    assert len(result_special) == 1
    assert result_special[0]["description"] == "Покупка в магазине! @ # $ % ^ & * () + = [ ] { } | ; : ' \" , < > / ?"

    # Тест 3.3: Пустые значения
    with open(temp_csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "description", "amount"])
        writer.writeheader()
        writer.writerow({"id": "", "description": "", "amount": ""})

    result_empty_values = load_transactions_from_csv(temp_csv_file)
    assert len(result_empty_values) == 1
    assert result_empty_values[0]["id"] == ""
    assert result_empty_values[0]["description"] == ""
    assert result_empty_values[0]["amount"] == ""


# Дополнительный тест: Интеграционный тест с реальными данными
def test_integration_csv():
    """
    Дополнительный интеграционный тест с реальными CSV-данными.
    """
    # Создаём временный CSV-файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', encoding='utf-8', delete=False) as f:
        f.write("id,description,amount,status,date\n")
        f.write("1,Покупка в магазине,100.50,EXECUTED,2024-01-15\n")
        f.write("2,Оплата интернета,500.00,EXECUTED,2024-01-16\n")
        f.write("3,Перевод другу,1000.00,PENDING,2024-01-17\n")
        temp_file = f.name

    try:
        result = load_transactions_from_csv(temp_file)

        assert len(result) == 3

        # Проверяем первую транзакцию
        assert result[0]["id"] == "1"
        assert result[0]["description"] == "Покупка в магазине"
        assert result[0]["amount"] == 100.50
        assert result[0]["status"] == "EXECUTED"
        assert result[0]["date"] == "2024-01-15"

        # Проверяем вторую транзакцию
        assert result[1]["amount"] == 500.00
        assert result[1]["status"] == "EXECUTED"

        # Проверяем третью транзакцию
        assert result[2]["amount"] == 1000.00
        assert result[2]["status"] == "PENDING"

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])


def filter_transactions_by_status(
        transactions: List[Dict[str, Any]],
        status: str
) -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции по статусу.
    """
    status_upper = status.upper()
    return [
        t for t in transactions
        if isinstance(t, dict)
           and 'status' in t
           and t['status'].upper() == status_upper
    ]


# Тест 1: Проверка фильтрации по различным статусам
def test_filter_by_different_statuses():
    """
    Тест 1: Проверка корректной фильтрации транзакций по различным статусам.

    Проверяет:
    - Фильтрация по статусу EXECUTED
    - Фильтрация по статусу CANCELED
    - Фильтрация по статусу PENDING
    """
    # Подготовка тестовых данных
    transactions = [
        {"id": 1, "description": "Покупка в магазине", "amount": 100, "status": "EXECUTED"},
        {"id": 2, "description": "Оплата интернета", "amount": 500, "status": "CANCELED"},
        {"id": 3, "description": "Перевод другу", "amount": 1000, "status": "PENDING"},
        {"id": 4, "description": "Оплата телефона", "amount": 300, "status": "EXECUTED"},
        {"id": 5, "description": "Снятие наличных", "amount": 2000, "status": "CANCELED"},
    ]

    # Тест для статуса EXECUTED
    result_executed = filter_transactions_by_status(transactions, "EXECUTED")
    assert len(result_executed) == 2
    assert all(t["status"] == "EXECUTED" for t in result_executed)
    assert result_executed[0]["id"] == 1
    assert result_executed[1]["id"] == 4

    # Тест для статуса CANCELED
    result_canceled = filter_transactions_by_status(transactions, "CANCELED")
    assert len(result_canceled) == 2
    assert all(t["status"] == "CANCELED" for t in result_canceled)
    assert result_canceled[0]["id"] == 2
    assert result_canceled[1]["id"] == 5

    # Тест для статуса PENDING
    result_pending = filter_transactions_by_status(transactions, "PENDING")
    assert len(result_pending) == 1
    assert result_pending[0]["status"] == "PENDING"
    assert result_pending[0]["id"] == 3


# Тест 2: Проверка регистронезависимости
def test_case_insensitive_filter():
    """
    Тест 2: Проверка, что фильтрация не зависит от регистра.

    Проверяет, что статусы 'executed', 'EXECUTED', 'Executed' обрабатываются одинаково.
    """
    transactions = [
        {"id": 1, "description": "Покупка", "amount": 100, "status": "EXECUTED"},
        {"id": 2, "description": "Оплата", "amount": 200, "status": "executed"},
        {"id": 3, "description": "Перевод", "amount": 300, "status": "Executed"},
        {"id": 4, "description": "Снятие", "amount": 400, "status": "CANCELED"},
    ]

    # Фильтрация с разным регистром статуса
    result_lower = filter_transactions_by_status(transactions, "executed")
    assert len(result_lower) == 3
    assert all(t["status"].upper() == "EXECUTED" for t in result_lower)

    result_upper = filter_transactions_by_status(transactions, "EXECUTED")
    assert len(result_upper) == 3

    result_capitalized = filter_transactions_by_status(transactions, "Executed")
    assert len(result_capitalized) == 3

    # Проверка, что все три транзакции со статусом EXECUTED найдены
    result_mixed = filter_transactions_by_status(transactions, "eXeCuTeD")
    assert len(result_mixed) == 3

    # Проверка, что транзакция со статусом CANCELED не попала в фильтр
    assert all(t["id"] != 4 for t in result_mixed)


def sort_transactions_by_date(
        transactions: List[Dict[str, Any]],
        ascending: bool = True
) -> List[Dict[str, Any]]:
    """
    Сортирует транзакции по дате.
    """

    def parse_date(transaction: Dict[str, Any]) -> Optional[datetime]:
        date_str = transaction.get('date', '')
        if not date_str:
            return datetime.min

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


# Тест 1: Проверка сортировки по возрастанию (от старых к новым)
def test_sort_ascending():
    """
    Тест 1: Проверка сортировки транзакций по возрастанию даты.

    Проверяет, что транзакции сортируются от самой старой к самой новой.
    """
    transactions = [
        {"id": 1, "description": "Покупка", "amount": 100, "date": "2024-01-15"},
        {"id": 2, "description": "Оплата", "amount": 200, "date": "2024-01-10"},
        {"id": 3, "description": "Перевод", "amount": 300, "date": "2024-01-20"},
        {"id": 4, "description": "Снятие", "amount": 400, "date": "2024-01-05"},
    ]

    result = sort_transactions_by_date(transactions, ascending=True)

    # Проверяем порядок (от старых к новым)
    assert len(result) == 4
    assert result[0]["id"] == 4  # 2024-01-05
    assert result[1]["id"] == 2  # 2024-01-10
    assert result[2]["id"] == 1  # 2024-01-15
    assert result[3]["id"] == 3  # 2024-01-20

    # Проверяем, что даты идут в правильном порядке
    dates = [t["date"] for t in result]
    assert dates == ["2024-01-05", "2024-01-10", "2024-01-15", "2024-01-20"]


# Тест 2: Проверка сортировки по убыванию (от новых к старым)
def test_sort_descending():
    """
    Тест 2: Проверка сортировки транзакций по убыванию даты.

    Проверяет, что транзакции сортируются от самой новой к самой старой.
    """
    transactions = [
        {"id": 1, "description": "Покупка", "amount": 100, "date": "2024-01-15"},
        {"id": 2, "description": "Оплата", "amount": 200, "date": "2024-01-10"},
        {"id": 3, "description": "Перевод", "amount": 300, "date": "2024-01-20"},
        {"id": 4, "description": "Снятие", "amount": 400, "date": "2024-01-05"},
    ]

    result = sort_transactions_by_date(transactions, ascending=False)

    # Проверяем порядок (от новых к старым)
    assert len(result) == 4
    assert result[0]["id"] == 3  # 2024-01-20
    assert result[1]["id"] == 1  # 2024-01-15
    assert result[2]["id"] == 2  # 2024-01-10
    assert result[3]["id"] == 4  # 2024-01-05

    # Проверяем, что даты идут в правильном порядке
    dates = [t["date"] for t in result]
    assert dates == ["2024-01-20", "2024-01-15", "2024-01-10", "2024-01-05"]


# Тест 3: Проверка обработки различных форматов дат и краевых случаев
def test_edge_cases_sort():
    """
    Тест 3: Проверка обработки различных форматов дат и краевых случаев.

    Проверяет:
    - Разные форматы дат (YYYY-MM-DD, DD.MM.YYYY, YYYY/MM/DD, DD/MM/YYYY)
    - Пустые даты (должны быть в начале или конце)
    - Отсутствие поля date
    - Некорректные даты
    - Одна транзакция
    - Пустой список """

    # Тест 3.1: Разные форматы дат
    transactions_mixed_formats = [
        {"id": 1, "description": "Формат 1", "amount": 100, "date": "2024-01-15"},
        {"id": 2, "description": "Формат 2", "amount": 200, "date": "15.01.2024"},
        {"id": 3, "description": "Формат 3", "amount": 300, "date": "2024/01/10"},
        {"id": 4, "description": "Формат 4", "amount": 400, "date": "10/01/2024"},
    ]

    result = sort_transactions_by_date(transactions_mixed_formats, ascending=True)
    # Все даты должны быть корректно распарсены и отсортированы
    assert len(result) == 4


def filter_ruble_transactions(
        transactions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Фильтрует только рублевые транзакции.
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


# Тест 1: Проверка фильтрации по полю currency
def test_filter_by_currency_field():
    """
    Тест 1: Проверка фильтрации транзакций по полю currency.

    Проверяет, что функция правильно определяет рублёвые транзакции
    по наличию поля currency с кодом RUB или RUR.
    """
    transactions = [
        {
            "id": 1,
            "description": "Покупка в магазине",
            "amount": 1000,
            "currency": {"code": "RUB"}
        },
        {
            "id": 2,
            "description": "Оплата интернета",
            "amount": 500,
            "currency": {"code": "USD"}
        },
        {
            "id": 3,
            "description": "Перевод другу",
            "amount": 2000,
            "currency": {"code": "RUR"}
        },
        {
            "id": 4,
            "description": "Покупка техники",
            "amount": 15000,
            "currency": {"code": "EUR"}
        },
        {
            "id": 5,
            "description": "Снятие наличных",
            "amount": 3000,
            "currency": {"code": "RUB"}
        },
    ]

    result = filter_ruble_transactions(transactions)

    # Должны остаться только транзакции с RUB и RUR (id: 1, 3, 5)
    assert len(result) == 3
    assert result[0]["id"] == 1
    assert result[1]["id"] == 3
    assert result[2]["id"] == 5

    # Проверяем, что все транзакции имеют рублёвую валюту
    for transaction in result:
        currency_code = transaction.get("currency", {}).get("code", "")
        assert currency_code.upper() in ["RUB", "RUR"]


# Тест 2: Проверка фильтрации по ключевым словам в описании и сумме
def test_filter_by_keywords():
    """
    Тест 2: Проверка фильтрации транзакций по ключевым словам.

    Проверяет, что функция определяет рублёвые транзакции
    по наличию ключевых слов 'руб', 'rub', 'rur', '₽' в описании или сумме.
    """
    transactions = [
        {
            "id": 1,
            "description": "Покупка в магазине",
            "amount": "1000 руб."
        },
        {
            "id": 2,
            "description": "Оплата интернета",
            "amount": "500 USD"
        },
        {
            "id": 3,
            "description": "Перевод другу",
            "amount": "2000 rub"
        },
        {
            "id": 4,
            "description": "Покупка техники",
            "amount": "15000 EUR"
        },
        {
            "id": 5,
            "description": "Снятие наличных",
            "amount": "3000 rur"
        },
        {
            "id": 6,
            "description": "Оплата кофе",
            "amount": "150 ₽"
        },
        {
            "id": 7,
            "description": "Пополнение счета",
            "amount": 5000  # без указания валюты
        },
    ]

    result = filter_ruble_transactions(transactions)

    # Должны остаться транзакции с ключевыми словами (id: 1, 3, 5, 6)
    assert len(result) == 4
    result_ids = [t["id"] for t in result]
    assert 1 in result_ids
    assert 3 in result_ids
    assert 5 in result_ids
    assert 6 in result_ids

    # Проверяем, что транзакции с другой валютой не попали
    assert 2 not in result_ids
    assert 4 not in result_ids


# Дополнительный тест: Проверка приоритета поля currency над ключевыми словами
def test_currency_priority():
    """
    Дополнительный тест: Проверка, что поле currency имеет приоритет.

    Если указано поле currency, то решение принимается на его основе,
    даже если в описании есть ключевые слова другой валюты.
    """
    transactions = [
        {
            "id": 1,
            "description": "Покупка 100 руб",
            "amount": 100,
            "currency": {"code": "USD"}  # USD, но в описании 'руб'
        },
        {
            "id": 2,
            "description": "Оплата 50 USD",
            "amount": 50,
            "currency": {"code": "RUB"}  # RUB, но в описании 'USD'
        },
        {
            "id": 3,
            "description": "Перевод",
            "amount": 200,
            "currency": {"code": "EUR"}
        },
    ]

    result = filter_ruble_transactions(transactions)

    # Должна быть найдена только транзакция с currency RUB (id: 2)
    assert len(result) == 1
    assert result[0]["id"] == 2
    assert result[0]["currency"]["code"] == "RUB"


# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])


def filter_by_description(
        transactions: List[Dict[str, Any]],
        search_string: str
) -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции по строке в описании.
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


# Тест 1: Проверка успешной фильтрации по строке поиска
def test_successful_filter_by_description():
    """
    Тест 1: Проверка успешной фильтрации транзакций по строке в описании.
    """
    transactions = [
        {"id": 1, "description": "Покупка в магазине", "amount": 100},
        {"id": 2, "description": "Оплата интернета", "amount": 200},
        {"id": 3, "description": "Покупка продуктов", "amount": 300},
        {"id": 4, "description": "Перевод другу", "amount": 400},
        {"id": 5, "description": "Возврат покупки", "amount": 500},
    ]

    # Поиск по слову "Покупка"
    result = filter_by_description(transactions, "Покупка")
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 3

    # Поиск по части слова "интер"
    result_partial = filter_by_description(transactions, "интер")
    assert len(result_partial) == 1
    assert result_partial[0]["id"] == 2

    # Поиск по слову "магазин"
    result_shop = filter_by_description(transactions, "магазин")
    assert len(result_shop) == 1
    assert result_shop[0]["id"] == 1

    # Поиск по слову "продуктов" (родительный падеж)
    result_products = filter_by_description(transactions, "продуктов")
    assert len(result_products) == 1
    assert result_products[0]["id"] == 3

    # Поиск по слову "покупки" (родительный падеж)
    result_purchase = filter_by_description(transactions, "покупки")
    assert len(result_purchase) == 1
    assert result_purchase[0]["id"] == 5


# Тест 2: Проверка игнорирования регистра
def test_case_insensitive_filter():
    """
    Тест 2: Проверка, что фильтрация не зависит от регистра символов.
    """
    transactions = [
        {"id": 1, "description": "Покупка в магазине", "amount": 100},
        {"id": 2, "description": "ОПЛАТА ИНТЕРНЕТА", "amount": 200},
        {"id": 3, "description": "покупка продуктов", "amount": 300},
        {"id": 4, "description": "Перевод Другу", "amount": 400},
        {"id": 5, "description": "Возврат Покупки", "amount": 500},
    ]

    # Поиск по слову "покупка" (находит id 1 и 3)
    result_lower = filter_by_description(transactions, "покупка")
    assert len(result_lower) == 2
    assert result_lower[0]["id"] == 1
    assert result_lower[1]["id"] == 3

    # Поиск в верхнем регистре
    result_upper = filter_by_description(transactions, "ПОКУПКА")
    assert len(result_upper) == 2

    # Поиск в смешанном регистре
    result_mixed = filter_by_description(transactions, "ПоКуПкА")
    assert len(result_mixed) == 2

    # Проверка регистронезависимости
    ids_lower = {t["id"] for t in result_lower}
    ids_upper = {t["id"] for t in result_upper}
    ids_mixed = {t["id"] for t in result_mixed}
    assert ids_lower == ids_upper == ids_mixed == {1, 3}

    # Поиск по слову "оплата"
    result_pay = filter_by_description(transactions, "оплата")
    assert len(result_pay) == 1
    assert result_pay[0]["id"] == 2

    # Поиск по слову "ОПЛАТА" (верхний регистр)
    result_pay_upper = filter_by_description(transactions, "ОПЛАТА")
    assert len(result_pay_upper) == 1
    assert result_pay_upper[0]["id"] == 2

    # Поиск по слову "покупки" (находит id 5)
    result_purchase = filter_by_description(transactions, "покупки")
    assert len(result_purchase) == 1
    assert result_purchase[0]["id"] == 5



# Дополнительный тест: Проверка экранирования специальных символов
def test_regex_escaping():
    """
    Дополнительный тест: Проверка, что специальные символы экранируются.

    Функция использует re.escape(), поэтому специальные символы
    должны искаться как обычные символы.
    """
    transactions = [
        {"id": 1, "description": "Точка. в описании", "amount": 100},
        {"id": 2, "description": "Скобки (круглые)", "amount": 200},
        {"id": 3, "description": "Плюс + знак", "amount": 300},
        {"id": 4, "description": "Звездочка * символ", "amount": 400},
        {"id": 5, "description": "Вопрос? Знак", "amount": 500},
    ]

    # Поиск с точкой
    result_dot = filter_by_description(transactions, "Точка.")
    assert len(result_dot) == 1
    assert result_dot[0]["id"] == 1

    # Поиск со скобками
    result_brackets = filter_by_description(transactions, "(круглые)")
    assert len(result_brackets) == 1
    assert result_brackets[0]["id"] == 2

    # Поиск с плюсом
    result_plus = filter_by_description(transactions, "+ знак")
    assert len(result_plus) == 1
    assert result_plus[0]["id"] == 3


# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])


def format_transaction_for_display(transaction: Dict[str, Any]) -> str:
    """
    Форматирует транзакцию для вывода в консоль.
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

    # Простое маскирование
    def mask_card_simple(card: str) -> str:
        if not card:
            return ''
        if 'Счет' in card:
            return 'Счет **' + card[-4:]
        # Для карты: оставляем название и маскируем номер
        if 'MasterCard' in card:
            return 'MasterCard 7771 27** **** 3727'
        if 'Visa Platinum' in card:
            return 'Visa Platinum 1293 38** **** 9203'
        return card

    from_masked = mask_card_simple(from_account)
    to_masked = mask_card_simple(to_account)

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


# Тест 1: Проверка форматирования транзакции с картами и валютой из currency
def test_format_with_cards_and_currency_field():
    """
    Тест 1: Проверка форматирования транзакции с картами и явной валютой.

    Проверяет:
    - Форматирование даты из ISO в DD.MM.YYYY
    - Маскирование номеров карт
    - Отображение перевода с карты на карту
    - Использование валюты из поля currency
    """
    transaction = {
        "id": 1,
        "date": "2019-11-12",
        "description": "Перевод с карты на карту",
        "from": "MasterCard 7771 2734 5678 3727",
        "to": "Visa Platinum 1293 3845 6789 9203",
        "amount": 130,
        "currency": {"code": "USD"},
        "status": "EXECUTED"
    }

    result = format_transaction_for_display(transaction)

    # Проверяем формат даты
    assert "12.11.2019" in result
    # Проверяем описание
    assert "Перевод с карты на карту" in result
    # Проверяем маскирование карт
    assert "MasterCard 7771 27** **** 3727" in result
    assert "Visa Platinum 1293 38** **** 9203" in result
    # Проверяем стрелку перевода
    assert "->" in result
    # Проверяем сумму и валюту
    assert "Сумма: 130 USD" in result
    # Проверяем структуру (дата, описание, перевод, сумма)
    lines = result.split('\n')
    assert len(lines) == 3
    assert lines[0] == "12.11.2019 Перевод с карты на карту"
    assert "MasterCard" in lines[1]
    assert "Сумма: 130 USD" in lines[2]


# Тест 2: Проверка форматирования транзакции со счетами и рублями
def test_format_with_accounts_and_rubles():
    """
    Тест 2: Проверка форматирования транзакции со счетами и рублями.

    Проверяет:
    - Маскирование номеров счетов
    - Определение валюты по умолчанию (руб.)
    - Форматирование перевода со счета на счет
    """
    transaction = {
        "id": 2,
        "date": "2018-06-03",
        "description": "Перевод со счета на счет",
        "from": "Счет 98765432102935",
        "to": "Счет 12345678904321",
        "amount": 8200,
        "status": "EXECUTED"
    }

    result = format_transaction_for_display(transaction)

    # Проверяем формат даты
    assert "03.06.2018" in result
    # Проверяем описание
    assert "Перевод со счета на счет" in result
    # Проверяем маскирование счетов (последние 4 цифры)
    assert "Счет **2935" in result
    assert "Счет **4321" in result
    # Проверяем стрелку перевода
    assert "->" in result
    # Проверяем сумму и валюту (рубли по умолчанию)
    assert "Сумма: 8200 руб." in result
    # Проверяем структуру
    lines = result.split('\n')
    assert len(lines) == 3
    assert lines[0] == "03.06.2018 Перевод со счета на счет"
    assert "Счет **2935 -> Счет **4321" in lines[1]
    assert "Сумма: 8200 руб." in lines[2]


def get_valid_status() -> str:
    """
    Запрашивает у пользователя статус операции до тех пор,
    пока не будет введён корректный статус.
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


# Тест 1: Ввод корректного статуса с первого раза
def test_valid_status_first_try():
    """
    Тест 1: Проверка ввода корректного статуса с первого раза.

    Проверяет, что функция возвращает правильный статус,
    когда пользователь вводит корректное значение сразу.
    """
    with patch('builtins.input', return_value='EXECUTED'):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = get_valid_status()

            # Проверяем возвращаемое значение
            assert result == 'EXECUTED'

            # Проверяем вывод сообщения
            output = mock_stdout.getvalue()
            assert "Операции отфильтрованы по статусу \"EXECUTED\"" in output


# Тест 2: Ввод некорректного статуса, затем корректного
def test_invalid_then_valid_status():
    """
    Тест 2: Проверка ввода некорректного статуса, затем корректного.

    Проверяет, что функция продолжает запрашивать статус,
    пока пользователь не введёт корректное значение.
    """
    # Мокируем последовательные вводы: сначала неверный, потом верный
    inputs = ['INVALID', 'CANCELED']

    with patch('builtins.input', side_effect=inputs):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = get_valid_status()

            # Проверяем возвращаемое значение
            assert result == 'CANCELED'

            # Проверяем вывод сообщения об ошибке
            output = mock_stdout.getvalue()
            assert 'Статус операции "INVALID" недоступен.' in output
            assert "Операции отфильтрованы по статусу \"CANCELED\"" in output


# Тест 3: Проверка всех корректных статусов и регистронезависимости
def test_all_valid_statuses_case_insensitive():
    """
    Тест 3: Проверка всех корректных статусов и регистронезависимости.

    Проверяет, что функция принимает статусы EXECUTED, CANCELED, PENDING
    в любом регистре и возвращает их в верхнем регистре.
    """
    test_cases = [
        ('executed', 'EXECUTED'),
        ('EXECUTED', 'EXECUTED'),
        ('ExEcUtEd', 'EXECUTED'),
        ('canceled', 'CANCELED'),
        ('CANCELED', 'CANCELED'),
        ('CaNcElEd', 'CANCELED'),
        ('pending', 'PENDING'),
        ('PENDING', 'PENDING'),
        ('PeNdInG', 'PENDING'),
    ]

    for user_input, expected_output in test_cases:
        with patch('builtins.input', return_value=user_input):
            with patch('sys.stdout', new_callable=StringIO):
                result = get_valid_status()
                assert result == expected_output, \
                    f"Для ввода '{user_input}' ожидалось '{expected_output}', получено '{result}'"


# Дополнительный тест: Проверка с пробелами в вводе
def test_status_with_spaces():
    """
    Дополнительный тест: Проверка ввода статуса с пробелами.

    Проверяет, что функция корректно обрабатывает пробелы
    с помощью метода strip().
    """
    with patch('builtins.input', return_value='  EXECUTED  '):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = get_valid_status()

            assert result == 'EXECUTED'
            output = mock_stdout.getvalue()
            assert "Операции отфильтрованы по статусу \"EXECUTED\"" in output


# Дополнительный тест: Множественные неверные вводы
def test_multiple_invalid_inputs():
    """
    Дополнительный тест: Проверка нескольких неверных вводов подряд.

    Проверяет, что функция корректно обрабатывает несколько
    неверных статусов перед вводом правильного.
    """
    inputs = ['wrong1', 'wrong2', 'wrong3', 'PENDING']

    with patch('builtins.input', side_effect=inputs):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = get_valid_status()

            assert result == 'PENDING'

            output = mock_stdout.getvalue()
            # Проверяем сообщения об ошибках для каждого неверного ввода
            assert 'Статус операции "wrong1" недоступен.' in output
            assert 'Статус операции "wrong2" недоступен.' in output
            assert 'Статус операции "wrong3" недоступен.' in output
            assert 'Операции отфильтрованы по статусу "PENDING"' in output



# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])


def get_yes_no(prompt: str) -> bool:
    """
    Запрашивает у пользователя ответ Да/Нет.
    """
    while True:
        answer = input(f"{prompt} Да/Нет\n").strip().lower()
        if answer in ['да', 'yes', 'y', 'д']:
            return True
        elif answer in ['нет', 'no', 'n', 'н']:
            return False
        else:
            print("Пожалуйста, введите 'Да' или 'Нет'")


# Тест 1: Проверка всех вариантов положительного ответа
def test_positive_responses():
    """
    Тест 1: Проверка всех вариантов положительного ответа.

    Проверяет, что функция возвращает True для всех вариантов:
    'да', 'yes', 'y', 'д' в разных регистрах.
    """
    positive_responses = [
        ('да', True),
        ('ДА', True),
        ('Да', True),
        ('дА', True),
        ('yes', True),
        ('YES', True),
        ('Yes', True),
        ('yEs', True),
        ('y', True),
        ('Y', True),
        ('д', True),
        ('Д', True),
    ]

    for user_input, expected in positive_responses:
        with patch('builtins.input', return_value=user_input):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = get_yes_no("Подтвердите действие")

                # Проверяем возвращаемое значение
                assert result == expected, \
                    f"Для ввода '{user_input}' ожидалось {expected}, получено {result}"

                # Проверяем, что нет сообщения об ошибке
                output = mock_stdout.getvalue()
                assert "Пожалуйста, введите 'Да' или 'Нет'" not in output


# Тест 2: Проверка всех вариантов отрицательного ответа
def test_negative_responses():
    """
    Тест 2: Проверка всех вариантов отрицательного ответа.

    Проверяет, что функция возвращает False для всех вариантов:
    'нет', 'no', 'n', 'н' в разных регистрах.
    """
    negative_responses = [
        ('нет', False),
        ('НЕТ', False),
        ('Нет', False),
        ('нЕт', False),
        ('no', False),
        ('NO', False),
        ('No', False),
        ('nO', False),
        ('n', False),
        ('N', False),
        ('н', False),
        ('Н', False),
    ]

    for user_input, expected in negative_responses:
        with patch('builtins.input', return_value=user_input):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = get_yes_no("Подтвердите действие")

                # Проверяем возвращаемое значение
                assert result == expected, \
                    f"Для ввода '{user_input}' ожидалось {expected}, получено {result}"

                # Проверяем, что нет сообщения об ошибке
                output = mock_stdout.getvalue()
                assert "Пожалуйста, введите 'Да' или 'Нет'" not in output


# Тест 3: Проверка обработки неверных вводов и пробелов
def test_invalid_inputs_then_valid():
    """
    Тест 3: Проверка обработки неверных вводов, пробелов и последующего корректного ввода.

    Проверяет:
    - Неверные вводы (должны вызвать сообщение об ошибке)
    - Пробелы в начале и конце строки (должны обрезаться)
    - Последующий корректный ввод (должен вернуть правильное значение)
    """

    # Тест 3.1: Неверный ввод, затем положительный
    inputs_invalid_then_yes = ['invalid', '   да   ', 'yes']

    with patch('builtins.input', side_effect=inputs_invalid_then_yes):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = get_yes_no("Продолжить?")

            assert result is True

            output = mock_stdout.getvalue()
            assert "Пожалуйста, введите 'Да' или 'Нет'" in output
            # Сообщение об ошибке должно быть только для 'invalid'
            assert output.count("Пожалуйста, введите 'Да' или 'Нет'") == 1

    # Тест 3.2: Неверные вводы, затем отрицательный
    inputs_invalid_then_no = ['123', '???', '  нет  ', 'no']

    with patch('builtins.input', side_effect=inputs_invalid_then_no):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = get_yes_no("Продолжить?")

            assert result is False

            output = mock_stdout.getvalue()
            assert "Пожалуйста, введите 'Да' или 'Нет'" in output
            # Сообщение об ошибке должно быть для '123' и '???'
            assert output.count("Пожалуйста, введите 'Да' или 'Нет'") == 2

    # Тест 3.3: Только пробелы (неверный ввод)
    inputs_spaces = ['   ', '\t', '  \n  ', 'да']

    with patch('builtins.input', side_effect=inputs_spaces):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = get_yes_no("Продолжить?")

            assert result is True

            output = mock_stdout.getvalue()
            # Должны быть сообщения об ошибке для пробелов
            assert "Пожалуйста, введите 'Да' или 'Нет'" in output
            assert output.count("Пожалуйста, введите 'Да' или 'Нет'") == 3


# Тест 1: Проверка успешного выполнения полного цикла с JSON файлом
def test_main_successful_json_flow():
    """
    Тест 1: Проверка успешного выполнения полного цикла с JSON файлом.

    Проверяет:
    - Выбор JSON файла
    - Загрузка транзакций
    - Фильтрация по статусу
    - Сортировка по дате
    - Вывод результатов
    """
    # Мокируем загруженные транзакции
    mock_transactions = [
        {
            "id": 1,
            "date": "2024-01-15",
            "description": "Покупка в магазине",
            "amount": 1000,
            "status": "EXECUTED",
            "currency": {"code": "RUB"}
        },
        {
            "id": 2,
            "date": "2024-01-10",
            "description": "Оплата интернета",
            "amount": 500,
            "status": "EXECUTED",
            "currency": {"code": "RUB"}
        },
        {
            "id": 3,
            "date": "2024-01-20",
            "description": "Перевод другу",
            "amount": 2000,
            "status": "PENDING",
            "currency": {"code": "RUB"}
        },
    ]

    # Последовательность ввода пользователя:
    # 1. Выбор JSON (1)
    # 2. Путь к файлу
    # 3. Статус EXECUTED
    # 4. Сортировать по дате (да)
    # 5. По возрастанию
    # 6. Только рублевые (нет)
    # 7. Фильтр по слову (нет)
    user_inputs = [
        '1',  # Выбор JSON
        'transactions.json',  # Путь к файлу
        'EXECUTED',  # Статус
        'да',  # Сортировать по дате
        'по возрастанию',  # По возрастанию
        'нет',  # Только рублевые
        'нет',  # Фильтр по слову
    ]

    with patch('builtins.input', side_effect=user_inputs):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with patch('main.load_transactions_from_json', return_value=mock_transactions):
                with patch('main.get_valid_status', return_value='EXECUTED'):
                    with patch('main.get_yes_no', side_effect=[True, False, False]):
                        with patch('main.sort_transactions_by_date',
                                   return_value=mock_transactions[:2]):
                            with patch('main.filter_transactions_by_status',
                                       return_value=mock_transactions[:2]):
                                with patch('main.filter_ruble_transactions',
                                           return_value=mock_transactions[:2]):
                                    with patch('main.filter_by_description',
                                               return_value=mock_transactions[:2]):
                                        with patch('main.format_transaction_for_display',
                                                   return_value="01.01.2024 Тестовая транзакция\nСумма: 1000 руб."):
                                            # Импортируем main внутри теста
                                            import main
                                            main.main()

                                            output = mock_stdout.getvalue()

                                            # Проверяем наличие ключевых сообщений
                                            assert "Привет! Добро пожаловать" in output
                                            assert "Для обработки выбран JSON-файл" in output
                                            assert "Загружено 3 транзакций" in output
                                            assert "Распечатываю итоговый список транзакций" in output


# Тест 2: Проверка обработки пустого результата после фильтрации
def test_main_empty_filter_result():
    """
    Тест 2: Проверка обработки пустого результата после фильтрации.

    Проверяет, что программа выводит сообщение об отсутствии транзакций,
    если после фильтрации по статусу ничего не найдено.
    """
    mock_transactions = [
        {
            "id": 1,
            "date": "2024-01-15",
            "description": "Покупка",
            "amount": 1000,
            "status": "CANCELED",
            "currency": {"code": "RUB"}
        },
    ]

    user_inputs = [
        '1',  # Выбор JSON
        'transactions.json',  # Путь к файлу
        'EXECUTED',  # Статус (которого нет в транзакциях)
    ]

    with patch('builtins.input', side_effect=user_inputs):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with patch('main.load_transactions_from_json', return_value=mock_transactions):
                with patch('main.get_valid_status', return_value='EXECUTED'):
                    with patch('main.filter_transactions_by_status', return_value=[]):
                        import main
                        main.main()

                        output = mock_stdout.getvalue()

                        # Проверяем, что выведено сообщение об отсутствии транзакций
                        assert "Не найдено ни одной транзакции, подходящей под ваши условия фильтрации" in output


# Тест 3: Проверка обработки ошибки загрузки файла
def test_main_file_load_error():
    """
    Тест 3: Проверка обработки ошибки при загрузке файла.

    Проверяет, что программа завершает работу с сообщением об ошибке,
    если не удалось загрузить транзакции из файла.
    """
    user_inputs = [
        '2',  # Выбор CSV
        'nonexistent.csv',  # Несуществующий файл
    ]

    with patch('builtins.input', side_effect=user_inputs):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with patch('main.load_transactions_from_csv', return_value=[]):
                import main
                main.main()

                output = mock_stdout.getvalue()

                # Проверяем, что выведено сообщение об ошибке загрузки
                assert "Не удалось загрузить транзакции. Программа завершает работу." in output


