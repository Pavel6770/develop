import sys
sys.path.insert(0, '.')

import pytest
from unittest.mock import patch, MagicMock
import requests


from src.external_api import convert_to_rub, get_exchange_rate, get_fallback_rate


class TestConvertToRub:
    """Тесты для функции convert_to_rub"""

    @pytest.mark.parametrize("transaction,expected", [
        ({"amount": 1000, "currency": "RUB"}, 1000.0),
        ({"amount": 500.50, "currency": "RUB"}, 500.5),
        ({"amount": 0, "currency": "RUB"}, 0.0),
        ({"amount": 10000, "currency": "rub"}, 10000.0),
        ({"amount": 750, "currency": "RuB"}, 750.0),
        ({"amount": 123.45, "currency": "RUB", "extra": "field"}, 123.45),
    ])
    def test_convert_rub_transaction_returns_same_amount(self, transaction, expected):
        """Тест рублевых транзакций"""
        result = convert_to_rub(transaction)
        assert isinstance(result, float)
        assert result == expected

    @patch('currency_converter.get_exchange_rate')
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
        mock_get_rate.return_value = rate
        transaction = {"amount": usd_amount, "currency": "USD"}

        result = convert_to_rub(transaction)

        assert isinstance(result, float)
        assert result == expected
        mock_get_rate.assert_called_once_with("USD")

    @patch('currency_converter.get_exchange_rate')
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
        mock_get_rate.return_value = None
        transaction = {"amount": amount, "currency": currency}

        result = convert_to_rub(transaction)

        assert isinstance(result, float)
        assert result == 0.0
        mock_get_rate.assert_called_once_with(currency)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])



class TestGetExchangeRate:
    """Тесты для функции get_exchange_rate"""

    @patch('currency_converter.requests.get')
    @pytest.mark.parametrize("currency,expected_rate", [
        ("USD", 92.50),
        ("EUR", 100.20),
        ("USD", 91.75),
        ("EUR", 99.80),
    ])
    def test_successful_api_response_returns_correct_rate(
        self, mock_get, currency, expected_rate
    ):
        """
        Тест 1: Параметризованный тест успешных ответов API
        Проверяет корректную обработку различных курсов валют
        """
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": expected_rate
        }
        mock_get.return_value = mock_response

        # Act
        result = get_exchange_rate(currency)

        # Assert
        assert result is not None
        assert isinstance(result, float)
        assert result == expected_rate
        mock_get.assert_called_once()

    @patch('currency_converter.requests.get')
    @pytest.mark.parametrize("exception", [
        requests.RequestException("Network error"),
        requests.Timeout("Request timed out"),
        requests.ConnectionError("Failed to connect"),
        Exception("Unexpected error"),
    ])
    def test_request_exception_returns_fallback_rate(self, mock_get, exception):
        """
        Тест 2: Проверяет обработку различных исключений при запросе к API
        """
        # Arrange
        mock_get.side_effect = exception

        # Act
        result = get_exchange_rate("USD")

        # Assert
        assert result is not None
        assert isinstance(result, float)
        assert result > 0  # Резервный курс должен быть положительным
        mock_get.assert_called_once()

    @patch('currency_converter.requests.get')
    @pytest.mark.parametrize("status_code", [
        400,  # Bad Request
        401,  # Unauthorized
        403,  # Forbidden
        404,  # Not Found
        500,  # Internal Server Error
        502,  # Bad Gateway
        503,  # Service Unavailable
    ])
    def test_api_error_status_codes_use_fallback(self, mock_get, status_code):
        """
        Тест 3: Проверяет обработку различных ошибочных статус-кодов HTTP
        """
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"error": "API Error"}
        mock_get.return_value = mock_response

        # Act
        result = get_exchange_rate("EUR")

        # Assert
        assert result is not None
        assert isinstance(result, float)
        assert result > 0
        mock_get.assert_called_once()

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

    @pytest.mark.parametrize("currency,expected_rate", [
        ("USD", 92.50),
        ("usd", 92.50),  # Проверка нижнего регистра
        ("Usd", 92.50),  # Проверка смешанного регистра
        ("EUR", 100.20),
        ("eur", 100.20),  # Проверка нижнего регистра
        ("Eur", 100.20),  # Проверка смешанного регистра
    ])
    def test_get_fallback_rate_for_supported_currencies(self, currency, expected_rate):
        """
        Тест 1: Параметризованный тест для поддерживаемых валют
        Проверяет корректность резервных курсов для USD и EUR
        с учетом разных регистров
        """
        # Act
        result = get_fallback_rate(currency)

        # Assert
        assert result is not None
        assert isinstance(result, float)
        assert result == expected_rate

    @pytest.mark.parametrize("unsupported_currency", [
        "GBP", "gbp", "JPY", "CNY", "CHF", "CAD", "AUD", "NZD",
        "RUB", "rub", "", "   ", "123", None, "USDEUR"
    ])
    def test_get_fallback_rate_for_unsupported_currencies_returns_none(self, unsupported_currency):
        """
        Тест 2: Параметризованный тест для неподдерживаемых валют
        Проверяет, что функция возвращает None для валют,
        отсутствующих в словаре fallback_rates
        """
        # Act
        result = get_fallback_rate(unsupported_currency)

        # Assert
        assert result is None

    def test_get_fallback_rate_returns_float_type(self):
        """
        Тест 3: Проверяет, что для поддерживаемых валют возвращается
        значение типа float, а не int
        """
        # Act
        usd_result = get_fallback_rate("USD")
        eur_result = get_fallback_rate("EUR")

        # Assert
        assert isinstance(usd_result, float)
        assert isinstance(eur_result, float)
        # Проверка, что значения не являются целыми числами
        assert usd_result == 92.50
        assert eur_result == 100.20


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])


