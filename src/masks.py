import logging
from pathlib import Path

# Создаём папку logs в корне проекта (если её нет)
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

# Создаём объект логера для модуля masks
logger = logging.getLogger(__name__)

# Устанавливаем уровень логирования не ниже DEBUG
logger.setLevel(logging.DEBUG)

# Создаём file_handler для записи логов в файл
log_file = log_dir / 'masks.log'
file_handler = logging.FileHandler(log_file, encoding='utf-8')

# Создаём file_formatter с нужным форматом
# Формат: метка времени, название модуля, уровень серьезности, сообщение
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Устанавливаем форматер для file_handler
file_handler.setFormatter(file_formatter)

# Добавляем handler к логеру
logger.addHandler(file_handler)

# Опционально: добавляем вывод в консоль для удобства отладки
console_handler = logging.StreamHandler()
console_handler.setFormatter(file_formatter)
logger.addHandler(console_handler)


def get_mask_card_number(card_number):
    """
    Функция принимает на вход номер карты в виде числа и возвращает маску номера

    Args:
        card_number: Номер карты (число или строка)

    Returns:
        str: Маскированный номер карты или сообщение об ошибке
    """
    logger.debug(f"Вызов get_mask_card_number с аргументом: {card_number}")

    try:
        # Преобразуем число в строку
        card_number_str = str(card_number)

        # Проверяем, что строка состоит только из цифр
        if not card_number_str.isdigit():
            logger.error(
                f"Неверный формат номера карты: {card_number} - содержит не цифры"
            )
            return "Неверный номер карты. Номер должен содержать только цифры."

        # Проверяем длину номера карты
        if len(card_number_str) != 16:
            logger.error(
                f"Неверная длина номера карты: {len(card_number_str)} (ожидается 16)"
            )
            return "Неверный номер карты. Должно быть 16 цифр."

        # Формируем маску в формате "XXXX XX** **** XXXX"
        result = (
            f"{card_number_str[:4]} {card_number_str[4:6]}** "
            f"**** {card_number_str[-4:]}"
        )

        logger.info(
            f"Успешное маскирование номера карты: входной номер замаскирован в {result}"
        )
        logger.debug(f"Результат маскирования карты: {result}")

        return result

    except Exception as e:
        logger.error(f"Непредвиденная ошибка в get_mask_card_number: {e}", exc_info=True)
        return "Ошибка при маскировании номера карты"


def get_mask_account(account_number):
    """
    Функция принимает на вход номер счета в виде числа и возвращает маску номера

    Args:
        account_number: Номер счета (число или строка)

    Returns:
        str: Маскированный номер счета
    """
    logger.debug(f"Вызов get_mask_account с аргументом: {account_number}")

    try:
        account_str = str(account_number)

        # Проверяем, что строка состоит только из цифр
        if not account_str.isdigit():
            logger.error(
                f"Неверный формат номера счета: {account_number} - содержит не цифры"
            )
            return "Неверный номер счета. Номер должен содержать только цифры."

        # Если длина номера счета меньше 4, возвращаем его целиком
        if len(account_str) < 4:
            logger.warning(
                f"Номер счета слишком короткий: {len(account_str)} цифр (меньше 4)"
            )
            logger.info(
                f"Маскирование счета: короткий номер '{account_str}' возвращен без изменений"
            )
            return account_str

        # Создаем маску в формате "**XXXX" (где XXXX - последние 4 цифры)
        result = f"**{account_str[-4:]}"

        logger.info(
            f"Успешное маскирование номера счета: входной номер замаскирован в {result}"
        )
        logger.debug(f"Результат маскирования счета: {result}")

        return result

    except Exception as e:
        logger.error(f"Непредвиденная ошибка в get_mask_account: {e}", exc_info=True)
        return "Ошибка при маскировании номера счета"


# Пример использования для проверки
if __name__ == "__main__":
    # Успешные случаи
    print("=== Успешные случаи ===")
    print(get_mask_card_number(1234567890123456))
    print(get_mask_account(12345678901234567890))

    print("\n=== Ошибочные случаи ===")
    print(get_mask_card_number(12345))
    print(get_mask_card_number("1234abcd5678efgh"))
    print(get_mask_account(123))
    print(get_mask_account("abc123"))