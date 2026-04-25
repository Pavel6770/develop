import csv


def read_financial_operations_from_csv(file_path: str) -> list[dict]:
    """
    Считывает финансовые операции из CSV-файла.

    Аргументы:
        file_path (str): Путь к CSV-файлу.

    Возвращает:
        list[dict]: Список словарей с транзакциями.
    """
    transactions = []

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Преобразование числовых значений
                for key, value in row.items():
                    if value is None:
                        continue
                    # Проверка на целое число
                    if value.lstrip('-').isdigit():
                        row[key] = int(value)
                    # Проверка на число с плавающей точкой
                    elif value.replace('.', '', 1).lstrip('-').isdigit():
                        row[key] = float(value)
                transactions.append(row)

    except FileNotFoundError:
        print(f"Ошибка: файл {file_path} не найден.")
    except Exception as e:
        print(f"Ошибка при чтении CSV: {e}")

    return transactions