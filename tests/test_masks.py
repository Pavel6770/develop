import pytest
from typing import Any

from src.masks import get_mask_card_number, get_mask_account


@pytest.fixture
def valid_card_number() -> int:
    """Фикстура, предоставляющая корректный номер карты (16 цифр)."""
    return 7000792289606361


@pytest.fixture
def valid_card_number_as_string() -> str:
    """Фикстура, предоставляющая корректный номер карты в виде строки."""
    return "7000792289606361"


@pytest.fixture
def short_card_number() -> int:
    """Фикстура, предоставляющая номер карты с недостаточным количеством цифр."""
    return 700079228960


@pytest.fixture
def long_card_number() -> int:
    """Фикстура, предоставляющая номер карты с избыточным количеством цифр."""
    return 70007922896063611234


@pytest.fixture
def expected_mask() -> str:
    """Фикстура, предоставляющая ожидаемую маску для корректного номера."""
    return "7000 79** **** 6361"


def test_get_mask_card_number_with_valid_integer(
        valid_card_number: int,
        expected_mask: str
) -> None:
    """
    Тестирует маскировку корректного номера карты, переданного как целое число.
    Проверяет, что функция возвращает маску в правильном формате.
    """
    # Act (Действие)
    result = get_mask_card_number(valid_card_number)

    # Assert (Проверка)
    assert result == expected_mask
    assert isinstance(result, str)
    assert len(result) == 19  # "XXXX XX** **** XXXX" = 19 символов с пробелами
    assert result.count(" ") == 3  # Проверяем наличие трех пробелов



def test_get_mask_card_number_with_valid_string(
        valid_card_number_as_string: str,
        expected_mask: str
) -> None:
    """
    Тестирует маскировку корректного номера карты, переданного как строка.
    Проверяет, что функция корректно обрабатывает строковый тип данных.
    """
    # Act (Действие)
    result = get_mask_card_number(valid_card_number_as_string)

    # Assert (Проверка)
    assert result == expected_mask
    assert isinstance(result, str)
    # Проверяем структуру маски
    parts = result.split()
    assert len(parts) == 4
    assert parts[0] == "7000"
    assert parts[1] == "79**"
    assert parts[2] == "****"
    assert parts[3] == "6361"


def test_get_mask_card_number_with_short_number(
        short_card_number: int
) -> None:
    """
    Тестирует обработку номера карты с недостаточным количеством цифр.
    Проверяет, что функция возвращает сообщение об ошибке.
    """
    # Act (Действие)
    result = get_mask_card_number(short_card_number)

    # Assert (Проверка)
    assert result == "Неверный номер карты. Должно быть 16 цифр."
    assert isinstance(result, str)
    # Проверяем, что длина номера действительно меньше 16
    assert len(str(short_card_number)) < 16


def test_get_mask_card_number_with_long_number(
        long_card_number: int
) -> None:
    """
    Тестирует обработку номера карты с избыточным количеством цифр.
    Проверяет, что функция возвращает сообщение об ошибке.
    """
    # Act (Действие)
    result = get_mask_card_number(long_card_number)

    # Assert (Проверка)
    assert result == "Неверный номер карты. Должно быть 16 цифр."
    assert isinstance(result, str)
    # Проверяем, что длина номера больше 16
    assert len(str(long_card_number)) > 16


def test_get_mask_card_number_with_edge_cases() -> None:
    """
    Тестирует маскировку с граничными значениями.
    Проверяет обработку минимального и максимального 16-значных чисел.
    """
    # Arrange (Подготовка)
    min_16_digit = 1000000000000000
    max_16_digit = 9999999999999999

    # Act (Действие)
    result_min = get_mask_card_number(min_16_digit)
    result_max = get_mask_card_number(max_16_digit)

    # Assert (Проверка)
    assert result_min == "1000 00** **** 0000"
    assert result_max == "9999 99** **** 9999"
    # Проверяем формат маски для граничных значений
    assert len(result_min) == 19
    assert len(result_max) == 19


