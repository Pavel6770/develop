import pytest
from typing import Any
from unittest.mock import Mock
from datetime import datetime

from src.widget import mask_account_card, get_date


# Заглушки для функций маскировки для использования в тестах
def mock_get_mask_account(account_number: str) -> str:
    """Заглушка для функции маскировки счета."""
    return f"**{account_number[-4:]}"


def mock_get_mask_card_number(card_number: str) -> str:
    """Заглушка для функции маскировки карты."""
    # Удаляем пробелы из номера для корректной маскировки
    clean_number = card_number.replace(" ", "")
    if len(clean_number) == 16:
        return f"{clean_number[:4]} {clean_number[4:6]}** **** {clean_number[-4:]}"
    return f"Ошибка: {card_number}"


class TestMaskAccountCard:
    """Класс с тестами для функции маскировки номера карты или счета."""

    # Тесты для проверки корректного распознавания типа (карта или счет)
    @pytest.mark.parametrize(
        "input_info,expected_output",
        [
            # Счета
            ("Счет 73654108430135874305", "Счет **4305"),
            ("Счет 12345678901234567890", "Счет **7890"),
            ("Счет 1000200030004000", "Счет **4000"),
            # Карты
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
        expected_output: str
    ) -> None:
        """Тест корректного распознавания типа (карта или счет)."""
        result = mask_account_card(
            input_info,
            mock_get_mask_account,
            mock_get_mask_card_number
        )
        assert result == expected_output

    # Параметризованные тесты с разными типами карт и счетов
    @pytest.mark.parametrize(
        "input_info,expected_output",
        [
            # Различные типы карт
            ("Visa 1234567890123456", "Visa 1234 56** **** 3456"),
            ("MasterCard 9876543210987654", "MasterCard 9876 54** **** 7654"),
            ("Maestro 5555666677778888", "Maestro 5555 66** **** 8888"),
            ("МИР 1111222233334444", "МИР 1111 22** **** 4444"),
            ("UnionPay 1234123412341234", "UnionPay 1234 12** **** 1234"),
            ("JCB 4321432143214321", "JCB 4321 43** **** 4321"),
            # Карты с составными названиями
            ("Visa Gold 7000792289606361", "Visa Gold 7000 79** **** 6361"),
            (
                "MasterCard Black Edition 1234567890123456",
                "MasterCard Black Edition 1234 56** **** 3456"
            ),
            (
                "American Express Platinum 1111222233334444",
                "American Express Platinum 1111 22** **** 4444"
            ),
            # Различные счета
            ("Счет 12345", "Счет **2345"),
            ("Счет 123456", "Счет **3456"),
            ("Счет 1234567", "Счет **4567"),
            ("Счет 12345678", "Счет **5678"),
            ("Счет 123456789", "Счет **6789"),
            ("Счет 1234567890", "Счет **7890"),
            # Счета с ведущими нулями
            ("Счет 001234567890", "Счет **7890"),
            ("Счет 000012345678", "Счет **5678"),
            # Карты с пробелами в номере
            ("Visa 7000 7922 8960 6361", "Visa 7000 79** **** 6361"),
            ("MasterCard 1234 5678 9012 3456", "MasterCard 1234 56** **** 3456"),
        ],
    )
    def test_various_card_and_account_types(
        self,
        input_info: str,
        expected_output: str
    ) -> None:
        """Параметризованные тесты с разными типами карт и счетов."""
        result = mask_account_card(
            input_info,
            mock_get_mask_account,
            mock_get_mask_card_number
        )
        assert result == expected_output

    # Тестирование обработки некорректных входных данных
    @pytest.mark.parametrize(
        "input_info,expected_exception,expected_message",
        [
            # Пустые строки
            ("", IndexError, "Передана пустая строка"),
            ("   ", IndexError, "Передана пустая строка"),
            # Строки без номера
            ("Счет", IndexError, "Не указан номер счета"),
            ("Visa", IndexError, "Не указан номер карты"),
            ("MasterCard Platinum", IndexError, "Не указан номер карты"),
            # Неполные данные
            ("Счет ", IndexError, "Не указан номер счета"),
            ("Visa ", IndexError, "Не указан номер карты"),
            # Строки с некорректными разделителями
            ("Счет-73654108430135874305", IndexError, "Не указан номер счета"),
            ("Visa-Platinum-7000792289606361", IndexError, "Не указан номер карты"),
        ],
    )
    def test_invalid_input_handling(
        self,
        input_info: str,
        expected_exception: Any,
        expected_message: str
    ) -> None:
        """Тестирование обработки некорректных входных данных."""
        with pytest.raises(expected_exception, match=expected_message):
            mask_account_card(
                input_info,
                mock_get_mask_account,
                mock_get_mask_card_number
            )

    # Тесты с моками для проверки вызова правильных функций
    def test_correct_function_calls_for_card(self) -> None:
        """Проверка вызова правильной функции для карты."""
        mock_card = Mock(return_value="mocked_card")
        mock_account = Mock(return_value="mocked_account")

        result = mask_account_card(
            "Visa Platinum 7000792289606361",
            mock_account,
            mock_card
        )

        # Проверяем, что вызвалась функция для карты, а не для счета
        mock_card.assert_called_once_with("7000792289606361")
        mock_account.assert_not_called()
        assert result == "Visa Platinum mocked_card"

    def test_correct_function_calls_for_account(self) -> None:
        """Проверка вызова правильной функции для счета."""
        mock_card = Mock(return_value="mocked_card")
        mock_account = Mock(return_value="mocked_account")

        result = mask_account_card(
            "Счет 73654108430135874305",
            mock_account,
            mock_card
        )

        # Проверяем, что вызвалась функция для счета, а не для карты
        mock_account.assert_called_once_with("73654108430135874305")
        mock_card.assert_not_called()
        assert result == "Счет mocked_account"

    # Тесты для проверки обработки различных форматов номеров
    @pytest.mark.parametrize(
        "input_info,expected_card_call,expected_account_call",
        [
            ("Visa 7000792289606361", "7000792289606361", None),
            ("MasterCard 1234 5678 9012 3456", "1234 5678 9012 3456", None),
            ("Счет 73654108430135874305", None, "73654108430135874305"),
            ("Счет 1234 5678 9012 3456 7890", None, "1234 5678 9012 3456 7890"),
        ],
    )
    def test_number_format_preservation(
        self,
        input_info: str,
        expected_card_call: str | None,
        expected_account_call: str | None
    ) -> None:
        """Проверка передачи номера в исходном формате в функции маскировки."""
        mock_card = Mock(return_value="mocked_card")
        mock_account = Mock(return_value="mocked_account")

        mask_account_card(input_info, mock_account, mock_card)

        if expected_card_call:
            mock_card.assert_called_once_with(expected_card_call)
            mock_account.assert_not_called()
        if expected_account_call:
            mock_account.assert_called_once_with(expected_account_call)
            mock_card.assert_not_called()

    # Тест с реальными функциями маскировки
    def test_with_real_mask_functions(self) -> None:
        """Тест с реальными функциями маскировки."""
        # Создаем реальные функции для теста
        def real_mask_account(num: str) -> str:
            return f"**{num[-4:]}"

        def real_mask_card(num: str) -> str:
            clean_num = num.replace(" ", "")
            if len(clean_num) == 16:
                return f"{clean_num[:4]} {clean_num[4:6]}** **** {clean_num[-4:]}"
            return "Invalid card"

        test_cases = [
            ("Visa Platinum 7000792289606361", "Visa Platinum 7000 79** **** 6361"),
            ("Счет 73654108430135874305", "Счет **4305"),
            ("Maestro 1234567890123456", "Maestro 1234 56** **** 3456"),
        ]

        for input_info, expected in test_cases:
            result = mask_account_card(input_info, real_mask_account, real_mask_card)
            assert result == expected

    # Тест на устойчивость к ошибкам в функциях маскировки
    def test_error_handling_from_mask_functions(self) -> None:
        """Проверка обработки ошибок из функций маскировки."""
        def error_mask_function(num: str) -> str:
            return f"Error: {num}"

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
    @pytest.mark.parametrize(
        "input_date,expected_output",
        [
            # Стандартные ISO форматы
            ("2024-03-11T02:26:18.671407", "11.03.2024"),
            ("2023-12-31T23:59:59.999999", "31.12.2023"),
            ("2024-01-01T00:00:00.000000", "01.01.2024"),
            # Различные месяцы и дни
            ("2024-02-29T12:00:00.000000", "29.02.2024"),  # Високосный год
            ("2023-02-28T12:00:00.000000", "28.02.2023"),  # Невисокосный год
            ("2024-04-30T12:00:00.000000", "30.04.2024"),
            ("2024-06-01T12:00:00.000000", "01.06.2024"),
            # Различные годы
            ("2000-01-01T00:00:00.000000", "01.01.2000"),
            ("1999-12-31T23:59:59.999999", "31.12.1999"),
            ("2100-12-31T23:59:59.999999", "31.12.2100"),
        ],
    )
    def test_correct_date_conversion(self, input_date: str, expected_output: str) -> None:
        """Тестирование правильности преобразования даты."""
        assert get_date(input_date) == expected_output

    # Проверка работы функции на различных входных форматах
    @pytest.mark.parametrize(
        "input_date,expected_output",
        [
            # ISO форматы без микросекунд
            ("2024-03-11T02:26:18", "11.03.2024"),
            ("2023-12-31T23:59:59", "31.12.2023"),
            # ISO форматы с часовым поясом
            ("2024-03-11T02:26:18+03:00", "11.03.2024"),
            ("2024-03-11T02:26:18-05:00", "11.03.2024"),
            ("2024-03-11T02:26:18+00:00", "11.03.2024"),
            # ISO форматы с Z (UTC)
            ("2024-03-11T02:26:18Z", "11.03.2024"),
            # Только дата в ISO формате
            ("2024-03-11", "11.03.2024"),
            ("2023-12-31", "31.12.2023"),
            # Граничные случаи
            ("0001-01-01T00:00:00", "01.01.0001"),
            ("9999-12-31T23:59:59", "31.12.9999"),
            # Разделители
            ("2024/03/11T02:26:18", "11.03.2024"),
            ("2024.03.11T02:26:18", "11.03.2024"),
        ],
    )
    def test_various_date_formats(self, input_date: str, expected_output: str) -> None:
        """Проверка работы функции на различных входных форматах даты."""
        assert get_date(input_date) == expected_output

    # Проверка обработки некорректных входных данных
    @pytest.mark.parametrize(
        "input_date,expected_exception,expected_message",
        [
            # Пустые строки
            ("", ValueError, "Строка '' не соответствует формату ISO"),
            ("   ", ValueError, "Строка '   ' не соответствует формату ISO"),
            # Неполные даты
            ("2024", ValueError, "Строка '2024' не соответствует формату ISO"),
            ("2024-03", ValueError, "Строка '2024-03' не соответствует формату ISO"),
            ("2024-03-11T", ValueError, "Строка '2024-03-11T' не соответствует формату ISO"),
            # Неправильные разделители
            (
                "2024.03.11 02:26:18",
                ValueError,
                "Строка '2024.03.11 02:26:18' не соответствует формату ISO"
            ),
            (
                "11-03-2024T02:26:18",
                ValueError,
                "Строка '11-03-2024T02:26:18' не соответствует формату ISO"
            ),
            # Несуществующие даты
            (
                "2024-02-30T12:00:00",
                ValueError,
                "Строка '2024-02-30T12:00:00' не соответствует формату ISO"
            ),
            (
                "2024-04-31T12:00:00",
                ValueError,
                "Строка '2024-04-31T12:00:00' не соответствует формату ISO"
            ),
            (
                "2023-02-29T12:00:00",
                ValueError,
                "Строка '2023-02-29T12:00:00' не соответствует формату ISO"
            ),
            # Некорректные символы
            ("abc", ValueError, "Строка 'abc' не соответствует формату ISO"),
            (
                "2024-03-11T02:26:18.671407abc",
                ValueError,
                "Строка '2024-03-11T02:26:18.671407abc' не соответствует формату ISO"
            ),
            # Неправильный формат времени
            (
                "2024-03-11T25:00:00",
                ValueError,
                "Строка '2024-03-11T25:00:00' не соответствует формату ISO"
            ),
            (
                "2024-03-11T02:60:00",
                ValueError,
                "Строка '2024-03-11T02:60:00' не соответствует формату ISO"
            ),
            (
                "2024-03-11T02:26:60",
                ValueError,
                "Строка '2024-03-11T02:26:60' не соответствует формату ISO"
            ),
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

    # Проверка обработки отсутствия даты (нестроковые типы)
    @pytest.mark.parametrize(
        "input_date,expected_exception,expected_message",
        [
            (None, TypeError, "Ожидалась строка, получен NoneType"),
            (123, TypeError, "Ожидалась строка, получен int"),
            (45.67, TypeError, "Ожидалась строка, получен float"),
            ([], TypeError, "Ожидалась строка, получен list"),
            ({}, TypeError, "Ожидалась строка, получен dict"),
            (True, TypeError, "Ожидалась строка, получен bool"),
            (datetime.now(), TypeError, "Ожидалась строка, получен datetime"),
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
        # Минимальная дата
        assert get_date("0001-01-01T00:00:00") == "01.01.0001"

        # Максимальная дата
        assert get_date("9999-12-31T23:59:59") == "31.12.9999"

        # Високосный день
        assert get_date("2020-02-29T12:00:00") == "29.02.2020"

        # Начало года
        assert get_date("2024-01-01T00:00:00") == "01.01.2024"

        # Конец года
        assert get_date("2024-12-31T23:59:59") == "31.12.2024"

    def test_timezone_handling(self) -> None:
        """Проверка обработки разных часовых поясов."""
        # Все эти даты должны давать одинаковый результат (дата не зависит от времени)
        test_cases = [
            ("2024-03-11T00:00:00+00:00", "11.03.2024"),
            ("2024-03-11T23:59:59+03:00", "11.03.2024"),
            ("2024-03-11T02:26:18-05:00", "11.03.2024"),
            ("2024-03-11T12:00:00Z", "11.03.2024"),
        ]

        for input_date, expected in test_cases:
            assert get_date(input_date) == expected

    def test_microseconds_precision(self) -> None:
        """Проверка обработки разной точности микросекунд."""
        test_cases = [
            ("2024-03-11T02:26:18.1", "11.03.2024"),
            ("2024-03-11T02:26:18.12", "11.03.2024"),
            ("2024-03-11T02:26:18.123", "11.03.2024"),
            ("2024-03-11T02:26:18.123456", "11.03.2024"),
            ("2024-03-11T02:26:18.123456789", "11.03.2024"),
        ]

        for input_date, expected in test_cases:
            assert get_date(input_date) == expected

    def test_whitespace_handling(self) -> None:
        """Проверка обработки пробелов в строке."""
        # Пробелы в начале или конце не допускаются ISO форматом
        with pytest.raises(ValueError, match="не соответствует формату ISO"):
            get_date(" 2024-03-11T02:26:18")

        with pytest.raises(ValueError, match="не соответствует формату ISO"):
            get_date("2024-03-11T02:26:18 ")

        # Пробелы внутри строки тоже недопустимы
        with pytest.raises(ValueError, match="не соответствует формату ISO"):
            get_date("2024-03-11 T02:26:18")


if __name__ == "__main__":
    pytest.main(["-v", __file__])