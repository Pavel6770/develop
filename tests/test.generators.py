import pytest
from typing import List, Dict, Any
from collections.abc import Generator

# Импортируем тестируемую функцию
from src.generators import filter_by_currency, transaction_descriptions, card_number_generator


class TestFilterByCurrency:
    """Тесты для функции filter_by_currency."""

    @pytest.fixture
    def sample_transactions(self) -> List[Dict[str, Any]]:
        """Фикстура с образцами транзакций для тестирования."""
        return [
            {
                "id": 939719570,
                "state": "EXECUTED",
                "date": "2018-06-30T02:08:58.425572",
                "operationAmount": {
                    "amount": "9824.07",
                    "currency": {
                        "name": "USD",
                        "code": "USD"
                    }
                },
                "description": "Перевод организации",
                "from": "Счет 75106830613657916952",
                "to": "Счет 11776614605963066702"
            },
            {
                "id": 142264268,
                "state": "EXECUTED",
                "date": "2019-04-04T23:20:05.206878",
                "operationAmount": {
                    "amount": "79114.93",
                    "currency": {
                        "name": "USD",
                        "code": "USD"
                    }
                },
                "description": "Перевод со счета на счет",
                "from": "Счет 19708645243227258542",
                "to": "Счет 75651667383060284188"
            },
            {
                "id": 895315941,
                "state": "EXECUTED",
                "date": "2018-08-19T04:27:37.904916",
                "operationAmount": {
                    "amount": "5683.33",
                    "currency": {
                        "name": "RUB",
                        "code": "RUB"
                    }
                },
                "description": "Перевод с карты на карту",
                "from": "Visa Classic 6831982476737658",
                "to": "Visa Platinum 8990922113665229"
            },
            {
                "id": 587085106,
                "state": "EXECUTED",
                "date": "2018-03-23T10:45:06.972075",
                "operationAmount": {
                    "amount": "48223.05",
                    "currency": {
                        "name": "EUR",
                        "code": "EUR"
                    }
                },
                "description": "Перевод со счета на счет",
                "from": "Счет 75106830613657916952",
                "to": "Счет 84112757540888855644"
            }
        ]

    @pytest.fixture
    def empty_transactions(self) -> List[Dict[str, Any]]:
        """Фикстура с пустым списком транзакций."""
        return []

    def test_filter_by_currency_returns_generator(self, sample_transactions):
        """Проверяет, что функция возвращает генератор."""
        result = filter_by_currency(sample_transactions, "USD")

        assert isinstance(result, Generator)
        assert hasattr(result, '__iter__')
        assert hasattr(result, '__next__')

    def test_filter_by_currency_usd_success(self, sample_transactions):
        """Проверяет корректную фильтрацию USD-транзакций."""
        usd_transactions = filter_by_currency(sample_transactions, "USD")

        # Получаем все отфильтрованные транзакции
        filtered_list = list(usd_transactions)

        # Проверяем количество
        assert len(filtered_list) == 2

        # Проверяем, что все транзакции имеют валюту USD
        for transaction in filtered_list:
            currency_code = transaction["operationAmount"]["currency"]["code"]
            assert currency_code == "USD"

        # Проверяем ID отфильтрованных транзакций
        filtered_ids = [t["id"] for t in filtered_list]
        assert 939719570 in filtered_ids
        assert 142264268 in filtered_ids

    def test_filter_by_currency_eur_success(self, sample_transactions):
        """Проверяет корректную фильтрацию EUR-транзакций."""
        eur_transactions = filter_by_currency(sample_transactions, "EUR")

        filtered_list = list(eur_transactions)

        assert len(filtered_list) == 1
        assert filtered_list[0]["id"] == 587085106

        currency_code = filtered_list[0]["operationAmount"]["currency"]["code"]
        assert currency_code == "EUR"

    def test_filter_by_currency_rub_success(self, sample_transactions):
        """Проверяет корректную фильтрацию RUB-транзакций."""
        rub_transactions = filter_by_currency(sample_transactions, "RUB")

        filtered_list = list(rub_transactions)

        assert len(filtered_list) == 1
        assert filtered_list[0]["id"] == 895315941

        currency_code = filtered_list[0]["operationAmount"]["currency"]["code"]
        assert currency_code == "RUB"

    def test_filter_by_currency_no_matching_currency(self, sample_transactions):
        """Проверяет обработку случая, когда транзакции с искомой валютой отсутствуют."""
        # GBP отсутствует в транзакциях
        gbp_transactions = filter_by_currency(sample_transactions, "GBP")

        # Преобразуем в список
        filtered_list = list(gbp_transactions)

        # Проверяем, что список пуст
        assert len(filtered_list) == 0

        # Проверяем, что генератор не выбрасывает исключение при итерации
        with pytest.raises(StopIteration):
            next(filter_by_currency(sample_transactions, "GBP"))

    def test_filter_by_currency_empty_list(self, empty_transactions):
        """Проверяет обработку пустого списка транзакций."""
        result = filter_by_currency(empty_transactions, "USD")

        # Проверяем, что функция возвращает генератор
        assert isinstance(result, Generator)

        # Проверяем, что генератор не содержит элементов
        filtered_list = list(result)
        assert len(filtered_list) == 0

        # Проверяем, что next выбрасывает StopIteration
        with pytest.raises(StopIteration):
            next(filter_by_currency(empty_transactions, "USD"))

    def test_filter_by_currency_no_currency_field(self):
        """Проверяет обработку транзакций без поля currency."""
        transactions_without_currency = [
            {
                "id": 1,
                "state": "EXECUTED",
                "description": "Перевод без валюты"
            },
            {
                "id": 2,
                "operationAmount": {
                    "amount": "100",
                    "currency": {
                        "name": "USD",
                        "code": "USD"
                    }
                },
                "description": "Перевод с валютой"
            }
        ]

        result = filter_by_currency(transactions_without_currency, "USD")
        filtered_list = list(result)

        # Должна быть найдена только транзакция с валютой
        assert len(filtered_list) == 1
        assert filtered_list[0]["id"] == 2

    def test_filter_by_currency_partial_currency_structure(self):
        """Проверяет обработку транзакций с неполной структурой валюты."""
        transactions_partial = [
            {
                "id": 1,
                "operationAmount": {
                    "amount": "100",
                    "currency": {
                        "code": "USD"
                    }
                }
            },
            {
                "id": 2,
                "operationAmount": {
                    "amount": "200",
                    "currency": {
                        "name": "USD"
                    }
                }
            },
            {
                "id": 3,
                "operationAmount": {
                    "amount": "300",
                    "currency": "USD"  # Неверная структура
                }
            }
        ]

        result = filter_by_currency(transactions_partial, "USD")
        filtered_list = list(result)

        # Функция должна обрабатывать некорректные данные без ошибок
        # В зависимости от реализации может найти 0 или 1 транзакцию
        # Главное - не должно быть исключений
        assert isinstance(filtered_list, list)

    def test_filter_by_currency_maintains_order(self, sample_transactions):
        """Проверяет, что порядок транзакций сохраняется."""
        usd_transactions = filter_by_currency(sample_transactions, "USD")
        filtered_list = list(usd_transactions)

        # Проверяем порядок следования
        assert filtered_list[0]["id"] == 939719570  # Первая USD в списке
        assert filtered_list[1]["id"] == 142264268  # Вторая USD в списке

    def test_filter_by_currency_multiple_calls(self, sample_transactions):
        """Проверяет, что генератор можно использовать повторно."""
        # Первый вызов
        usd_transactions_1 = filter_by_currency(sample_transactions, "USD")
        list_1 = list(usd_transactions_1)

        # Второй вызов
        usd_transactions_2 = filter_by_currency(sample_transactions, "USD")
        list_2 = list(usd_transactions_2)

        # Результаты должны быть одинаковыми
        assert len(list_1) == len(list_2)
        assert list_1[0]["id"] == list_2[0]["id"]

    def test_filter_by_currency_lazy_evaluation(self, sample_transactions):
        """Проверяет, что генератор работает лениво (не вычисляет все сразу)."""
        usd_transactions = filter_by_currency(sample_transactions, "USD")

        # Получаем первый элемент
        first = next(usd_transactions)
        assert first["id"] == 939719570

        # Получаем второй элемент
        second = next(usd_transactions)
        assert second["id"] == 142264268

        # Проверяем, что больше элементов нет
        with pytest.raises(StopIteration):
            next(usd_transactions)

    def test_filter_by_currency_with_different_currency_codes(self, sample_transactions):
        """Проверяет фильтрацию с разными кодами валют."""
        currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY"]

        for currency in currencies:
            result = filter_by_currency(sample_transactions, currency)
            filtered_list = list(result)

            # Проверяем, что все найденные транзакции имеют правильный код валюты
            for transaction in filtered_list:
                if "operationAmount" in transaction and "currency" in transaction["operationAmount"]:
                    currency_code = transaction["operationAmount"]["currency"].get("code")
                    assert currency_code == currency

    def test_filter_by_currency_case_sensitivity(self, sample_transactions):
        """Проверяет чувствительность к регистру при фильтрации."""
        # Проверяем с нижним регистром
        result_lower = filter_by_currency(sample_transactions, "usd")
        filtered_lower = list(result_lower)

        # Проверяем с верхним регистром
        result_upper = filter_by_currency(sample_transactions, "USD")
        filtered_upper = list(result_upper)

        # В зависимости от реализации, может быть разное поведение
        # Тест проверяет, что функция не падает при разных регистрах
        assert isinstance(filtered_lower, list)
        assert isinstance(filtered_upper, list)


