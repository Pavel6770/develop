def get_mask_card_number(card_number):
    """Функция принимает на вход номер карты в виде числа и возвращает маску номера"""
    # Преобразуем число в строку
    card_number_str = str(card_number)

    # Проверяем длину номера карты
    if len(card_number_str) != 16:
        return "Неверный номер карты. Должно быть 16 цифр."

    # Формируем маску в формате "XXXX XX** **** XXXX"
    return f"{card_number_str[:4]} {card_number_str[4:6]}** **** {card_number_str[-4:]}"


def get_mask_account(account_number):
    """Функция принимает на вход номер счета в виде числа и возвращает маску номера"""

    account_str = str(account_number)

    # Если длина номера счета меньше 4, возвращаем его целиком
    if len(account_str) < 4:
        return account_str

    # Создаем маску в формате "**XXXX" (где XXXX - последние 4 цифры)
    return f"**{account_str[-4:]}"