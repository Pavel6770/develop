import pytest
from typing import Any
from unittest.mock import Mock
from datetime import datetime

from src.widget import mask_account_card, get_date


# Fixtures for common test data
@pytest.fixture
def mock_mask_account():
    """Fixture providing a mock function for account masking."""

    def _mock_mask_account(account_number: str) -> str:
        return f"**{account_number[-4:]}"

    return _mock_mask_account


@pytest.fixture
def mock_mask_card_number():
    """Fixture providing a mock function for card number masking."""

    def _mock_mask_card_number(card_number: str) -> str:
        clean_number = card_number.replace(" ", "")
        if len(clean_number) == 16:
            return f"{clean_number[:4]} {clean_number[4:6]}** **** {clean_number[-4:]}"
        return f"Ошибка: {card_number}"

    return _mock_mask_card_number


@pytest.fixture
def mock_functions():
    """Fixture providing both mock functions."""
    return {
        "account": Mock(return_value="mocked_account"),
        "card": Mock(return_value="mocked_card")
    }


@pytest.fixture
def error_mask_function():
    """Fixture providing an error mask function."""

    def _error_mask_function(num: str) -> str:
        return f"Error: {num}"

    return _error_mask_function


@pytest.fixture
def real_mask_functions():
    """Fixture providing real mask functions for testing."""

    def real_mask_account(num: str) -> str:
        return f"**{num[-4:]}"

    def real_mask_card(num: str) -> str:
        clean_num = num.replace(" ", "")
        if len(clean_num) == 16:
            return f"{clean_num[:4]} {clean_num[4:6]}** **** {clean_num[-4:]}"
        return "Invalid card"

    return {"account": real_mask_account, "card": real_mask_card}


@pytest.fixture
def test_cases_accounts():
    """Fixture providing test cases for accounts."""
    return [
        ("Счет 73654108430135874305", "Счет **4305"),
        ("Счет 12345678901234567890", "Счет **7890"),
        ("Счет 1000200030004000", "Счет **4000"),
        ("Счет 12345", "Счет **2345"),
        ("Счет 123456", "Счет **3456"),
        ("Счет 1234567", "Счет **4567"),
        ("Счет 12345678", "Счет **5678"),
        ("Счет 123456789", "Счет **6789"),
        ("Счет 1234567890", "Счет **7890"),
    ]


@pytest.fixture
def test_cases_cards():
    """Fixture providing test cases for cards."""
    return [
        ("Visa Platinum 7000792289606361", "Visa Platinum 7000 79** **** 6361"),
        ("Maestro 7000792289606361", "Maestro 7000 79** **** 6361"),
        ("MasterCard 1234567890123456", "MasterCard 1234 56** **** 3456"),
        ("Visa Classic 1111222233334444", "Visa Classic 1111 22** **** 4444"),
        ("American Express 1234567890123456", "American Express 1234 56** **** 3456"),
        ("Visa 1234567890123456", "Visa 1234 56** **** 3456"),
        ("MasterCard 9876543210987654", "MasterCard 9876 54** **** 7654"),
        ("Maestro 5555666677778888", "Maestro 5555 66** **** 8888"),
        ("МИР 1111222233334444", "МИР 1111 22** **** 4444"),
        ("UnionPay 1234123412341234", "UnionPay 1234 12** **** 1234"),
        ("JCB 4321432143214321", "JCB 4321 43** **** 4321"),
    ]


@pytest.fixture
def test_cases_cards_with_composite_names():
    """Fixture providing test cases for cards with composite names."""
    return [
        ("Visa Gold 7000792289606361", "Visa Gold 7000 79** **** 6361"),
        ("MasterCard Black Edition 1234567890123456", "MasterCard Black Edition 1234 56** **** 3456"),
        ("American Express Platinum 1111222233334444", "American Express Platinum 1111 22** **** 4444"),
    ]


@pytest.fixture
def test_cases_with_spaces():
    """Fixture providing test cases with spaces in numbers."""
    return [
        ("Visa 7000 7922 8960 6361", "Visa 7000 79** **** 6361"),
        ("MasterCard 1234 5678 9012 3456", "MasterCard 1234 56** **** 3456"),
    ]


@pytest.fixture
def test_cases_leading_zeros():
    """Fixture providing test cases with leading zeros."""
    return [
        ("Счет 001234567890", "Счет **7890"),
        ("Счет 000012345678", "Счет **5678"),
    ]


@pytest.fixture
def invalid_inputs():
    """Fixture providing invalid inputs for mask_account_card."""
    return [
        ("", IndexError, "Передана пустая строка"),
        ("   ", IndexError, "Передана пустая строка"),
        ("Счет", IndexError, "Не указан номер счета"),
        ("Visa", IndexError, "Не указан номер карты"),
        ("MasterCard Platinum", IndexError, "Не указан номер карты"),
        ("Счет ", IndexError, "Не указан номер счета"),
        ("Visa ", IndexError, "Не указан номер карты"),
        ("Счет-73654108430135874305", IndexError, "Не указан номер счета"),
        ("Visa-Platinum-7000792289606361", IndexError, "Не указан номер карты"),
    ]