class TestTransactionDescriptions:
    """Тесты для функции transaction_descriptions."""

    @pytest.fixture
    def sample_transactions(self) -> List[Dict[str, Any]]:
        """Фикстура с образцами транзакций для тестирования."""
        return [
            {
                "id": 939719570,
                "state": "EXECUTED",
                "date": "2018-06-30T02:08:58.425572",
                "operationAmount": {
                    "amount": "9824.07",
                    "currency": {
                        "name": "USD",
                        "code": "USD"
                    }
                },
                "description": "Перевод организации",
                "from": "Счет 75106830613657916952",
                "to": "Счет 11776614605963066702"
            },
            {
                "id": 142264268,
                "state": "EXECUTED",
                "date": "2019-04-04T23:20:05.206878",
                "operationAmount": {
                    "amount": "79114.93",
                    "currency": {
                        "name": "USD",
                        "code": "USD"
                    }
                },
                "description": "Перевод со счета на счет",
                "from": "Счет 19708645243227258542",
                "to": "Счет 75651667383060284188"
            },
            {
                "id": 895315941,
                "state": "EXECUTED",
                "date": "2018-08-19T04:27:37.904916",
                "operationAmount": {
                    "amount": "5683.33",
                    "currency": {
                        "name": "RUB",
                        "code": "RUB"
                    }
                },
                "description": "Перевод с карты на карту",
                "from": "Visa Classic 6831982476737658",
                "to": "Visa Platinum 8990922113665229"
            },
            {
                "id": 587085106,
                "state": "EXECUTED",
                "date": "2018-03-23T10:45:06.972075",
                "operationAmount": {
                    "amount": "48223.05",
                    "currency": {
                        "name": "EUR",
                        "code": "EUR"
                    }
                },
                "description": "Перевод со счета на счет",
                "from": "Счет 75106830613657916952",
                "to": "Счет 84112757540888855644"
            },
            {
                "id": 781165910,
                "state": "EXECUTED",
                "date": "2018-06-30T02:08:58.425572",
                "operationAmount": {
                    "amount": "32456.89",
                    "currency": {
                        "name": "USD",
                        "code": "USD"
                    }
                },
                "description": "Перевод организации",
                "from": "Счет 72082042523231494215",
                "to": "Счет 11776614605963066702"
            }
        ]

    @pytest.fixture
    def transactions_with_missing_description(self) -> List[Dict[str, Any]]:
        """Фикстура с транзакциями, у которых отсутствует описание."""
        return [
            {
                "id": 1,
                "state": "EXECUTED",
                "description": "Перевод организации",
                "amount": "100"
            },
            {
                "id": 2,
                "state": "EXECUTED",
                # description отсутствует
                "amount": "200"
            },
            {
                "id": 3,
                "state": "EXECUTED",
                "description": None,  # description равен None
                "amount": "300"
            },
            {
                "id": 4,
                "state": "EXECUTED",
                "description": "Перевод с карты на карту",
                "amount": "400"
            }
        ]

    @pytest.fixture
    def single_transaction(self) -> List[Dict[str, Any]]:
        """Фикстура с одной транзакцией."""
        return [
            {
                "id": 1,
                "description": "Единственная транзакция",
                "amount": "100"
            }
        ]

    @pytest.fixture
    def empty_transactions(self) -> List[Dict[str, Any]]:
        """Фикстура с пустым списком транзакций."""
        return []

    def test_returns_generator(self, sample_transactions):
        """Проверяет, что функция возвращает генератор."""
        result = transaction_descriptions(sample_transactions)

        assert isinstance(result, Generator)
        assert hasattr(result, '__iter__')
        assert hasattr(result, '__next__')

    def test_returns_correct_descriptions(self, sample_transactions):
        """Проверяет, что функция возвращает корректные описания."""
        descriptions = transaction_descriptions(sample_transactions)

        expected_descriptions = [
            "Перевод организации",
            "Перевод со счета на счет",
            "Перевод с карты на карту",
            "Перевод со счета на счет",
            "Перевод организации"
        ]

        for expected in expected_descriptions:
            actual = next(descriptions)
            assert actual == expected

    def test_returns_all_descriptions(self, sample_transactions):
        """Проверяет, что функция возвращает все описания."""
        descriptions = transaction_descriptions(sample_transactions)
        descriptions_list = list(descriptions)

        expected_count = len(sample_transactions)
        assert len(descriptions_list) == expected_count

        # Проверяем, что каждое описание соответствует транзакции
        for i, transaction in enumerate(sample_transactions):
            assert descriptions_list[i] == transaction["description"]

    def test_preserves_order(self, sample_transactions):
        """Проверяет, что порядок описаний соответствует порядку транзакций."""
        descriptions = transaction_descriptions(sample_transactions)

        for transaction in sample_transactions:
            expected_description = transaction["description"]
            actual_description = next(descriptions)
            assert actual_description == expected_description

    def test_empty_transactions(self, empty_transactions):
        """Проверяет обработку пустого списка транзакций."""
        descriptions = transaction_descriptions(empty_transactions)

        # Проверяем, что функция возвращает генератор
        assert isinstance(descriptions, Generator)

        # Проверяем, что генератор не содержит элементов
        descriptions_list = list(descriptions)
        assert len(descriptions_list) == 0

        # Проверяем, что next выбрасывает StopIteration
        with pytest.raises(StopIteration):
            next(transaction_descriptions(empty_transactions))

    def test_single_transaction(self, single_transaction):
        """Проверяет работу с одной транзакцией."""
        descriptions = transaction_descriptions(single_transaction)

        # Получаем описание
        description = next(descriptions)
        assert description == "Единственная транзакция"

        # Проверяем, что больше нет элементов
        with pytest.raises(StopIteration):
            next(descriptions)

    def test_multiple_transactions(self, sample_transactions):
        """Проверяет работу с множеством транзакций."""
        descriptions = transaction_descriptions(sample_transactions)

        count = 0
        for _ in descriptions:
            count += 1

        assert count == len(sample_transactions)

    def test_missing_description_field(self, transactions_with_missing_description):
        """Проверяет обработку транзакций без поля description."""
        descriptions = transaction_descriptions(transactions_with_missing_description)
        descriptions_list = list(descriptions)

        # Должны быть возвращены только существующие описания
        # (в зависимости от реализации)
        # Реализация может возвращать None или пустую строку для отсутствующих
        assert len(descriptions_list) == 4

        # Проверяем, что для транзакций с описанием возвращены корректные значения
        assert descriptions_list[0] == "Перевод организации"
        assert descriptions_list[3] == "Перевод с карты на карту"

    def test_description_field_is_none(self):
        """Проверяет обработку транзакций с description равным None."""
        transactions = [
            {"id": 1, "description": "Нормальное описание"},
            {"id": 2, "description": None},
            {"id": 3, "description": "Еще одно описание"}
        ]

        descriptions = transaction_descriptions(transactions)
        descriptions_list = list(descriptions)

        assert len(descriptions_list) == 3
        assert descriptions_list[0] == "Нормальное описание"
        assert descriptions_list[2] == "Еще одно описание"

        # Проверяем, что None обрабатывается корректно
        # (не выбрасывает исключение)
        assert descriptions_list[1] is None or descriptions_list[1] == "Описание отсутствует"

    def test_lazy_evaluation(self, sample_transactions):
        """Проверяет, что генератор работает лениво."""
        descriptions = transaction_descriptions(sample_transactions)

        # Получаем первый элемент
        first = next(descriptions)
        assert first == "Перевод организации"

        # Получаем второй элемент
        second = next(descriptions)
        assert second == "Перевод со счета на счет"

        # Проверяем, что остальные элементы все еще доступны
        remaining = list(descriptions)
        assert len(remaining) == 3

    def test_multiple_iterations(self, sample_transactions):
        """Проверяет, что генератор можно использовать для разных итераций."""
        # Первый генератор
        descriptions_1 = transaction_descriptions(sample_transactions)
        list_1 = list(descriptions_1)

        # Второй генератор (новый)
        descriptions_2 = transaction_descriptions(sample_transactions)
        list_2 = list(descriptions_2)

        # Результаты должны быть одинаковыми
        assert list_1 == list_2
        assert len(list_1) == len(sample_transactions)

    def test_stop_iteration_raised(self, sample_transactions):
        """Проверяет, что генератор выбрасывает StopIteration после завершения."""
        descriptions = transaction_descriptions(sample_transactions)

        # Получаем все элементы
        for _ in range(len(sample_transactions)):
            next(descriptions)

        # Попытка получить следующий элемент должна вызвать StopIteration
        with pytest.raises(StopIteration):
            next(descriptions)

    def test_does_not_modify_original_data(self, sample_transactions):
        """Проверяет, что функция не изменяет исходные данные."""
        original_transactions = sample_transactions.copy()

        descriptions = transaction_descriptions(sample_transactions)
        list(descriptions)  # Итерируем полностью

        # Проверяем, что исходные данные не изменились
        assert sample_transactions == original_transactions

    def test_description_data_type(self, sample_transactions):
        """Проверяет, что функция возвращает строки."""
        descriptions = transaction_descriptions(sample_transactions)

        for description in descriptions:
            assert isinstance(description, str)

    def test_different_description_formats(self):
        """Проверяет обработку различных форматов описаний."""
        transactions = [
            {"id": 1, "description": "Обычное описание"},
            {"id": 2, "description": "Описание с цифрами 123"},
            {"id": 3, "description": "Описание с символами!@#"},
            {"id": 4, "description": ""},  # Пустая строка
            {"id": 5, "description": "   "},  # Пробелы
            {"id": 6, "description": "Перевод организации №12345"}
        ]

        descriptions = transaction_descriptions(transactions)
        descriptions_list = list(descriptions)

        assert len(descriptions_list) == 6
        assert descriptions_list[0] == "Обычное описание"
        assert descriptions_list[1] == "Описание с цифрами 123"
        assert descriptions_list[2] == "Описание с символами!@#"
        assert descriptions_list[3] == ""
        assert descriptions_list[4] == "   "
        assert descriptions_list[5] == "Перевод организации №12345"