def test_get_mask_card_number_preserves_format_for_valid_numbers() -> None:
    """
    Тестирует, что маска для корректных номеров всегда имеет одинаковый формат.
    Проверяет структуру маски для разных номеров карт.
    """
    # Arrange (Подготовка)
    test_cases = [
        (1234567812345678, "1234 56** **** 5678"),
        (1111222233334444, "1111 22** **** 4444"),
        (9999888877776666, "9999 88** **** 6666"),
    ]

    # Act & Assert (Действие и Проверка)
    for card_number, expected in test_cases:
        result = get_mask_card_number(card_number)
        assert result == expected
        parts = result.split()
        assert len(parts) == 4
        assert parts[1][2:] == "**", "5-я и 6-я цифры должны быть заменены на **"
        assert parts[2] == "****", "7-10 цифры должны быть заменены на ****"

        second_block = parts[1]  # "56**" или "22**" и т.д.
        assert second_block.startswith(second_block[:2])  # первые 2 цифры сохраняются
        assert second_block.endswith("**")  # последние 2 цифры заменены на **

        third_block = parts[2]
        assert third_block == "****"  # все 4 цифры заменены на ****


def test_get_mask_card_number_with_zero_card_number() -> None:
    """
    Тестирует маскировку номера карты, состоящего из 16 нулей.
    Проверяет обработку минимального значения.
    """
    # Arrange (Подготовка)
    zero_card = 0

    # Act (Действие)
    result = get_mask_card_number(zero_card)

    # Assert (Проверка)
    # Число 0 при преобразовании в строку дает "0", что не соответствует 16 цифрам
    assert result == "Неверный номер карты. Должно быть 16 цифр."


def test_get_mask_card_number_handles_leading_zeros() -> None:
    """
    Тестирует маскировку номера карты с ведущими нулями.
    Проверяет, что функция корректно обрабатывает числа с ведущими нулями.
    """
    # Arrange (Подготовка)
    card_with_leading_zeros = "0012345678901234"

    # Act (Действие)
    result = get_mask_card_number(card_with_leading_zeros)

    # Assert (Проверка)
    assert result == "0012 34** **** 1234"
    # Проверяем, что ведущие нули сохранились в маске
    assert result.startswith("0012")


@pytest.fixture
def valid_account_number() -> int:
    """Фикстура, предоставляющая корректный номер счета (более 4 цифр)."""
    return 73654108430135874305


@pytest.fixture
def valid_account_number_as_string() -> str:
    """Фикстура, предоставляющая корректный номер счета в виде строки."""
    return "73654108430135874305"


@pytest.fixture
def short_account_number() -> int:
    """Фикстура, предоставляющая номер счета менее 4 цифр."""
    return 123


@pytest.fixture
def short_account_number_two_digits() -> int:
    """Фикстура, предоставляющая номер счета из 2 цифр."""
    return 45


@pytest.fixture
def expected_mask() -> str:
    """Фикстура, предоставляющая ожидаемую маску для корректного номера."""
    return "**4305"


def test_get_mask_account_with_valid_number(
        valid_account_number: int,
        expected_mask: str
) -> None:
    """
    Тестирует маскировку корректного номера счета, переданного как целое число.
    Проверяет, что функция возвращает маску в формате "**XXXX".
    """
    # Act (Действие)
    result = get_mask_account(valid_account_number)

    # Assert (Проверка)
    assert result == expected_mask
    assert isinstance(result, str)
    assert result.startswith("**")
    assert len(result) == 6  # "**" + 4 цифры = 6 символов
    assert result[-4:] == "4305"  # Последние 4 цифры исходного номера


def test_get_mask_account_with_valid_string(
        valid_account_number_as_string: str,
        expected_mask: str
) -> None:
    """
    Тестирует маскировку корректного номера счета, переданного как строка.
    Проверяет, что функция корректно обрабатывает строковый тип данных.
    """
    # Act (Действие)
    result = get_mask_account(valid_account_number_as_string)

    # Assert (Проверка)
    assert result == expected_mask
    assert isinstance(result, str)
    # Проверяем, что маска содержит только звездочки и последние 4 цифры
    assert result == "**4305"
    assert len(result) == 6


