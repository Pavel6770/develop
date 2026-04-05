import pytest
from typing import List, Dict, Any
from collections.abc import Generator

# Импортируем тестируемую функцию
from src.generators import filter_by_currency, transaction_descriptions, card_number_generator


def test_filter_by_currency_matching_transactions():
    """Тест 1: Фильтрация транзакций с совпадающей валютой."""
    transactions = [
        {"operationAmount": {"currency": {"code": "USD"}, "amount": "100"}},
        {"operationAmount": {"currency": {"code": "EUR"}, "amount": "200"}},
        {"operationAmount": {"currency": {"code": "USD"}, "amount": "300"}},
    ]

    result = filter_by_currency(transactions, "USD")

    assert isinstance(result, Generator)
    result_list = list(result)
    assert len(result_list) == 2
    assert all(t["operationAmount"]["currency"]["code"] == "USD" for t in result_list)


def test_filter_by_currency_no_matching_transactions():
    """Тест 2: Нет транзакций с указанной валютой."""
    transactions = [
        {"operationAmount": {"currency": {"code": "EUR"}, "amount": "100"}},
        {"operationAmount": {"currency": {"code": "GBP"}, "amount": "200"}},
    ]

    result = filter_by_currency(transactions, "USD")

    assert list(result) == []


def test_filter_by_currency_skip_invalid_transactions():
    """Тест 3: Пропуск транзакций с некорректной структурой."""
    transactions = [
        {"operationAmount": {"currency": {"code": "USD"}, "amount": "100"}},  # корректная
        {"invalid": "structure"},  # некорректная (KeyError)
        {"operationAmount": None, "amount": "200"},  # некорректная (TypeError)
        {"operationAmount": {"currency": {"code": "USD"}, "amount": "300"}},  # корректная
    ]

    result = filter_by_currency(transactions, "USD")

    result_list = list(result)
    assert len(result_list) == 2
    assert result_list[0]["operationAmount"]["amount"] == "100"
    assert result_list[1]["operationAmount"]["amount"] == "300"


class TestTransactionDescriptions:
    """Тесты для функции transaction_descriptions."""

    @pytest.fixture
    def sample_transactions(self) -> List[Dict[str, Any]]:
        """Фикстура с образцами транзакций для тестирования."""
        return [
            {
                "id": 939719570,
                "state": "EXECUTED",
                "description": "Перевод организации",
                "amount": "9824.07"
            },
            {
                "id": 142264268,
                "state": "EXECUTED",
                "description": "Перевод со счета на счет",
                "amount": "79114.93"
            },
            {
                "id": 895315941,
                "state": "EXECUTED",
                "description": "Перевод с карты на карту",
                "amount": "5683.33"
            }
        ]

    @pytest.fixture
    def transactions_with_missing_description(self) -> List[Dict[str, Any]]:
        """Фикстура с транзакциями, у которых отсутствует описание."""
        return [
            {
                "id": 1,
                "description": "Перевод организации",
                "amount": "100"
            },
            {
                "id": 2,
                "amount": "200"  # description отсутствует
            },
            {
                "id": 3,
                "description": None,  # description равен None
                "amount": "300"
            },
            {
                "id": 4,
                "description": "Перевод с карты на карту",
                "amount": "400"
            }
        ]

    def test_transaction_descriptions_returns_generator(self, sample_transactions):
        """
        Тест 1: Проверяет, что функция возвращает генератор.

        Убеждаемся, что возвращаемый объект является генератором и имеет
        необходимые методы для итерации.
        """
        result = transaction_descriptions(sample_transactions)

        assert isinstance(result, Generator)
        assert hasattr(result, '__iter__')
        assert hasattr(result, '__next__')

    def test_transaction_descriptions_returns_correct_descriptions(self, sample_transactions):
        """
        Тест 2: Проверяет корректность возвращаемых описаний.

        Убеждаемся, что функция возвращает правильные описания для каждой
        транзакции в правильном порядке.
        """
        descriptions = transaction_descriptions(sample_transactions)

        expected_descriptions = [
            "Перевод организации",
            "Перевод со счета на счет",
            "Перевод с карты на карту"
        ]

        for expected in expected_descriptions:
            actual = next(descriptions)
            assert actual == expected

        # Проверяем, что все описания были получены
        with pytest.raises(StopIteration):
            next(descriptions)

    def test_transaction_descriptions_missing_description(self, transactions_with_missing_description):
        """
        Тест 3: Проверяет обработку транзакций без описания.

        Убеждаемся, что для транзакций с отсутствующим описанием или
        description=None возвращается строка "Описание отсутствует".
        """
        descriptions = transaction_descriptions(transactions_with_missing_description)

        # Первая транзакция - есть описание
        assert next(descriptions) == "Перевод организации"

        # Вторая транзакция - отсутствует поле description
        assert next(descriptions) == "Описание отсутствует"

        # Третья транзакция - description равен None
        assert next(descriptions) == "Описание отсутствует"

        # Четвертая транзакция - есть описание
        assert next(descriptions) == "Перевод с карты на карту"

        # Проверяем, что больше нет элементов
        with pytest.raises(StopIteration):
            next(descriptions)


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