class TestCardNumberGenerator:
    """Тесты для генератора card_number_generator."""

    @pytest.fixture
    def small_range(self) -> tuple[int, int]:
        """Фикстура с малым диапазоном номеров."""
        return (1, 5)

    @pytest.fixture
    def medium_range(self) -> tuple[int, int]:
        """Фикстура со средним диапазоном номеров."""
        return (9995, 10005)

    @pytest.fixture
    def large_start_range(self) -> tuple[int, int]:
        """Фикстура с диапазоном в конце диапазона."""
        return (9999999999999990, 9999999999999995)

    @pytest.fixture
    def single_number_range(self) -> tuple[int, int]:
        """Фикстура с диапазоном из одного числа."""
        return (42, 42)

    def test_returns_generator(self, small_range):
        """Проверяет, что функция возвращает генератор."""
        start, end = small_range
        result = card_number_generator(start, end)

        assert isinstance(result, GeneratorType)
        assert hasattr(result, '__iter__')
        assert hasattr(result, '__next__')

    def test_correct_number_of_elements(self, small_range):
        """Проверяет, что генерируется правильное количество номеров."""
        start, end = small_range
        generator = card_number_generator(start, end)

        expected_count = end - start + 1
        actual_count = sum(1 for _ in generator)

        assert actual_count == expected_count

    def test_correct_format(self, small_range):
        """Проверяет корректность форматирования номеров карт."""
        start, end = small_range
        generator = card_number_generator(start, end)

        # Шаблон для проверки формата: 4 группы по 4 цифры, разделенные пробелом
        pattern = r'^\d{4} \d{4} \d{4} \d{4}$'

        for card_number in generator:
            assert re.match(pattern, card_number) is not None

    def test_correct_numbers_small_range(self, small_range):
        """Проверяет правильность номеров в малом диапазоне."""
        start, end = small_range
        generator = card_number_generator(start, end)

        expected_numbers = [
            "0000 0000 0000 0001",
            "0000 0000 0000 0002",
            "0000 0000 0000 0003",
            "0000 0000 0000 0004",
            "0000 0000 0000 0005"
        ]

        for expected in expected_numbers:
            actual = next(generator)
            assert actual == expected

    def test_correct_numbers_medium_range(self, medium_range):
        """Проверяет правильность номеров в среднем диапазоне."""
        start, end = medium_range
        generator = card_number_generator(start, end)

        expected_numbers = [
            "0000 0000 0000 9995",
            "0000 0000 0000 9996",
            "0000 0000 0000 9997",
            "0000 0000 0000 9998",
            "0000 0000 0000 9999",
            "0000 0000 0001 0000",
            "0000 0000 0001 0001",
            "0000 0000 0001 0002",
            "0000 0000 0001 0003",
            "0000 0000 0001 0004",
            "0000 0000 0001 0005"
        ]

        for expected in expected_numbers:
            actual = next(generator)
            assert actual == expected

    def test_correct_numbers_large_start_range(self, large_start_range):
        """Проверяет правильность номеров в диапазоне с большими числами."""
        start, end = large_start_range
        generator = card_number_generator(start, end)

        expected_numbers = [
            "9999 9999 9999 9990",
            "9999 9999 9999 9991",
            "9999 9999 9999 9992",
            "9999 9999 9999 9993",
            "9999 9999 9999 9994",
            "9999 9999 9999 9995"
        ]

        for expected in expected_numbers:
            actual = next(generator)
            assert actual == expected

    def test_single_number_range(self, single_number_range):
        """Проверяет работу с диапазоном из одного числа."""
        start, end = single_number_range
        generator = card_number_generator(start, end)

        expected = "0000 0000 0000 0042"
        actual = next(generator)
        assert actual == expected

        # Проверяем, что больше нет элементов
        with pytest.raises(StopIteration):
            next(generator)

    def test_range_start_from_one(self):
        """Проверяет начало диапазона с 1."""
        generator = card_number_generator(1, 3)

        assert next(generator) == "0000 0000 0000 0001"
        assert next(generator) == "0000 0000 0000 0002"
        assert next(generator) == "0000 0000 0000 0003"

    def test_range_with_zeros(self):
        """Проверяет диапазон с числами, содержащими много нулей."""
        generator = card_number_generator(1000, 1003)

        expected_numbers = [
            "0000 0000 0000 1000",
            "0000 0000 0000 1001",
            "0000 0000 0000 1002",
            "0000 0000 0000 1003"
        ]

        for expected in expected_numbers:
            assert next(generator) == expected

    def test_range_with_max_value(self):
        """Проверяет генерацию максимального номера карты."""
        generator = card_number_generator(9999999999999999, 9999999999999999)

        expected = "9999 9999 9999 9999"
        actual = next(generator)
        assert actual == expected

        with pytest.raises(StopIteration):
            next(generator)

    def test_format_consistency(self):
        """Проверяет, что все номера имеют одинаковый формат."""
        generator = card_number_generator(1, 100)

        for card_number in generator:
            # Проверяем длину строки (16 цифр + 3 пробела = 19)
            assert len(card_number) == 19

            # Проверяем, что разделители - пробелы
            assert card_number[4] == ' '
            assert card_number[9] == ' '
            assert card_number[14] == ' '

            # Проверяем, что все символы кроме пробелов - цифры
            parts = card_number.split()
            assert len(parts) == 4
            for part in parts:
                assert part.isdigit()
                assert len(part) == 4

    def test_correct_leading_zeros(self):
        """Проверяет правильность добавления ведущих нулей."""
        test_cases = [
            (1, "0000 0000 0000 0001"),
            (42, "0000 0000 0000 0042"),
            (123, "0000 0000 0000 0123"),
            (1234, "0000 0000 0000 1234"),
            (12345, "0000 0000 0001 2345"),
            (123456, "0000 0000 0012 3456"),
            (1234567, "0000 0000 0123 4567"),
            (12345678, "0000 0001 2345 6789"),
            (123456789, "0000 0123 4567 8901"),
        ]

        for number, expected in test_cases:
            generator = card_number_generator(number, number)
            assert next(generator) == expected

    def test_edge_values_boundaries(self):
        """Проверяет граничные значения диапазона."""
        # Минимальное значение
        generator_min = card_number_generator(1, 1)
        assert next(generator_min) == "0000 0000 0000 0001"

        # Максимальное значение
        generator_max = card_number_generator(9999999999999999, 9999999999999999)
        assert next(generator_max) == "9999 9999 9999 9999"

        # Значение с переходом через разряд
        generator_transition = card_number_generator(9999, 10001)
        assert next(generator_transition) == "0000 0000 0000 9999"
        assert next(generator_transition) == "0000 0000 0001 0000"
        assert next(generator_transition) == "0000 0000 0001 0001"

    def test_stop_iteration_after_range_end(self):
        """Проверяет, что генератор выбрасывает StopIteration после окончания."""
        generator = card_number_generator(1, 3)

        assert next(generator) == "0000 0000 0000 0001"
        assert next(generator) == "0000 0000 0000 0002"
        assert next(generator) == "0000 0000 0000 0003"

        with pytest.raises(StopIteration):
            next(generator)

    def test_lazy_evaluation(self):
        """Проверяет, что генератор работает лениво."""
        # Создаем генератор с большим диапазоном
        generator = card_number_generator(1, 1000000)

        # Получаем только первые 3 элемента
        first = next(generator)
        second = next(generator)
        third = next(generator)

        assert first == "0000 0000 0000 0001"
        assert second == "0000 0000 0000 0002"
        assert third == "0000 0000 0000 0003"

        # Проверяем, что генератор все еще жив
        assert hasattr(generator, '__next__')

    def test_multiple_iterations(self):
        """Проверяет, что можно создать несколько независимых генераторов."""
        generator1 = card_number_generator(1, 3)
        generator2 = card_number_generator(1, 3)

        # Оба генератора должны выдавать одинаковые значения
        assert list(generator1) == list(generator2)

    def test_large_range_memory_efficiency(self):
        """Проверяет, что генератор не хранит все значения в памяти."""
        import sys

        generator = card_number_generator(1, 1000000)

        # Размер генератора должен быть маленьким (не содержать все числа)
        generator_size = sys.getsizeof(generator)

        # Генератор должен занимать мало памяти (обычно < 1KB)
        assert generator_size < 1024  # Меньше 1KB

    def test_all_groups_have_four_digits(self):
        """Проверяет, что каждая группа содержит ровно 4 цифры."""
        generator = card_number_generator(1, 100)

        for card_number in generator:
            groups = card_number.split()
            for group in groups:
                assert len(group) == 4
                assert group.isdigit()

    def test_no_extra_spaces(self):
        """Проверяет, что в номере нет лишних пробелов."""
        generator = card_number_generator(1, 10)

        for card_number in generator:
            # Проверяем, что нет пробелов в начале и конце
            assert not card_number.startswith(' ')
            assert not card_number.endswith(' ')

            # Проверяем, что между группами ровно один пробел
            assert '  ' not in card_number

    def test_sequential_numbers(self):
        """Проверяет, что номера идут последовательно."""
        generator = card_number_generator(100, 110)

        previous = None
        for card_number in generator:
            if previous:
                # Преобразуем номер в число для проверки последовательности
                num_str = card_number.replace(' ', '')
                prev_num_str = previous.replace(' ', '')

                current_num = int(num_str)
                previous_num = int(prev_num_str)

                assert current_num == previous_num + 1

            previous = card_number

    def test_range_with_large_numbers(self):
        """Проверяет работу с большими числами в диапазоне."""
        start = 1234567890123456
        end = 1234567890123460

        generator = card_number_generator(start, end)

        expected_numbers = [
            "1234 5678 9012 3456",
            "1234 5678 9012 3457",
            "1234 5678 9012 3458",
            "1234 5678 9012 3459",
            "1234 5678 9012 3460"
        ]

        for expected in expected_numbers:
            assert next(generator) == expected

    def test_start_equals_end(self):
        """Проверяет случай, когда start равен end."""
        generator = card_number_generator(7777, 7777)

        assert next(generator) == "0000 0000 0000 7777"

        with pytest.raises(StopIteration):
            next(generator)