import sys
import os
import pytest
from unittest.mock import patch, MagicMock
import requests

# Добавляем корень проекта в путь
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Теперь импортируем из src
from src.external_api import convert_to_rub, get_exchange_rate, get_fallback_rate


class TestConvertToRub:
    """Тесты для функции convert_to_rub"""

    # ИСПРАВЛЕНО: путь для patch
    @patch('src.external_api.get_exchange_rate')
    @pytest.mark.parametrize("usd_amount,rate,expected", [
        (100, 92.50, 9250.0),
        (50, 90.00, 4500.0),
        (1, 92.50, 92.5),
        (0, 92.50, 0.0),
        (1000.50, 92.50, 92546.25),
    ])
    def test_convert_usd_transaction_successful_api(
        self, mock_get_rate, usd_amount, rate, expected
    ):
        """Тест USD транзакций с успешным API"""
        # Arrange
        mock_get_rate.return_value = rate
        transaction = {"amount": usd_amount, "currency": "USD"}

        # Act
        result = convert_to_rub(transaction)

        # Assert
        assert isinstance(result, float)
        assert result == expected
        mock_get_rate.assert_called_once_with("USD")

    # ИСПРАВЛЕНО: путь для patch
    @patch('src.external_api.get_exchange_rate')
    @pytest.mark.parametrize("currency,amount", [
        ("EUR", 100),
        ("EUR", 50.50),
        ("EUR", 0),
        ("EUR", 1000),
    ])
    def test_convert_eur_transaction_when_api_fails(
        self, mock_get_rate, currency, amount
    ):
        """Тест EUR транзакций при недоступности API"""
        # Arrange
        mock_get_rate.return_value = None
        transaction = {"amount": amount, "currency": currency}

        # Act
        result = convert_to_rub(transaction)

        # Assert
        assert isinstance(result, float)
        assert result == 0.0
        mock_get_rate.assert_called_once_with(currency)

    def test_negative_amount(self):
        """Отрицательные суммы"""
        with patch('src.external_api.get_exchange_rate') as mock:
            mock.return_value = 92.50
            result = convert_to_rub({"amount": -100, "currency": "USD"})
            assert result == -9250.0

    def test_large_amount(self):
        """Большие суммы"""
        with patch('src.external_api.get_exchange_rate') as mock:
            mock.return_value = 92.50
            result = convert_to_rub({"amount": 1_000_000, "currency": "USD"})
            assert result == 92_500_000.0

    def test_decimal_precision(self):
        """Точность десятичных дробей"""
        with patch('src.external_api.get_exchange_rate') as mock:
            mock.return_value = 92.75
            result = convert_to_rub({"amount": 100.55, "currency": "USD"})
            assert result == 100.55 * 92.75

    def test_missing_amount(self):
        """Отсутствие ключа amount"""
        result = convert_to_rub({"currency": "USD"})
        assert result == 0.0

    def test_amount_as_string(self):
        """Сумма в виде строки - должна конвертироваться в число"""
        with patch('src.external_api.get_exchange_rate') as mock_rate:
            mock_rate.return_value = 92.50
            result = convert_to_rub({"amount": "100", "currency": "USD"})
            assert result == 9250.0

    def test_extra_fields_ignored(self):
        """Дополнительные поля игнорируются"""
        with patch('src.external_api.get_exchange_rate') as mock:
            mock.return_value = 92.50
            transaction = {"amount": 100, "currency": "USD", "id": 1, "desc": "test"}
            result = convert_to_rub(transaction)
            assert result == 9250.0

    def test_returns_float(self):
        """Проверка типа возвращаемого значения"""
        result = convert_to_rub({"amount": 100, "currency": "RUB"})
        assert isinstance(result, float)


