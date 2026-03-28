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


class TestMaskAccountCard:
    """Класс с тестами для функции маскировки номера карты или счета."""

    # Тесты для проверки корректного распознавания типа (карта или счет)
    @pytest.mark.parametrize(
        "input_info,expected_output",
        [
            ("Счет 73654108430135874305", "Счет **4305"),
            ("Счет 12345678901234567890", "Счет **7890"),
            ("Счет 1000200030004000", "Счет **4000"),
            ("Visa Platinum 7000792289606361", "Visa Platinum 7000 79** **** 6361"),
            ("Maestro 7000792289606361", "Maestro 7000 79** **** 6361"),
            ("MasterCard 1234567890123456", "MasterCard 1234 56** **** 3456"),
            ("Visa Classic 1111222233334444", "Visa Classic 1111 22** **** 4444"),
            ("American Express 1234567890123456", "American Express 1234 56** **** 3456"),
        ],
    )
    def test_correct_type_recognition(
            self,
            input_info: str,
            expected_output: str,
            mock_mask_account,
            mock_mask_card_number
    ) -> None:
        """Тест корректного распознавания типа (карта или счет)."""
        result = mask_account_card(
            input_info,
            mock_mask_account,
            mock_mask_card_number
        )
        assert result == expected_output

    # Параметризованные тесты с разными типами карт с использованием фикстур
    def test_various_card_types(
            self,
            test_cases_cards,
            mock_mask_account,
            mock_mask_card_number
    ) -> None:
        """Параметризованные тесты с разными типами карт."""
        for input_info, expected_output in test_cases_cards:
            result = mask_account_card(
                input_info,
                mock_mask_account,
                mock_mask_card_number
            )
            assert result == expected_output

    # Параметризованные тесты с разными типами счетов с использованием фикстур
    def test_various_account_types(
            self,
            test_cases_accounts,
            mock_mask_account,
            mock_mask_card_number
    ) -> None:
        """Параметризованные тесты с разными типами счетов."""
        for input_info, expected_output in test_cases_accounts:
            result = mask_account_card(
                input_info,
                mock_mask_account,
                mock_mask_card_number
            )
            assert result == expected_output

    # Тесты с составными названиями карт
    def test_composite_card_names(
            self,
            test_cases_cards_with_composite_names,
            mock_mask_account,
            mock_mask_card_number
    ) -> None:
        """Тесты с составными названиями карт."""
        for input_info, expected_output in test_cases_cards_with_composite_names:
            result = mask_account_card(
                input_info,
                mock_mask_account,
                mock_mask_card_number
            )
            assert result == expected_output

    # Тесты с пробелами в номерах
    def test_spaces_in_numbers(
            self,
            test_cases_with_spaces,
            mock_mask_account,
            mock_mask_card_number
    ) -> None:
        """Тесты с пробелами в номерах."""
        for input_info, expected_output in test_cases_with_spaces:
            result = mask_account_card(
                input_info,
                mock_mask_account,
                mock_mask_card_number
            )
            assert result == expected_output

    # Тесты с ведущими нулями
    def test_leading_zeros(
            self,
            test_cases_leading_zeros,
            mock_mask_account,
            mock_mask_card_number
    ) -> None:
        """Тесты с ведущими нулями."""
        for input_info, expected_output in test_cases_leading_zeros:
            result = mask_account_card(
                input_info,
                mock_mask_account,
                mock_mask_card_number
            )
            assert result == expected_output

    # Параметризованные тесты с разными типами карт и счетов (оригинальные)
    @pytest.mark.parametrize(
        "input_info,expected_output",
        [
            ("Visa 1234567890123456", "Visa 1234 56** **** 3456"),
            ("MasterCard 9876543210987654", "MasterCard 9876 54** **** 7654"),
            ("Maestro 5555666677778888", "Maestro 5555 66** **** 8888"),
            ("МИР 1111222233334444", "МИР 1111 22** **** 4444"),
            ("UnionPay 1234123412341234", "UnionPay 1234 12** **** 1234"),
            ("JCB 4321432143214321", "JCB 4321 43** **** 4321"),
            ("Visa Gold 7000792289606361", "Visa Gold 7000 79** **** 6361"),
        ],
    )
    def test_various_card_and_account_types(
            self,
            input_info: str,
            expected_output: str,
            mock_mask_account,
            mock_mask_card_number
    ) -> None:
        """Параметризованные тесты с разными типами карт и счетов."""
        result = mask_account_card(
            input_info,
            mock_mask_account,
            mock_mask_card_number
        )
        assert result == expected_output

    # Тестирование обработки некорректных входных данных с использованием фикстуры
    def test_invalid_input_handling_with_fixture(
            self,
            invalid_inputs,
            mock_mask_account,
            mock_mask_card_number
    ) -> None:
        """Тестирование обработки некорректных входных данных."""
        for input_info, expected_exception, expected_message in invalid_inputs:
            with pytest.raises(expected_exception, match=expected_message):
                mask_account_card(
                    input_info,
                    mock_mask_account,
                    mock_mask_card_number
                )

    # Тестирование обработки некорректных входных данных (оригинальные)
    @pytest.mark.parametrize(
        "input_info,expected_exception,expected_message",
        [
            ("", IndexError, "Передана пустая строка"),
            ("   ", IndexError, "Передана пустая строка"),
            ("Счет", IndexError, "Не указан номер счета"),
            ("Visa", IndexError, "Не указан номер карты"),
        ],
    )
    def test_invalid_input_handling(
            self,
            input_info: str,
            expected_exception: Any,
            expected_message: str,
            mock_mask_account,
            mock_mask_card_number
    ) -> None:
        """Тестирование обработки некорректных входных данных."""
        with pytest.raises(expected_exception, match=expected_message):
            mask_account_card(
                input_info,
                mock_mask_account,
                mock_mask_card_number
            )

    # Тесты с моками для проверки вызова правильных функций
    def test_correct_function_calls_for_card(self, mock_functions) -> None:
        """Проверка вызова правильной функции для карты."""
        result = mask_account_card(
            "Visa Platinum 7000792289606361",
            mock_functions["account"],
            mock_functions["card"]
        )

        mock_functions["card"].assert_called_once_with("7000792289606361")
        mock_functions["account"].assert_not_called()
        assert result == "Visa Platinum mocked_card"

    def test_correct_function_calls_for_account(self, mock_functions) -> None:
        """Проверка вызова правильной функции для счета."""
        result = mask_account_card(
            "Счет 73654108430135874305",
            mock_functions["account"],
            mock_functions["card"]
        )

        mock_functions["account"].assert_called_once_with("73654108430135874305")
        mock_functions["card"].assert_not_called()
        assert result == "Счет mocked_account"

    # Тесты для проверки обработки различных форматов номеров
    def test_number_format_preservation(
            self,
            number_format_cases,
            mock_functions
    ) -> None:
        """Проверка передачи номера в исходном формате в функции маскировки."""
        for input_info, expected_card_call, expected_account_call in number_format_cases:
            # Сброс моков перед каждым тестом
            mock_functions["card"].reset_mock()
            mock_functions["account"].reset_mock()

            mask_account_card(
                input_info,
                mock_functions["account"],
                mock_functions["card"]
            )

            if expected_card_call:
                mock_functions["card"].assert_called_once_with(expected_card_call)
                mock_functions["account"].assert_not_called()
            if expected_account_call:
                mock_functions["account"].assert_called_once_with(expected_account_call)
                mock_functions["card"].assert_not_called()

    # Тест с реальными функциями маскировки
    def test_with_real_mask_functions(self, real_mask_functions) -> None:
        """Тест с реальными функциями маскировки."""
        test_cases = [
            ("Visa Platinum 7000792289606361", "Visa Platinum 7000 79** **** 6361"),
            ("Счет 73654108430135874305", "Счет **4305"),
            ("Maestro 1234567890123456", "Maestro 1234 56** **** 3456"),
        ]

        for input_info, expected in test_cases:
            result = mask_account_card(
                input_info,
                real_mask_functions["account"],
                real_mask_functions["card"]
            )
            assert result == expected

    # Тест на устойчивость к ошибкам в функциях маскировки
    def test_error_handling_from_mask_functions(self, error_mask_function) -> None:
        """Проверка обработки ошибок из функций маскировки."""
        result_card = mask_account_card(
            "Visa 1234567890123456",
            error_mask_function,
            error_mask_function
        )
        assert result_card == "Visa Error: 1234567890123456"

        result_account = mask_account_card(
            "Счет 1234567890",
            error_mask_function,
            error_mask_function
        )
        assert result_account == "Счет Error: 1234567890"


