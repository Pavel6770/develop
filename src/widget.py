from datetime import datetime
from typing import Optional


def mask_account_card(account_info):
    """
    Функция принимает строку с типом и номером карты или счета
    и возвращает замаскированный номер

    Примеры:
    mask_account_card("Visa Platinum 7000792289606361") -> "Visa Platinum 7000 79** **** 6361"
    mask_account_card("Maestro 7000792289606361") -> "Maestro 7000 79** **** 6361"
    mask_account_card("Счет 73654108430135874305") -> "Счет **4305"
    """
    # Разделяем строку на части
    parts = account_info.split()

    # Проверяем, является ли это счетом (начинается со слова "Счет")
    if parts[0] == "Счет":
        # Для счета: первое слово - "Счет", последняя часть - номер
        account_number = parts[-1]
        # Используем существующую функцию маскировки счета
        masked_number = get_mask_account(account_number)
        # Возвращаем "Счет" + маскированный номер
        return f"Счет {masked_number}"
    else:
        # Для карты: все части, кроме последней - название карты
        card_type = " ".join(parts[:-1])
        card_number = parts[-1]
        # Используем существующую функцию маскировки карты
        masked_number = get_mask_card_number(card_number)
        # Возвращаем тип карты + маскированный номер
        return f"{card_type} {masked_number}"


def get_date(date_string: str) -> Optional[str]:
    """
    Преобразует дату из формата "2024-03-11T02:26:18.671407" в формат "ДД.ММ.ГГГГ"

    Args:
        date_string (str): Строка с датой в формате ISO

    Returns:
        Optional[str]: Дата в формате "ДД.ММ.ГГГГ" или None при ошибке
    """
    try:
        dt = datetime.fromisoformat(date_string)
        return dt.strftime("%d.%m.%Y")
    except (ValueError, TypeError) as e:
        print(f"Ошибка при парсинге даты: {e}")
        return None