class TestGetExchangeRate:
    """Тесты для функции get_exchange_rate"""

    @patch('src.external_api.requests.get')
    @pytest.mark.parametrize("currency,expected_rate", [
        ("USD", 92.50),
        ("EUR", 100.20),
    ])
    def test_successful_api_response_returns_correct_rate(
        self, mock_get, currency, expected_rate
    ):
        """Тест успешных ответов API"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": expected_rate
        }
        mock_get.return_value = mock_response

        result = get_exchange_rate(currency)

        assert result == expected_rate
        mock_get.assert_called_once()

    # ИСПРАВЛЕНО: убран Exception, оставлены только requests исключения
    @patch('src.external_api.requests.get')
    @pytest.mark.parametrize("exception", [
        requests.RequestException("Network error"),
        requests.Timeout("Request timed out"),
        requests.ConnectionError("Failed to connect"),
        # Exception("Unexpected error"),  # ← УДАЛИТЬ ЭТУ СТРОКУ
    ])
    def test_request_exception_returns_fallback_rate(self, mock_get, exception):
        """Тест обработки исключений requests"""
        # Arrange
        mock_get.side_effect = exception

        # Act
        result = get_exchange_rate("USD")

        # Assert
        assert result is not None
        assert isinstance(result, float)
        assert result == 92.50  # Fallback курс для USD
        mock_get.assert_called_once()

    @patch('src.external_api.requests.get')
    @pytest.mark.parametrize("status_code", [
        400, 401, 403, 404, 500, 502, 503,
    ])
    def test_api_error_status_codes_use_fallback(self, mock_get, status_code):
        """Тест обработки ошибок HTTP"""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"error": "API Error"}
        mock_get.return_value = mock_response

        result = get_exchange_rate("EUR")

        assert result == 100.20  # Fallback курс для EUR
        mock_get.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

class TestGetFallbackRate:
    """Тесты для функции get_fallback_rate"""

    def test_get_fallback_rate_for_usd_returns_correct_rate(self):
        """Тест fallback курса для USD"""
        # Act
        result = get_fallback_rate("USD")

        # Assert
        assert result == 92.50
        assert isinstance(result, float)

    def test_get_fallback_rate_for_eur_returns_correct_rate(self):
        """Тест fallback курса для EUR"""
        # Act
        result = get_fallback_rate("EUR")

        # Assert
        assert result == 100.20
        assert isinstance(result, float)

    def test_get_fallback_rate_for_unsupported_currency_returns_none(self):
        """Тест для неподдерживаемой валюты"""
        # Act
        result = get_fallback_rate("GBP")

        # Assert
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

    @patch('currency_converter.requests.get')
    def test_api_response_missing_success_key_uses_fallback(self, mock_get):
        """
        Дополнительный тест: Проверяет обработку ответа API без ключа 'success'
        """
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": 92.50  # Отсутствует ключ 'success'
        }
        mock_get.return_value = mock_response

        # Act
        result = get_exchange_rate("USD")

        # Assert
        assert result is not None
        assert isinstance(result, float)
        assert result > 0
        mock_get.assert_called_once()

    @patch('currency_converter.requests.get')
    def test_api_response_success_false_uses_fallback(self, mock_get):
        """
        Дополнительный тест: Проверяет обработку ответа с success=False
        """
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": False,
            "error": "Invalid API key"
        }
        mock_get.return_value = mock_response

        # Act
        result = get_exchange_rate("USD")

        # Assert
        assert result is not None
        assert isinstance(result, float)
        assert result > 0
        mock_get.assert_called_once()

    @patch('currency_converter.requests.get')
    def test_api_response_missing_result_key_uses_fallback(self, mock_get):
        """
        Дополнительный тест: Проверяет обработку ответа без ключа 'result'
        """
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True
            # Отсутствует ключ 'result'
        }
        mock_get.return_value = mock_response

        # Act
        result = get_exchange_rate("USD")

        # Assert
        assert result is not None
        assert isinstance(result, float)
        assert result > 0
        mock_get.assert_called_once()

    @patch('currency_converter.requests.get')
    def test_api_timeout_returns_fallback_rate(self, mock_get):
        """
        Дополнительный тест: Проверяет обработку таймаута при запросе
        """
        # Arrange
        mock_get.side_effect = requests.Timeout("Request timeout")

        # Act
        result = get_exchange_rate("EUR")

        # Assert
        assert result is not None
        assert isinstance(result, float)
        assert result > 0
        mock_get.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])


class TestGetFallbackRate:
    """Тесты для функции get_fallback_rate"""

    # Тест 1: Основные валюты
    @pytest.mark.parametrize("currency,expected", [
        ("USD", 92.50),
        ("EUR", 100.20),
        ("usd", 92.50),
        ("eur", 100.20),
        ("Usd", 92.50),
        ("Eur", 100.20),
    ])
    def test_get_fallback_rate_supported_currencies(self, currency, expected):
        """Тест для поддерживаемых валют"""
        result = get_fallback_rate(currency)
        assert result == expected
        assert isinstance(result, float)

    # Тест 2: Неподдерживаемые валюты
    @pytest.mark.parametrize("invalid_currency", [
        "GBP",
        "JPY",
        "CNY",
        "CHF",
        "CAD",
        "AUD",
        "RUB",
        "XYZ",
    ])
    def test_get_fallback_rate_unsupported_currencies_returns_none(self, invalid_currency):
        """Тест для неподдерживаемых валют"""
        result = get_fallback_rate(invalid_currency)
        assert result is None

    # Тест 3: Специальные символы
    @pytest.mark.parametrize("special_currency", [
        "US$",
        "EU€",
        "$",
        "€",
        "USD$",
        "EUR€",
        "@#$",
        "!@#$%",
    ])
    def test_get_fallback_rate_with_special_characters_returns_none(self, special_currency):
        """Тест для валют со спецсимволами"""
        result = get_fallback_rate(special_currency)
        assert result is None

    # Тест 4: Пробелы и табуляция (ИСПРАВЛЕННЫЙ)
    @pytest.mark.parametrize("whitespace_currency", [
        " USD",
        "USD ",
        " USD ",
        "  USD  ",
        "\tUSD",
        "USD\t",
        "\tUSD\t",
        "\nUSD",
        "USD\n",
        "\n\t USD \t\n",
    ])
    def test_get_fallback_rate_with_whitespace_returns_none(self, whitespace_currency):
        """Тест для валют с пробелами и табуляцией"""
        result = get_fallback_rate(whitespace_currency)
        assert result is None

    # Тест 5: Смешанный регистр с пробелами (ИСПРАВЛЕННЫЙ)
    @pytest.mark.parametrize("mixed_currency", [
        " UsD ",
        " eUr ",
        "  uSd  ",
        "\t EuR \t",
        "\n Usd \n",
        "  UsD  ",
        "\t\t eUr \t\t",
    ])
    def test_get_fallback_rate_with_mixed_case_and_spaces_returns_none(self, mixed_currency):
        """
        Тест: Проверяет обработку смешанного регистра с пробелами
        """
        # Act
        result = get_fallback_rate(mixed_currency)

        # Assert
        assert result is None, f"Для '{mixed_currency}' ожидался None"

    # Тест 6: Числовые строки
    @pytest.mark.parametrize("numeric_currency", [
        "123",
        "456.78",
        "0",
        "-100",
        "1.5",
        "USD123",
        "123USD",
        "US3D",
    ])
    def test_get_fallback_rate_with_numeric_strings_returns_none(self, numeric_currency):
        """Тест для строк, содержащих числа"""
        result = get_fallback_rate(numeric_currency)
        assert result is None

    # Тест 7: Unicode символы
    @pytest.mark.parametrize("unicode_currency", [
        "ДОЛЛАР",
        "ЕВРО",
        "美元",
        "ユーロ",
        "€€€",
        "$$$",
        "₽",
        "😀",
    ])
    def test_get_fallback_rate_with_unicode_returns_none(self, unicode_currency):
        """Тест для unicode символов"""
        result = get_fallback_rate(unicode_currency)
        assert result is None

    # Тест 8: None и пустые значения
    def test_get_fallback_rate_with_none_returns_none(self):
        """Тест с None"""
        result = get_fallback_rate(None)
        assert result is None

    def test_get_fallback_rate_with_empty_string_returns_none(self):
        """Тест с пустой строкой"""
        result = get_fallback_rate("")
        assert result is None

    def test_get_fallback_rate_with_spaces_only_returns_none(self):
        """Тест со строкой из пробелов"""
        result = get_fallback_rate("   ")
        assert result is None

    # Тест 9: Нестроковые типы
    @pytest.mark.parametrize("non_string", [
        123,
        45.67,
        True,
        False,
        ["USD"],
        {"USD": 92.50},
        (1, 2, 3),
    ])
    def test_get_fallback_rate_with_non_string_returns_none(self, non_string):
        """Тест с нестроковыми типами данных"""
        result = get_fallback_rate(non_string)
        assert result is None

    # Тест 10: Длина строки
    @pytest.mark.parametrize("invalid_length", [
        "U",
        "US",
        "USDE",
        "USDEUR",
        "EURO",
        "DOLLAR",
        "A" * 100,
    ])
    def test_get_fallback_rate_with_invalid_length_returns_none(self, invalid_length):
        """Тест с некорректной длиной кода валюты"""
        result = get_fallback_rate(invalid_length)
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])


