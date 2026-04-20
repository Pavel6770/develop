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

    def test_get_fallback_rate_for_usd_returns_correct_rate(self):
        """Тест fallback курса для USD"""
        result = get_fallback_rate("USD")
        assert result == 92.50
        assert isinstance(result, float)

    def test_get_fallback_rate_for_eur_returns_correct_rate(self):
        """Тест fallback курса для EUR"""
        result = get_fallback_rate("EUR")
        assert result == 100.20
        assert isinstance(result, float)

    def test_get_fallback_rate_for_unsupported_currency_returns_none(self):
        """Тест для неподдерживаемой валюты"""
        result = get_fallback_rate("GBP")
        assert result is None

    # ИСПРАВЛЕННЫЙ ТЕСТ - используем parametrize вместо subTest
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
        """
        Тест 5: Проверяет обработку валют со спецсимволами
        """
        # Act
        result = get_fallback_rate(special_currency)

        # Assert
        assert result is None

    @pytest.mark.parametrize("whitespace_currency", [
        " USD",
        "USD ",
        " USD ",
        "\tUSD",
        "USD\t",
        "\tUSD\t",
        "  USD  ",
        "\nUSD",
        "USD\n",
    ])
    def test_get_fallback_rate_with_whitespace_returns_none(self, whitespace_currency):
        """Тест обработки строк с пробелами"""
        # Act
        result = get_fallback_rate(whitespace_currency)

        # Assert
        assert result is None

    @pytest.mark.parametrize("numeric_currency", [
        "123",
        "456.78",
        "0",
        "-100",
        "1.5",
        "USD123",
        "123USD",
    ])
    def test_get_fallback_rate_with_numeric_string_returns_none(self, numeric_currency):
        """Тест обработки строк, содержащих числа"""
        # Act
        result = get_fallback_rate(numeric_currency)

        # Assert
        assert result is None

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
    def test_get_fallback_rate_with_unicode_characters_returns_none(self, unicode_currency):
        """Тест обработки строк с unicode символами"""
        # Act
        result = get_fallback_rate(unicode_currency)

        # Assert
        assert result is None

    @pytest.mark.parametrize("invalid_length", [
        "U",
        "US",
        "USDE",
        "USDEUR",
        "EURO",
        "DOLLAR",
    ])
    def test_get_fallback_rate_with_invalid_length_returns_none(self, invalid_length):
        """Тест с некорректной длиной кода валюты"""
        # Act
        result = get_fallback_rate(invalid_length)

        # Assert
        assert result is None

    @pytest.mark.parametrize("non_string", [
        123,
        45.67,
        True,
        False,
        ["USD"],
        {"USD": 92.50},
        (1, 2, 3),
        {1, 2, 3},
    ])
    def test_get_fallback_rate_with_non_string_returns_none(self, non_string):
        """Тест с нестроковыми типами данных"""
        # Act
        result = get_fallback_rate(non_string)

        # Assert
        assert result is None

    def test_get_fallback_rate_case_insensitive(self):
        """Тест регистронезависимости"""
        # Проверяем разные варианты написания USD
        assert get_fallback_rate("usd") == 92.50
        assert get_fallback_rate("Usd") == 92.50
        assert get_fallback_rate("uSd") == 92.50
        assert get_fallback_rate("USD") == 92.50

        # Проверяем разные варианты написания EUR
        assert get_fallback_rate("eur") == 100.20
        assert get_fallback_rate("Eur") == 100.20
        assert get_fallback_rate("eUr") == 100.20
        assert get_fallback_rate("EUR") == 100.20

    def test_get_fallback_rate_positive_values(self):
        """Проверка положительных значений"""
        assert get_fallback_rate("USD") > 0
        assert get_fallback_rate("EUR") > 0
        assert get_fallback_rate("USD") < 1000
        assert get_fallback_rate("EUR") < 1000

    def test_get_fallback_rate_returns_same_value_multiple_calls(self):
        """Проверка что функция возвращает одинаковое значение при многократных вызовах"""
        first_call = get_fallback_rate("USD")
        second_call = get_fallback_rate("USD")
        third_call = get_fallback_rate("USD")

        assert first_call == second_call == third_call == 92.50

    def test_get_fallback_rate_eur_higher_than_usd(self):
        """Проверка что курс EUR выше курса USD"""
        usd_rate = get_fallback_rate("USD")
        eur_rate = get_fallback_rate("EUR")

        assert eur_rate > usd_rate

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


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])


