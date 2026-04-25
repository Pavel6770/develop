import pandas as pd


def read_financial_operations_from_excel(file_path: str) -> list[dict]:
    """
    Считывает финансовые операции из Excel-файла.

    Аргументы:
        file_path (str): Путь к Excel-файлу.

    Возвращает:
        list[dict]: Список словарей с транзакциями.
    """
    try:
        # Чтение Excel-файла
        df = pd.read_excel(file_path, engine='openpyxl')

        # Преобразование DataFrame в список словарей
        transactions = df.to_dict(orient='records')

        # Преобразование типов (pandas и так хорошо справляется, но можно донастроить)
        for transaction in transactions:
            for key, value in transaction.items():
                if pd.isna(value):
                    transaction[key] = None
                elif isinstance(value, (pd.Timestamp, pd.DatetimeTZDtype)):
                    transaction[key] = str(value)

        return transactions

    except FileNotFoundError:
        print(f"Ошибка: файл {file_path} не найден.")
        return []
    except Exception as e:
        print(f"Ошибка при чтении Excel: {e}")
        return []