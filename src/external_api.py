import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# API ключ для внешнего сервиса
API_KEY = "ZTbjgKuTjQ2A245ZEMu3MMHiaygy2UMc"
API_URL = "https://marketplace.apilayer.com/account"  # Пример API (можно заменить)

# Загружаем переменные окружения из .env файла
load_dotenv()


def get_exchange_rate(currency: str) -> Optional[float]:
    """
    Получает текущий курс валюты к рублю через внешнее API.
    """
    if not API_KEY:
        print("API ключ не найден в .env файле")
        return get_fallback_rate(currency)

    try:
        headers = {"apikey": API_KEY}
        params = {
            "from": currency,
            "to": "RUB",
            "amount": 1
        }

        response = requests.get(API_URL, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return float(data.get('result', 0))

        return get_fallback_rate(currency)

    except requests.RequestException as e:
        print(f"Ошибка при обращении к API: {e}")
        return get_fallback_rate(currency)


def get_fallback_rate(currency: str) -> Optional[float]:
    """
    Возвращает запасной курс валюты на случай недоступности API.
    """
    if not currency or not isinstance(currency, str):
        return None

    fallback_rates = {
        'USD': 92.50,
        'EUR': 100.20
    }
    return fallback_rates.get(currency.upper())


def convert_to_rub(transaction: Dict[str, Any]) -> float:
    """
    Конвертирует сумму транзакции в рубли.

    Поддерживает два формата:
    1. Прямой: {"amount": 100, "currency": "USD"}
    2. Вложенный: {"operationAmount": {"amount": 100, "currency": {"code": "USD"}}}
    """
    # Извлекаем сумму и валюту из разных форматов
    amount = 0.0
    currency = 'RUB'

    # Проверяем, есть ли вложенная структура operationAmount
    if 'operationAmount' in transaction:
        operation_amount = transaction['operationAmount']

        # Извлекаем сумму
        if isinstance(operation_amount, dict):
            amount = operation_amount.get('amount', 0.0)

            # Извлекаем валюту из вложенной структуры currency.code
            if 'currency' in operation_amount:
                currency_obj = operation_amount['currency']
                if isinstance(currency_obj, dict):
                    currency = currency_obj.get('code', 'RUB')
                else:
                    currency = str(currency_obj)
            else:
                currency = 'RUB'
    else:
        # Прямой формат
        amount = transaction.get('amount', 0.0)
        currency = transaction.get('currency', 'RUB')

    # Приводим валюту к верхнему регистру
    currency = str(currency).upper() if currency else 'RUB'

    # Обработка строковых значений amount
    if isinstance(amount, str):
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            amount = 0.0
    elif not isinstance(amount, (int, float)):
        amount = 0.0

    # Если сумма в рублях
    if currency == 'RUB':
        return float(amount)

    # Конвертация для USD и EUR
    if currency in ['USD', 'EUR']:
        rate = get_exchange_rate(currency)
        if rate is not None:
            return float(amount * rate)
        else:
            print(f"Не удалось получить курс для {currency}")
            return 0.0

    # Для других валют
    print(f"Валюта {currency} не поддерживается для конвертации")
    return 0.0


def get_exchange_rate(currency: str) -> Optional[float]:
    """
    Получает текущий курс валюты к рублю через внешнее API.

    Args:
        currency (str): Код валюты (USD или EUR)

    Returns:
        Optional[float]: Курс валюты к рублю или None при ошибке
    """
    try:
        # Вариант 1: Использование API apilayer.com (требуется регистрация)
        headers = {
            "apikey": API_KEY
        }
        params = {
            "from": currency,
            "to": "RUB",
            "amount": 1
        }

        response = requests.get(API_URL, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return float(data.get('result', 0))

        # Если API недоступен, используем fallback курс
        return get_fallback_rate(currency)

    except requests.RequestException as e:
        print(f"Ошибка при обращении к API: {e}")
        return get_fallback_rate(currency)


def get_fallback_rate(currency: str) -> Optional[float]:
    """
    Возвращает запасной курс валюты на случай недоступности API.

    Args:
        currency (str): Код валюты

    Returns:
        Optional[float]: Курс валюты
    """
    # Добавить проверку на None и пустые строки
    if not currency or not isinstance(currency, str):
        return None

    fallback_rates = {
        'USD': 92.50,
        'EUR': 100.20
    }
    return fallback_rates.get(currency.upper())