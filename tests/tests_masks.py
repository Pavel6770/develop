import pytest
from typing import Any

from src.masks import get_mask_card_number, get_mask_account


# Fixtures for common test data
@pytest.fixture
def valid_card_numbers() -> list[tuple[Any, str]]:
    """Fixture providing valid card numbers and their expected masked formats."""
    return [
        (7000792289606361, "7000 79** **** 6361"),
        (1234567890123456, "1234 56** **** 3456"),
        (1111222233334444, "1111 22** **** 4444"),
        (9999999999999999, "9999 99** **** 9999"),
        (1000000000000000, "1000 00** **** 0000"),
    ]


@pytest.fixture
def invalid_card_numbers() -> list[tuple[Any, str]]:
    """Fixture providing invalid card numbers and their expected error messages."""
    return [
        (123456789012345, "Неверный номер карты. Должно быть 16 цифр."),
        (12345678901234567, "Неверный номер карты. Должно быть 16 цифр."),
        (0, "Неверный номер карты. Должно быть 16 цифр."),
        (None, "Неверный номер карты. Должно быть 16 цифр."),
        ("", "Неверный номер карты. Должно быть 16 цифр."),
        ("   ", "Неверный номер карты. Должно быть 16 цифр."),
    ]


@pytest.fixture
def card_numbers_with_leading_zeros() -> list[tuple[Any, str]]:
    """Fixture providing card numbers with leading zeros."""
    return [
        ("0123456789012345", "0123 45** **** 2345"),
        ("0011223344556677", "0011 22** **** 6677"),
        ("0000123456789012", "0000 12** **** 9012"),
    ]


@pytest.fixture
def valid_account_numbers() -> list[tuple[Any, str]]:
    """Fixture providing valid account numbers and their expected masked formats."""
    return [
        (73654108430135874305, "**4305"),
        (123456789, "**6789"),
        (1000200030004000, "**4000"),
        (1111222233334444, "**4444"),
        (12345, "**2345"),
        (1234, "**1234"),
    ]


@pytest.fixture
def short_account_numbers() -> list[tuple[Any, str]]:
    """Fixture providing short account numbers (less than 4 digits)."""
    return [
        (123, "123"),
        (12, "12"),
        (1, "1"),
        (0, "0"),
        (-123, "-123"),
        (-5, "-5"),
    ]


@pytest.fixture
def account_numbers_with_leading_zeros() -> list[tuple[Any, str]]:
    """Fixture providing account numbers with leading zeros."""
    return [
        ("001234", "**1234"),
        ("000123", "**0123"),
        ("000012", "**0012"),
        ("0000", "**0000"),
        ("000", "000"),
        ("00001234", "**1234"),
        ("00000000", "**0000"),
    ]


@pytest.fixture
def invalid_account_inputs() -> list[tuple[Any, str]]:
    """Fixture providing invalid inputs for account masking."""
    return [
        (None, "None"),
        ("", ""),
        ("   ", "   "),
        ([1, 2, 3], "[1, 2, 3]"),
        ({}, "{}"),
        ((), "()"),
        ("abc", "abc"),
        ("a1b2c3", "a1b2c3"),
        ("!@#$", "!@#$"),
    ]


