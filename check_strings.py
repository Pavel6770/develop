desc1 = "Покупка в магазине"
desc2 = "Покупка продуктов"

keywords = ["магазин", "продукты"]

print("Проверка строк:")
print(f"desc1: '{desc1}'")
print(f"desc2: '{desc2}'")
print(f"keywords[0]: '{keywords[0]}'")
print(f"keywords[1]: '{keywords[1]}'")

print("\nПоиск 'магазин' в desc1:", "магазин" in desc1)
print("Поиск 'продукты' в desc2:", "продукты" in desc2)

# Проверяем кодировку символов
print(f"\nКоды символов 'продукты':")
for ch in "продукты":
    print(f"  '{ch}' = {ord(ch)}")

print(f"\nКоды символов в desc2:")
for ch in desc2:
    print(f"  '{ch}' = {ord(ch)}")