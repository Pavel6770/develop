import pytest
import json
import os
import tempfile
from typing import List, Dict, Any
import csv

from main import load_transactions_from_csv, load_transactions_from_json, load_transactions_from_xlsx, filter_transactions_by_status, sort_transactions_by_date, filter_ruble_transactions, filter_by_description, format_transaction_for_display, get_valid_status, get_yes_no, main


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