class TestGetMaskCardNumber:
    """Класс с тестами для функции маскирования номера карты."""

    # Тестирование правильности маскирования номера карты
    @pytest.mark.parametrize(
        "input_card,expected_output",
        [
            (7000792289606361, "7000 79** **** 6361"),
            (1234567890123456, "1234 56** **** 3456"),
            (1111222233334444, "1111 22** **** 4444"),
        ],
    )
    def test_correct_masking(self, input_card: Any, expected_output: str) -> None:
        """Тестирование правильности маскирования номера карты."""
        assert get_mask_card_number(input_card) == expected_output

    # Тестирование с использованием фикстуры валидных номеров
    def test_correct_masking_with_fixture(self, valid_card_numbers: list[tuple[Any, str]]) -> None:
        """Тестирование правильности маскирования с использованием фикстуры."""
        for input_card, expected_output in valid_card_numbers:
            assert get_mask_card_number(input_card) == expected_output

    # Проверка работы функции на различных входных форматах
    @pytest.mark.parametrize(
        "input_card,expected_output",
        [
            # Номера разной длины
            (123456789012345, "Неверный номер карты. Должно быть 16 цифр."),
            (12345678901234567, "Неверный номер карты. Должно быть 16 цифр."),
            (0, "Неверный номер карты. Должно быть 16 цифр."),
            (1234567890123456, "1234 56** **** 3456"),
            # Номера с ведущими нулями
            ("0123456789012345", "0123 45** **** 2345"),
            ("0011223344556677", "0011 22** **** 6677"),
            # Номера в разных форматах (как строки)
            ("7000792289606361", "7000 79** **** 6361"),
            ("1234 5678 9012 3456", "Неверный номер карты. Должно быть 16 цифр."),
            ("1234-5678-9012-3456", "Неверный номер карты. Должно быть 16 цифр."),
            # Крайние случаи
            (9999999999999999, "9999 99** **** 9999"),
            (1000000000000000, "1000 00** **** 0000"),
        ],
    )
    def test_various_formats(self, input_card: Any, expected_output: str) -> None:
        """Проверка работы функции на различных входных форматах."""
        assert get_mask_card_number(input_card) == expected_output

    # Проверка обработки отсутствия номера карты с использованием фикстуры
    def test_missing_card_number(self, invalid_card_numbers: list[tuple[Any, str]]) -> None:
        """Проверка обработки отсутствия номера карты."""
        for input_card, expected_output in invalid_card_numbers:
            assert get_mask_card_number(input_card) == expected_output

    # Тестирование номеров с ведущими нулями с использованием фикстуры
    def test_card_numbers_with_leading_zeros(self, card_numbers_with_leading_zeros: list[tuple[Any, str]]) -> None:
        """Тестирование номеров карт с ведущими нулями."""
        for input_card, expected_output in card_numbers_with_leading_zeros:
            assert get_mask_card_number(input_card) == expected_output

    # Дополнительные тесты для граничных случаев
    def test_edge_cases(self) -> None:
        """Тестирование граничных случаев."""
        # Минимальное 16-значное число
        assert get_mask_card_number(1000000000000000) == "1000 00** **** 0000"

        # Максимальное 16-значное число
        assert get_mask_card_number(9999999999999999) == "9999 99** **** 9999"

        # Число с одинаковыми цифрами
        assert get_mask_card_number(1111111111111111) == "1111 11** **** 1111"

        # Число с ведущими нулями как строка
        assert get_mask_card_number("0000123456789012") == "0000 12** **** 9012"