def test_get_mask_account_with_short_number_less_than_four_digits(
        short_account_number: int
) -> None:
    """
    Тестирует обработку номера счета с менее чем 4 цифрами.
    Проверяет, что функция возвращает номер целиком без маскировки.
    """
    # Act (Действие)
    result = get_mask_account(short_account_number)

    # Assert (Проверка)
    assert result == "123"
    assert isinstance(result, str)
    assert "**" not in result  # Маска не применяется
    assert len(result) == 3
    # Проверяем, что номер счета меньше 4 цифр
    assert len(str(short_account_number)) < 4


def test_get_mask_account_with_two_digits_number(
        short_account_number_two_digits: int
) -> None:
    """
    Тестирует обработку номера счета с двумя цифрами.
    Проверяет, что функция возвращает номер целиком без маскировки.
    """
    # Act (Действие)
    result = get_mask_account(short_account_number_two_digits)

    # Assert (Проверка)
    assert result == "45"
    assert isinstance(result, str)
    assert "**" not in result
    assert len(result) == 2


def test_get_mask_account_with_exactly_four_digits() -> None:
    """
    Тестирует маскировку номера счета, содержащего ровно 4 цифры.
    Проверяет, что маска применяется даже к 4-значному номеру.
    """
    # Arrange (Подготовка)
    four_digit_account = 1234

    # Act (Действие)
    result = get_mask_account(four_digit_account)

    # Assert (Проверка)
    assert result == "**1234"
    assert isinstance(result, str)
    assert result.startswith("**")
    assert result[-4:] == "1234"
    assert len(result) == 6


def test_get_mask_account_with_empty_string() -> None:
    """
    Тестирует обработку пустой строки в качестве номера счета.
    Проверяет, что функция возвращает пустую строку.
    """
    # Arrange (Подготовка)
    empty_account = ""

    # Act (Действие)
    result = get_mask_account(empty_account)

    # Assert (Проверка)
    assert result == ""
    assert isinstance(result, str)
    assert len(result) == 0


def test_get_mask_account_with_zero() -> None:
    """
    Тестирует маскировку номера счета, равного нулю.
    Проверяет обработку граничного значения.
    """
    # Arrange (Подготовка)
    zero_account = 0

    # Act (Действие)
    result = get_mask_account(zero_account)

    # Assert (Проверка)
    # 0 при преобразовании в строку дает "0" (1 цифра), возвращаем целиком
    assert result == "0"
    assert "**" not in result


def test_get_mask_account_with_leading_zeros() -> None:
    """
    Тестирует маскировку номера счета с ведущими нулями.
    Проверяет, что функция корректно обрабатывает строки с ведущими нулями.
    """
    # Arrange (Подготовка)
    account_with_zeros = "001234"

    # Act (Действие)
    result = get_mask_account(account_with_zeros)

    # Assert (Проверка)
    assert result == "**1234"
    # Проверяем, что ведущие нули не влияют на последние 4 цифры
    assert result[-4:] == "1234"


def test_get_mask_account_preserves_last_four_digits_for_long_numbers() -> None:
    """
    Тестирует, что для длинных номеров счетов всегда берутся последние 4 цифры.
    Проверяет правильность извлечения последних 4 цифр для номеров разной длины.
    """
    # Arrange (Подготовка)
    test_cases = [
        (12345678, "**5678"),
        (987654321, "**4321"),
        (111111111111, "**1111"),
        (12345678901234567890, "**7890"),
    ]

    # Act & Assert (Действие и Проверка)
    for account_number, expected in test_cases:
        result = get_mask_account(account_number)
        assert result == expected
        assert result.startswith("**")
        # Проверяем, что последние 4 цифры соответствуют исходному номеру
        account_str = str(account_number)
        assert result[-4:] == account_str[-4:]


def test_get_mask_account_handles_different_numeric_types() -> None:
    """
    Тестирует обработку различных числовых типов данных.
    Проверяет работу с int, str и другими типами.
    """
    # Arrange (Подготовка)
    test_cases = [
        (73654108430135874305, "**4305"),
        ("73654108430135874305", "**4305"),
        (123, "123"),
        ("45", "45"),
    ]

    # Act & Assert (Действие и Проверка)
    for account_input, expected in test_cases:
        result = get_mask_account(account_input)
        assert result == expected
        assert isinstance(result, str)

if __name__ == "__main__":
    pytest.main(["-v", __file__])


