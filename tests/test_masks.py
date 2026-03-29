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


if __name__ == "__main__":
    pytest.main(["-v", __file__])