class TestCardNumberGenerator:
    """Тесты для генератора card_number_generator."""

    @pytest.fixture
    def small_range(self) -> tuple[int, int]:
        """Фикстура с малым диапазоном номеров."""
        return (1, 5)

    @pytest.fixture
    def single_number(self) -> tuple[int, int]:
        """Фикстура с одним номером."""
        return (42, 42)

    def test_card_number_generator_returns_generator(self, small_range):
        """
        Тест 1: Проверяет, что функция возвращает генератор.

        Убеждаемся, что возвращаемый объект является генератором и имеет
        необходимые методы для итерации.
        """
        start, end = small_range
        result = card_number_generator(start, end)

        assert isinstance(result, GeneratorType)
        assert hasattr(result, '__iter__')
        assert hasattr(result, '__next__')

    def test_card_number_generator_correct_format(self, small_range):
        """
        Тест 2: Проверяет корректность форматирования номеров карт.

        Убеждаемся, что все сгенерированные номера соответствуют формату
        "XXXX XXXX XXXX XXXX", где X - цифры.
        """
        start, end = small_range
        generator = card_number_generator(start, end)

        # Шаблон для проверки формата: 4 группы по 4 цифры, разделенные пробелом
        pattern = r'^\d{4} \d{4} \d{4} \d{4}$'

        for card_number in generator:
            # Проверяем соответствие формату
            assert re.match(pattern, card_number) is not None

            # Проверяем длину строки (16 цифр + 3 пробела = 19)
            assert len(card_number) == 19

            # Проверяем позиции пробелов
            assert card_number[4] == ' '
            assert card_number[9] == ' '
            assert card_number[14] == ' '

            # Проверяем, что каждая группа состоит из 4 цифр
            groups = card_number.split()
            assert len(groups) == 4
            for group in groups:
                assert len(group) == 4
                assert group.isdigit()

    def test_card_number_generator_correct_numbers(self):
        """
        Тест 3: Проверяет правильность генерации номеров в различных диапазонах.

        Убеждаемся, что функция генерирует правильные номера карт для
        разных диапазонов, включая граничные значения и переход через разряды.
        """
        # Тест 3.1: Малый диапазон
        generator = card_number_generator(1, 3)
        assert next(generator) == "0000 0000 0000 0001"
        assert next(generator) == "0000 0000 0000 0002"
        assert next(generator) == "0000 0000 0000 0003"

        # Тест 3.2: Диапазон с переходом через разряд
        generator = card_number_generator(9998, 10002)
        assert next(generator) == "0000 0000 0000 9998"
        assert next(generator) == "0000 0000 0000 9999"
        assert next(generator) == "0000 0000 0001 0000"
        assert next(generator) == "0000 0000 0001 0001"
        assert next(generator) == "0000 0000 0001 0002"

        # Тест 3.3: Один номер
        start, end = 42, 42
        generator = card_number_generator(start, end)
        assert next(generator) == "0000 0000 0000 0042"

        # Тест 3.4: Максимальное значение
        generator = card_number_generator(9999999999999999, 9999999999999999)
        assert next(generator) == "9999 9999 9999 9999"

        # Тест 3.5: Проверка ведущих нулей для разных чисел
        test_cases = [
            (1, "0000 0000 0000 0001"),
            (123, "0000 0000 0000 0123"),
            (1234, "0000 0000 0000 1234"),
            (12345, "0000 0000 0001 2345"),
            (12345678, "0000 0001 2345 6789"),
            (123456789012, "0000 1234 5678 9012"),
        ]

        for number, expected in test_cases:
            generator = card_number_generator(number, number)
            assert next(generator) == expected

        # Проверяем StopIteration после завершения
        generator = card_number_generator(1, 1)
        next(generator)
        with pytest.raises(StopIteration):
            next(generator)