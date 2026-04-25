from pathlib import Path
from csv_reader import read_financial_operations_from_csv
from excel_reader import read_financial_operations_from_excel


desktop = Path.home() / "Desktop"
csv_file = desktop / "transactions.csv"

print("=== Чтение CSV ===")
if csv_file.exists():
    csv_data = read_financial_operations_from_csv(str(csv_file))
    print(f"Найдено транзакций: {len(csv_data)}")
    if csv_data:
        print("Первая транзакция:", csv_data[0])
else:
    print(f"Файл не найден: {csv_file}")

print("\n" + "="*30 + "\n")

# Пример 2: Чтение Excel с Рабочего стола
excel_file = desktop / "transactions.xlsx"

print("=== Чтение Excel ===")
if excel_file.exists():
    excel_data = read_financial_operations_from_excel(str(excel_file))
    print(f"Найдено транзакций: {len(excel_data)}")
    if excel_data:
        print("Первая транзакция:", excel_data[0])
else:
    print(f"Файл не найден: {excel_file}")