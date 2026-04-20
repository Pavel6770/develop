import requests
from typing import Dict, Any, Optional

# API ключ для внешнего сервиса
API_KEY = "ZTbjgKuTjQ2A245ZEMu3MMHiaygy2UMc"
API_URL = "https://marketplace.apilayer.com/account"  # Пример API (можно заменить)


def convert_to_rub(transaction: Dict[str, Any]) -> float:
    """
    Конвертирует сумму транзакции в рубли.
    """
    amount = transaction.get('amount', 0.0)
    currency = transaction.get('currency', 'RUB').upper()

    # Обработка строковых значений amount
    if isinstance(amount, str):
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            amount = 0.0

    # Если сумма в рублях или валюта не указана
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