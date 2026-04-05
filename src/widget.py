from datetime import datetime
from typing import Callable, Union


def mask_account_card(
        account_info: str,
        get_mask_account: Callable[[str], str],
        get_mask_card_number: Callable[[str], str],
) -> str:
    """
    Маскирует номер карты или счета.

    Функция принимает строку с типом и номером карты или счета
    и возвращает замаскированный номер.

    Примеры:
        mask_account_card("Visa Platinum 7000792289606361", mask_acc, mask_card)
            -> "Visa Platinum 7000 79** **** 6361"
        mask_account_card("Maestro 7000792289606361", mask_acc, mask_card)
            -> "Maestro 7000 79** **** 6361"
        mask_account_card("Счет 73654108430135874305", mask_acc, mask_card)
            -> "Счет **4305"

    Args:
        account_info: Строка, содержащая тип и номер карты или счета
        get_mask_account: Функция для маскировки номера счета
        get_mask_card_number: Функция для маскировки номера карты

    Returns:
        Замаскированная строка с типом и номером

    Raises:
        IndexError: Если передана пустая строка или строка без номера
        ValueError: Если передан неизвестный тип карты/счета
    """
    if not account_info or not account_info.strip():
        raise IndexError("Передана пустая строка")

    parts: list[str] = account_info.split()

    if not parts:
        raise IndexError("Передана пустая строка")

    # Проверяем, является ли это счетом (начинается со слова "Счет")
    if parts[0] == "Счет":
        if len(parts) < 2:
            raise IndexError("Не указан номер счета")

        # Для счета: первое слово - "Счет", последняя часть - номер
        account_number: str = parts[-1]
        # Используем существующую функцию маскировки счета
        masked_number: str = get_mask_account(account_number)
        # Возвращаем "Счет" + маскированный номер
        return f"Счет {masked_number}"

    # Для карты: все части, кроме последней - название карты
    if len(parts) < 2:
        raise IndexError("Не указан номер карты")

    card_type: str = " ".join(parts[:-1])
    card_number: str = parts[-1]
    # Используем существующую функцию маскировки карты
    masked_number: str = get_mask_card_number(card_number)
    # Возвращаем тип карты + маскированный номер
    return f"{card_type} {masked_number}"


def get_date(date_string: Union[str, datetime]) -> str:
    """
    Преобразует дату из формата ISO в формат "ДД.ММ.ГГГГ".

    Args:
        date_string: Строка с датой в формате ISO или объект datetime

    Returns:
        Дата в формате "ДД.ММ.ГГГГ"

    Raises:
        TypeError: Если передан не строковый тип
        ValueError: Если переданная строка не соответствует формату ISO
    """
    # Проверка типа
    if not isinstance(date_string, str):
        raise TypeError(f"Ожидалась строка, получен {type(date_string).__name__}")

    # Проверка на пустую строку
    if not date_string or not date_string.strip():
        raise ValueError(f"Строка '{date_string}' не соответствует формату ISO")

    # Удаляем пробелы в начале и конце
    date_string = date_string.strip()

    try:
        # Пробуем стандартный ISO формат с microseconds
        dt: datetime = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except ValueError as e:
        # Пробуем формат без времени (YYYY-MM-DD)
        try:
            dt = datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Строка '{date_string}' не соответствует формату ISO") from e

    # Возвращаем дату в нужном формате
    return dt.strftime("%d.%m.%Y")