@pytest.fixture
def number_format_cases():
    """Fixture providing test cases for number format preservation."""
    return [
        ("Visa 7000792289606361", "7000792289606361", None),
        ("MasterCard 1234 5678 9012 3456", "1234 5678 9012 3456", None),
        ("Счет 73654108430135874305", None, "73654108430135874305"),
        ("Счет 1234 5678 9012 3456 7890", None, "1234 5678 9012 3456 7890"),
    ]


@pytest.fixture
def date_test_cases():
    """Fixture providing test cases for date conversion."""
    return [
        ("2024-03-11T02:26:18.671407", "11.03.2024"),
        ("2023-12-31T23:59:59.999999", "31.12.2023"),
        ("2024-01-01T00:00:00.000000", "01.01.2024"),
        ("2024-02-29T12:00:00.000000", "29.02.2024"),
        ("2023-02-28T12:00:00.000000", "28.02.2023"),
        ("2024-04-30T12:00:00.000000", "30.04.2024"),
        ("2024-06-01T12:00:00.000000", "01.06.2024"),
        ("2000-01-01T00:00:00.000000", "01.01.2000"),
        ("1999-12-31T23:59:59.999999", "31.12.1999"),
        ("2100-12-31T23:59:59.999999", "31.12.2100"),
    ]


@pytest.fixture
def date_format_cases():
    """Fixture providing test cases for various date formats."""
    return [
        ("2024-03-11T02:26:18", "11.03.2024"),
        ("2023-12-31T23:59:59", "31.12.2023"),
        ("2024-03-11T02:26:18+03:00", "11.03.2024"),
        ("2024-03-11T02:26:18-05:00", "11.03.2024"),
        ("2024-03-11T02:26:18+00:00", "11.03.2024"),
        ("2024-03-11T02:26:18Z", "11.03.2024"),
        ("2024-03-11", "11.03.2024"),
        ("2023-12-31", "31.12.2023"),
        ("0001-01-01T00:00:00", "01.01.0001"),
        ("9999-12-31T23:59:59", "31.12.9999"),
        ("2024/03/11T02:26:18", "11.03.2024"),
        ("2024.03.11T02:26:18", "11.03.2024"),
    ]


@pytest.fixture
def invalid_date_inputs():
    """Fixture providing invalid date inputs."""
    return [
        ("", ValueError, "Строка '' не соответствует формату ISO"),
        ("   ", ValueError, "Строка '   ' не соответствует формату ISO"),
        ("2024", ValueError, "Строка '2024' не соответствует формату ISO"),
        ("2024-03", ValueError, "Строка '2024-03' не соответствует формату ISO"),
        ("2024-03-11T", ValueError, "Строка '2024-03-11T' не соответствует формату ISO"),
        ("2024.03.11 02:26:18", ValueError, "Строка '2024.03.11 02:26:18' не соответствует формату ISO"),
        ("11-03-2024T02:26:18", ValueError, "Строка '11-03-2024T02:26:18' не соответствует формату ISO"),
        ("2024-02-30T12:00:00", ValueError, "Строка '2024-02-30T12:00:00' не соответствует формату ISO"),
        ("2024-04-31T12:00:00", ValueError, "Строка '2024-04-31T12:00:00' не соответствует формату ISO"),
        ("2023-02-29T12:00:00", ValueError, "Строка '2023-02-29T12:00:00' не соответствует формату ISO"),
        ("abc", ValueError, "Строка 'abc' не соответствует формату ISO"),
        ("2024-03-11T25:00:00", ValueError, "Строка '2024-03-11T25:00:00' не соответствует формату ISO"),
        ("2024-03-11T02:60:00", ValueError, "Строка '2024-03-11T02:60:00' не соответствует формату ISO"),
        ("2024-03-11T02:26:60", ValueError, "Строка '2024-03-11T02:26:60' не соответствует формату ISO"),
    ]


@pytest.fixture
def non_string_inputs():
    """Fixture providing non-string inputs for date function."""
    return [
        (None, TypeError, "Ожидалась строка, получен NoneType"),
        (123, TypeError, "Ожидалась строка, получен int"),
        (45.67, TypeError, "Ожидалась строка, получен float"),
        ([], TypeError, "Ожидалась строка, получен list"),
        ({}, TypeError, "Ожидалась строка, получен dict"),
        (True, TypeError, "Ожидалась строка, получен bool"),
        (datetime.now(), TypeError, "Ожидалась строка, получен datetime"),
    ]


@pytest.fixture
def timezone_test_cases():
    """Fixture providing test cases with different timezones."""
    return [
        ("2024-03-11T00:00:00+00:00", "11.03.2024"),
        ("2024-03-11T23:59:59+03:00", "11.03.2024"),
        ("2024-03-11T02:26:18-05:00", "11.03.2024"),
        ("2024-03-11T12:00:00Z", "11.03.2024"),
    ]


@pytest.fixture
def microseconds_test_cases():
    """Fixture providing test cases with different microsecond precision."""
    return [
        ("2024-03-11T02:26:18.1", "11.03.2024"),
        ("2024-03-11T02:26:18.12", "11.03.2024"),
        ("2024-03-11T02:26:18.123", "11.03.2024"),
        ("2024-03-11T02:26:18.123456", "11.03.2024"),
        ("2024-03-11T02:26:18.123456789", "11.03.2024"),
    ]


if __name__ == "__main__":
    pytest.main(["-v", __file__])