class TestGetDate:
    """Класс с тестами для функции преобразования даты."""

    # Тестирование правильности преобразования даты
    def test_correct_date_conversion(self, date_test_cases) -> None:
        """Тестирование правильности преобразования даты."""
        for input_date, expected_output in date_test_cases:
            assert get_date(input_date) == expected_output

    # Проверка работы функции на различных входных форматах
    def test_various_date_formats(self, date_format_cases) -> None:
        """Проверка работы функции на различных входных форматах даты."""
        for input_date, expected_output in date_format_cases:
            assert get_date(input_date) == expected_output

    # Проверка обработки некорректных входных данных с использованием фикстуры
    def test_invalid_date_handling_with_fixture(self, invalid_date_inputs) -> None:
        """Проверка обработки некорректных входных данных."""
        for input_date, expected_exception, expected_message in invalid_date_inputs:
            with pytest.raises(expected_exception, match=expected_message):
                get_date(input_date)

    # Проверка обработки некорректных входных данных (оригинальные)
    @pytest.mark.parametrize(
        "input_date,expected_exception,expected_message",
        [
            ("", ValueError, "Строка '' не соответствует формату ISO"),
            ("2024", ValueError, "Строка '2024' не соответствует формату ISO"),
            ("2024-02-30T12:00:00", ValueError, "Строка '2024-02-30T12:00:00' не соответствует формату ISO"),
        ],
    )
    def test_invalid_date_handling(
            self,
            input_date: str,
            expected_exception: Any,
            expected_message: str
    ) -> None:
        """Проверка обработки некорректных входных данных."""
        with pytest.raises(expected_exception, match=expected_message):
            get_date(input_date)

    # Проверка обработки отсутствия даты (нестроковые типы) с использованием фикстуры
    def test_non_string_input_with_fixture(self, non_string_inputs) -> None:
        """Проверка обработки нестроковых типов данных."""
        for input_date, expected_exception, expected_message in non_string_inputs:
            with pytest.raises(expected_exception, match=expected_message):
                get_date(input_date)  # type: ignore

    # Проверка обработки отсутствия даты (нестроковые типы) (оригинальные)
    @pytest.mark.parametrize(
        "input_date,expected_exception,expected_message",
        [
            (None, TypeError, "Ожидалась строка, получен NoneType"),
            (123, TypeError, "Ожидалась строка, получен int"),
            ([], TypeError, "Ожидалась строка, получен list"),
        ],
    )
    def test_non_string_input(
            self,
            input_date: Any,
            expected_exception: Any,
            expected_message: str
    ) -> None:
        """Проверка обработки нестроковых типов данных."""
        with pytest.raises(expected_exception, match=expected_message):
            get_date(input_date)  # type: ignore

    # Дополнительные тесты для граничных случаев
    def test_edge_cases(self) -> None:
        """Тестирование граничных случаев."""
        assert get_date("0001-01-01T00:00:00") == "01.01.0001"
        assert get_date("9999-12-31T23:59:59") == "31.12.9999"
        assert get_date("2020-02-29T12:00:00") == "29.02.2020"
        assert get_date("2024-01-01T00:00:00") == "01.01.2024"
        assert get_date("2024-12-31T23:59:59") == "31.12.2024"

    def test_timezone_handling(self, timezone_test_cases) -> None:
        """Проверка обработки разных часовых поясов."""
        for input_date, expected in timezone_test_cases:
            assert get_date(input_date) == expected

    def test_microseconds_precision(self, microseconds_test_cases) -> None:
        """Проверка обработки разной точности микросекунд."""
        for input_date, expected in microseconds_test_cases:
            assert get_date(input_date) == expected

    def test_whitespace_handling(self) -> None:
        """Проверка обработки пробелов в строке."""
        with pytest.raises(ValueError, match="не соответствует формату ISO"):
            get_date(" 2024-03-11T02:26:18")

        with pytest.raises(ValueError, match="не соответствует формату ISO"):
            get_date("2024-03-11T02:26:18 ")

        with pytest.raises(ValueError, match="не соответствует формату ISO"):
            get_date("2024-03-11 T02:26:18")


if __name__ == "__main__":
    pytest.main(["-v", __file__])