class TestGetMaskAccount:
    """Класс с тестами для функции маскирования номера счета."""

    # Тестирование правильности маскирования номера счета
    @pytest.mark.parametrize(
        "input_account,expected_output",
        [
            (73654108430135874305, "**4305"),
            (123456789, "**6789"),
            (1000200030004000, "**4000"),
            (1111222233334444, "**4444"),
            (12345, "**2345"),
        ],
    )
    def test_correct_masking(self, input_account: Any, expected_output: str) -> None:
        """Тестирование правильности маскирования номера счета."""
        assert get_mask_account(input_account) == expected_output

    # Тестирование с использованием фикстуры валидных номеров счетов
    def test_correct_masking_with_fixture(self, valid_account_numbers: list[tuple[Any, str]]) -> None:
        """Тестирование правильности маскирования с использованием фикстуры."""
        for input_account, expected_output in valid_account_numbers:
            assert get_mask_account(input_account) == expected_output

    # Проверка работы функции с различными форматами и длинами
    @pytest.mark.parametrize(
        "input_account,expected_output",
        [
            # Номера разной длины
            (123, "123"),  # Меньше 4 цифр
            (12, "12"),  # Меньше 4 цифр
            (1, "1"),  # Меньше 4 цифр
            (0, "0"),  # Меньше 4 цифр
            (1234, "**1234"),  # Ровно 4 цифры
            (12345, "**2345"),  # 5 цифр
            (123456, "**3456"),  # 6 цифр
            (1234567, "**4567"),  # 7 цифр
            (12345678, "**5678"),  # 8 цифр
            (12345678901234567890, "**7890"),  # 20 цифр
            # Номера с ведущими нулями
            ("001234", "**1234"),
            ("000123", "**0123"),
            ("000012", "**0012"),
            ("0000", "**0000"),
            ("000", "000"),
            # Номера в разных форматах (как строки)
            ("12345678901234567890", "**7890"),
            ("7365 4108 4301 3587 4305", "7365 4108 4301 3587 4305"),
            ("7365-4108-4301-3587-4305", "7365-4108-4301-3587-4305"),
            # Крайние случаи
            (9999, "**9999"),
            (1000, "**1000"),
            (99999999999999999999, "**9999"),
        ],
    )
    def test_various_formats_and_lengths(self, input_account: Any, expected_output: str) -> None:
        """Проверка работы функции с различными форматами и длинами номеров счетов."""
        assert get_mask_account(input_account) == expected_output

    # Проверка обработки коротких номеров счетов с использованием фикстуры
    def test_short_account_numbers(self, short_account_numbers: list[tuple[Any, str]]) -> None:
        """Проверка обработки коротких и нестандартных номеров счетов."""
        for input_account, expected_output in short_account_numbers:
            assert get_mask_account(input_account) == expected_output

    # Тестирование номеров счетов с ведущими нулями с использованием фикстуры
    def test_account_numbers_with_leading_zeros(self, account_numbers_with_leading_zeros: list[tuple[Any, str]]) -> None:
        """Тестирование номеров счетов с ведущими нулями."""
        for input_account, expected_output in account_numbers_with_leading_zeros:
            assert get_mask_account(input_account) == expected_output

    # Проверка обработки невалидных входных данных с использованием фикстуры
    def test_invalid_account_inputs(self, invalid_account_inputs: list[tuple[Any, str]]) -> None:
        """Проверка обработки невалидных входных данных."""
        for input_account, expected_output in invalid_account_inputs:
            assert get_mask_account(input_account) == expected_output

    # Дополнительные тесты для граничных случаев
    def test_edge_cases(self) -> None:
        """Тестирование граничных случаев."""
        # Минимальное 4-значное число
        assert get_mask_account(1000) == "**1000"

        # Максимальное 4-значное число
        assert get_mask_account(9999) == "**9999"

        # Число с одинаковыми цифрами
        assert get_mask_account(1111) == "**1111"
        assert get_mask_account(11111) == "**1111"

        # Число с ведущими нулями как строка
        assert get_mask_account("00001234") == "**1234"
        assert get_mask_account("00000000") == "**0000"

        # Очень длинные номера
        long_number = "1" * 100
        assert get_mask_account(long_number) == f"**{long_number[-4:]}"

    def test_type_preservation(self) -> None:
        """Проверка, что функция всегда возвращает строку."""
        test_cases: list[Any] = [
            123456789,
            "123456789",
            123,
            "",
            None,
            [1, 2, 3],
            {"key": "value"},
        ]

        for case in test_cases:
            result = get_mask_account(case)
            assert isinstance(result, str), (
                f"Для входа {case} результат должен быть строкой"
            )

    def test_last_four_digits_correctness(self) -> None:
        """Проверка, что маскируются именно последние 4 цифры."""
        # Для номеров разной длины проверяем последние 4 цифры
        test_numbers = [
            (1234567890, "**7890"),
            (987654321, "**4321"),
            (555666777888999, "**8999"),
            ("abcdefghijk", "**hijk"),
        ]

        for number, expected in test_numbers:
            result = get_mask_account(number)
            if len(str(number)) >= 4:
                assert result == expected
                # Проверяем, что последние 4 символа совпадают
                assert result[-4:] == str(number)[-4:]


if __name__ == "__main__":
    pytest.main(["-v", __file__])


