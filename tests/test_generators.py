import pytest
import re
from typing import Dict, Any, List, Tuple
from collections.abc import Generator


# Импортируем тестируемую функцию
from src.generators import filter_by_currency, card_number_generator
from src.generators import transaction_descriptions

@pytest.mark.parametrize("transactions, currency, expected_count, expected_amounts", [
    # Случай 1: Несколько транзакций с совпадающей валютой
    (
            [
                {"operationAmount": {"currency": {"code": "USD"}, "amount": "100"}},
                {"operationAmount": {"currency": {"code": "EUR"}, "amount": "200"}},
                {"operationAmount": {"currency": {"code": "USD"}, "amount": "300"}},
            ],
            "USD",
            2,
            ["100", "300"]
    ),
    # Случай 2: Все транзакции с нужной валютой
    (
            [
                {"operationAmount": {"currency": {"code": "RUB"}, "amount": "50"}},
                {"operationAmount": {"currency": {"code": "RUB"}, "amount": "150"}},
                {"operationAmount": {"currency": {"code": "RUB"}, "amount": "250"}},
            ],
            "RUB",
            3,
            ["50", "150", "250"]
    ),
    # Случай 3: Одна транзакция с совпадающей валютой
    (
            [
                {"operationAmount": {"currency": {"code": "EUR"}, "amount": "1000"}},
                {"operationAmount": {"currency": {"code": "USD"}, "amount": "500"}},
            ],
            "EUR",
            1,
            ["1000"]
    ),
])
def test_filter_by_currency_matching_transactions(
        transactions: List[Dict[str, Any]],
        currency: str,
        expected_count: int,
        expected_amounts: List[str]
):
    """Параметризованный тест: Фильтрация транзакций с совпадающей валютой."""
    result = filter_by_currency(transactions, currency)

    assert isinstance(result, Generator)
    result_list = list(result)
    assert len(result_list) == expected_count
    assert all(t["operationAmount"]["currency"]["code"] == currency for t in result_list)

    if expected_amounts:
        actual_amounts = [t["operationAmount"]["amount"] for t in result_list]
        assert actual_amounts == expected_amounts


@pytest.mark.parametrize("transactions, currency", [
    # Случай 1: Нет транзакций с указанной валютой
    (
            [
                {"operationAmount": {"currency": {"code": "EUR"}, "amount": "100"}},
                {"operationAmount": {"currency": {"code": "GBP"}, "amount": "200"}},
            ],
            "USD"
    ),
    # Случай 2: Пустой список транзакций
    ([], "USD"),
    # Случай 3: Транзакции с другими валютами
    (
            [
                {"operationAmount": {"currency": {"code": "RUB"}, "amount": "100"}},
                {"operationAmount": {"currency": {"code": "RUB"}, "amount": "200"}},
            ],
            "EUR"
    ),
])
def test_filter_by_currency_no_matching_transactions(
        transactions: List[Dict[str, Any]],
        currency: str
):
    """Параметризованный тест: Нет транзакций с указанной валютой."""
    result = filter_by_currency(transactions, currency)
    assert list(result) == []


@pytest.mark.parametrize("transactions, currency, expected_count, expected_amounts", [
    # Случай 1: Некорректные структуры в начале и середине
    (
            [
                {"invalid": "structure"},
                {"operationAmount": {"currency": {"code": "USD"}, "amount": "100"}},
                {"operationAmount": None, "amount": "200"},
                {"operationAmount": {"currency": {"code": "USD"}, "amount": "300"}},
            ],
            "USD",
            2,
            ["100", "300"]
    ),
    # Случай 2: Только некорректные транзакции
    (
            [
                {"invalid": "structure1"},
                {"invalid": "structure2"},
                {"operationAmount": None},
                None,
            ],
            "USD",
            0,
            []
    ),
    # Случай 3: Перемешанные корректные и некорректные с разными валютами
    (
            [
                {"operationAmount": {"currency": {"code": "USD"}, "amount": "10"}},
                {"bad": "data"},
                {"operationAmount": {"currency": {"code": "EUR"}, "amount": "20"}},
                None,
                {"operationAmount": {"currency": {"code": "USD"}, "amount": "30"}},
                {"operationAmount": {"currency": {"code": "GBP"}, "amount": "40"}},
            ],
            "USD",
            2,
            ["10", "30"]
    ),
])
def test_filter_by_currency_skip_invalid_transactions(
        transactions: List[Dict[str, Any]],
        currency: str,
        expected_count: int,
        expected_amounts: List[str]
):
    """Параметризованный тест: Пропуск транзакций с некорректной структурой."""
    result = filter_by_currency(transactions, currency)
    result_list = list(result)

    assert len(result_list) == expected_count

    if expected_amounts:
        actual_amounts = [t["operationAmount"]["amount"] for t in result_list]
        assert actual_amounts == expected_amounts


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
        Тест: Проверяет, что функция возвращает генератор.
        """
        result = transaction_descriptions(sample_transactions)

        assert isinstance(result, Generator)
        assert hasattr(result, '__iter__')
        assert hasattr(result, '__next__')

    @pytest.mark.parametrize("transactions, expected_descriptions", [
        # Случай 1: Обычные транзакции с описаниями
        (
            [
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
            ],
            [
                "Перевод организации",
                "Перевод со счета на счет",
                "Перевод с карты на карту"
            ]
        ),
        # Случай 2: Пустой список транзакций
        ([], []),
        # Случай 3: Одна транзакция
        (
            [
                {
                    "id": 1,
                    "description": "Оплата услуг",
                    "amount": "1000"
                }
            ],
            ["Оплата услуг"]
        ),
        # Случай 4: Транзакции с одинаковыми описаниями
        (
            [
                {"id": 1, "description": "Перевод", "amount": "100"},
                {"id": 2, "description": "Перевод", "amount": "200"},
                {"id": 3, "description": "Перевод", "amount": "300"},
            ],
            ["Перевод", "Перевод", "Перевод"]
        ),
    ])
    def test_transaction_descriptions_returns_correct_descriptions(
        self,
        transactions: List[Dict[str, Any]],
        expected_descriptions: List[str]
    ):
        """
        Параметризованный тест: Проверяет корректность возвращаемых описаний.
        """
        descriptions = transaction_descriptions(transactions)

        # Проверяем, что возвращается генератор
        assert isinstance(descriptions, Generator)

        # Получаем все описания
        result_descriptions = list(descriptions)

        # Сравниваем с ожидаемыми
        assert result_descriptions == expected_descriptions


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
                "amount": "200"
            },
            {
                "id": 3,
                "description": None,
                "amount": "300"
            },
            {
                "id": 4,
                "description": "Перевод с карты на карту",
                "amount": "400"
            }
        ]

    @pytest.mark.parametrize("transactions, expected_descriptions", [
        # Случай 1: Пропуск транзакций с отсутствующим описанием
        (
            [
                {"id": 1, "description": "Перевод организации", "amount": "100"},
                {"id": 2, "amount": "200"},
                {"id": 3, "description": None, "amount": "300"},
                {"id": 4, "description": "Перевод с карты на карту", "amount": "400"},
            ],
            [
                "Перевод организации",
                "Описание отсутствует",
                "Описание отсутствует",
                "Перевод с карты на карту"
            ]
        ),
        # Случай 2: Все транзакции без описания
        (
            [
                {"id": 1, "amount": "100"},
                {"id": 2, "description": None, "amount": "200"},
                {"id": 3, "amount": "300"},
            ],
            [
                "Описание отсутствует",
                "Описание отсутствует",
                "Описание отсутствует"
            ]
        ),
        # Случай 3: Смешанные данные с корректными и некорректными полями
        (
            [
                {"id": 1, "description": "Нормальная транзакция", "amount": "100"},
                {"id": 2, "wrong_field": "data"},
                {"id": 3, "description": "", "amount": "300"},
                {"id": 4, "description": "Еще одна нормальная", "amount": "400"},
            ],
            [
                "Нормальная транзакция",
                "Описание отсутствует",
                "",  # пустая строка возвращается как есть
                "Еще одна нормальная"
            ]
        ),
    ])
    def test_transaction_descriptions_missing_description(
        self,
        transactions: List[Dict[str, Any]],
        expected_descriptions: List[str]
    ):
        """
        Параметризованный тест: Проверяет обработку транзакций без описания.
        """
        descriptions = transaction_descriptions(transactions)

        for expected in expected_descriptions:
            actual = next(descriptions)
            assert actual == expected

        # Проверяем, что больше нет элементов
        with pytest.raises(StopIteration):
            next(descriptions)


class TestTransactionDescriptions:
    """Тесты для функции transaction_descriptions."""

    @pytest.mark.parametrize("transactions, expected_descriptions", [
        # Случай 1: Пустой список
        ([], []),
        # Случай 2: Список с None вместо транзакции
        (
            [None, {"description": "valid", "amount": "100"}],
            ["Описание отсутствует", "valid"]
        ),
        # Случай 3: Транзакция без поля description
        (
            [{"id": 1, "amount": "500"}],
            ["Описание отсутствует"]
        ),
        # Случай 4: Транзакция с description = None
        (
            [{"id": 2, "description": None, "amount": "300"}],
            ["Описание отсутствует"]
        ),
        # Случай 5: Смешанные корректные и некорректные транзакции
        (
            [
                {"id": 1, "description": "Нормальная", "amount": "100"},
                None,
                {"id": 2, "amount": "200"},
                {"id": 3, "description": None, "amount": "300"},
                {"id": 4, "description": "Еще нормальная", "amount": "400"}
            ],
            [
                "Нормальная",
                "Описание отсутствует",
                "Описание отсутствует",
                "Описание отсутствует",
                "Еще нормальная"
            ]
        ),
    ])
    def test_transaction_descriptions_edge_cases(
        self,
        transactions: List[Dict[str, Any]],
        expected_descriptions: List[str]
    ):
        """
        Параметризованный тест: Проверяет граничные случаи.
        """
        descriptions = transaction_descriptions(transactions)

        # Проверяем, что возвращается генератор
        assert isinstance(descriptions, Generator)

        # Получаем все описания
        result_descriptions = list(descriptions)

        # Сравниваем с ожидаемыми
        assert result_descriptions == expected_descriptions


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

    @pytest.mark.parametrize("transactions, expected_descriptions", [
        # Случай 1: Обычный случай с пропущенными описаниями
        (
                [
                    {"id": 1, "description": "Перевод организации", "amount": "100"},
                    {"id": 2, "amount": "200"},
                    {"id": 3, "description": None, "amount": "300"},
                    {"id": 4, "description": "Перевод с карты на карту", "amount": "400"},
                ],
                [
                    "Перевод организации",
                    "Описание отсутствует",
                    "Описание отсутствует",
                    "Перевод с карты на карту"
                ]
        ),
        # Случай 2: Все транзакции без описания
        (
                [
                    {"id": 1, "amount": "100"},
                    {"id": 2, "description": None, "amount": "200"},
                    {"id": 3, "amount": "300"},
                ],
                [
                    "Описание отсутствует",
                    "Описание отсутствует",
                    "Описание отсутствует"
                ]
        ),
        # Случай 3: Пустая строка в описании (не считается отсутствующим)
        (
                [
                    {"id": 1, "description": "", "amount": "100"},
                    {"id": 2, "description": "   ", "amount": "200"},
                ],
                [
                    "",
                    "   "
                ]
        ),
        # Случай 4: Смешанные данные с некорректными транзакциями
        (
                [
                    {"id": 1, "description": "Нормальная транзакция", "amount": "100"},
                    None,  # некорректная транзакция
                    {"id": 3, "amount": "300"},
                    {"id": 4, "description": "Еще одна нормальная", "amount": "400"},
                ],
                [
                    "Нормальная транзакция",
                    "Описание отсутствует",
                    "Описание отсутствует",
                    "Еще одна нормальная"
                ]
        ),
    ])
    def test_transaction_descriptions_missing_description(
            self,
            transactions: List[Dict[str, Any]],
            expected_descriptions: List[str]
    ):
        """
        Параметризованный тест: Проверяет обработку транзакций без описания.
        """
        descriptions = transaction_descriptions(transactions)

        for expected in expected_descriptions:
            actual = next(descriptions)
            assert actual == expected

        # Проверяем, что больше нет элементов
        with pytest.raises(StopIteration):
            next(descriptions)


class TestCardNumberGenerator:
    """Тесты для генератора card_number_generator."""

    @pytest.fixture
    def small_range(self) -> Tuple[int, int]:
        """Фикстура с малым диапазоном номеров."""
        return (1, 5)

    @pytest.fixture
    def medium_range(self) -> Tuple[int, int]:
        """Фикстура со средним диапазоном номеров."""
        return (9995, 10005)

    @pytest.fixture
    def large_start_range(self) -> Tuple[int, int]:
        """Фикстура с диапазоном в конце диапазона."""
        return (9999999999999990, 9999999999999995)

    @pytest.fixture
    def single_number_range(self) -> Tuple[int, int]:
        """Фикстура с диапазоном из одного числа."""
        return (42, 42)

    @pytest.mark.parametrize("start, end", [
        (1, 5),
        (100, 105),
        (9995, 10005),
        (42, 42),
    ])
    def test_returns_generator(self, start: int, end: int):
        """Параметризованный тест: Проверяет, что функция возвращает генератор."""
        result = card_number_generator(start, end)

        assert isinstance(result, Generator)
        assert hasattr(result, '__iter__')
        assert hasattr(result, '__next__')

    @pytest.mark.parametrize("start, end, expected_count", [
        (1, 5, 5),
        (10, 10, 1),
        (100, 105, 6),
        (9995, 10005, 11),
        (1, 100, 100),
    ])
    def test_correct_number_of_elements(
            self,
            start: int,
            end: int,
            expected_count: int
    ):
        """Параметризованный тест: Проверяет правильное количество номеров."""
        generator = card_number_generator(start, end)
        actual_count = sum(1 for _ in generator)
        assert actual_count == expected_count

    @pytest.mark.parametrize("start, end", [
        (1, 5),
        (100, 105),
        (9995, 10005),
        (42, 42),
        (9999999999999990, 9999999999999995),
    ])
    def test_correct_format(self, start: int, end: int):
        """Параметризованный тест: Проверяет корректность форматирования."""
        generator = card_number_generator(start, end)
        pattern = r'^\d{4} \d{4} \d{4} \d{4}$'

        for card_number in generator:
            assert re.match(pattern, card_number) is not None

    @pytest.mark.parametrize("start, end, expected_numbers", [
        # Малый диапазон
        (
                1, 5,
                [
                    "0000 0000 0000 0001",
                    "0000 0000 0000 0002",
                    "0000 0000 0000 0003",
                    "0000 0000 0000 0004",
                    "0000 0000 0000 0005"
                ]
        ),
        # Диапазон с одним числом
        (
                42, 42,
                ["0000 0000 0000 0042"]
        ),
        # Диапазон с переходом через десяток
        (
                8, 12,
                [
                    "0000 0000 0000 0008",
                    "0000 0000 0000 0009",
                    "0000 0000 0000 0010",
                    "0000 0000 0000 0011",
                    "0000 0000 0000 0012"
                ]
        ),
        # Диапазон с трехзначными числами
        (
                99, 102,
                [
                    "0000 0000 0000 0099",
                    "0000 0000 0000 0100",
                    "0000 0000 0000 0101",
                    "0000 0000 0000 0102"
                ]
        ),
    ])
    def test_correct_numbers_small_range(
            self,
            start: int,
            end: int,
            expected_numbers: List[str]
    ):
        """Параметризованный тест: Проверяет правильность номеров."""
        generator = card_number_generator(start, end)

        for expected in expected_numbers:
            actual = next(generator)
            assert actual == expected

    @pytest.mark.parametrize("start, end, expected_numbers", [
        # Диапазон с большими числами в конце (16-значные числа)
        (
                9999999999999990, 9999999999999995,
                [
                    "9999 9999 9999 9990",
                    "9999 9999 9999 9991",
                    "9999 9999 9999 9992",
                    "9999 9999 9999 9993",
                    "9999 9999 9999 9994",
                    "9999 9999 9999 9995"
                ]
        ),
        # Диапазон с 15-значными числами (добавляется ведущий ноль)
        (
                999999999995000, 999999999995003,
                [
                    "0999 9999 9999 5000",  # Исправлено
                    "0999 9999 9999 5001",  # Исправлено
                    "0999 9999 9999 5002",  # Исправлено
                    "0999 9999 9999 5003"  # Исправлено
                ]
        ),
        # Другой вариант с 16-значными числами
        (
                1234567890123456, 1234567890123460,
                [
                    "1234 5678 9012 3456",
                    "1234 5678 9012 3457",
                    "1234 5678 9012 3458",
                    "1234 5678 9012 3459",
                    "1234 5678 9012 3460"
                ]
        ),
    ])
    def test_correct_numbers_large_start_range(
            self,
            start: int,
            end: int,
            expected_numbers: List[str]
    ):
        """Параметризованный тест: Проверяет правильность номеров в диапазоне с большими числами."""
        generator = card_number_generator(start, end)

        for expected in expected_numbers:
            actual = next(generator)
            assert actual == expected

    @pytest.mark.parametrize("start, end, expected", [
        (42, 42, "0000 0000 0000 0042"),
        (1, 1, "0000 0000 0000 0001"),
        (100, 100, "0000 0000 0000 0100"),
        (9999, 9999, "0000 0000 0000 9999"),
        (10000, 10000, "0000 0000 0001 0000"),
        (9999999999999999, 9999999999999999, "9999 9999 9999 9999"),
    ])
    def test_single_number_range(
            self,
            start: int,
            end: int,
            expected: str
    ):
        """Параметризованный тест: Проверяет работу с диапазоном из одного числа."""
        generator = card_number_generator(start, end)

        actual = next(generator)
        assert actual == expected

        # Проверяем, что больше нет элементов
        with pytest.raises(StopIteration):
            next(generator)

    @pytest.mark.parametrize("start, end, expected_numbers", [
        (1, 3, ["0000 0000 0000 0001", "0000 0000 0000 0002", "0000 0000 0000 0003"]),
        (5, 7, ["0000 0000 0000 0005", "0000 0000 0000 0006", "0000 0000 0000 0007"]),
        (10, 12, ["0000 0000 0000 0010", "0000 0000 0000 0011", "0000 0000 0000 0012"]),
    ])
    def test_range_start_from_one(
            self,
            start: int,
            end: int,
            expected_numbers: List[str]
    ):
        """Параметризованный тест: Проверяет различные начала диапазонов."""
        generator = card_number_generator(start, end)

        for expected in expected_numbers:
            assert next(generator) == expected

    @pytest.mark.parametrize("start, end, expected_numbers", [
        (1000, 1003, [
            "0000 0000 0000 1000",
            "0000 0000 0000 1001",
            "0000 0000 0000 1002",
            "0000 0000 0000 1003"
        ]),
        (5000, 5003, [
            "0000 0000 0000 5000",
            "0000 0000 0000 5001",
            "0000 0000 0000 5002",
            "0000 0000 0000 5003"
        ]),
        (10000, 10003, [
            "0000 0000 0001 0000",
            "0000 0000 0001 0001",
            "0000 0000 0001 0002",
            "0000 0000 0001 0003"
        ]),
    ])
    def test_range_with_zeros(
            self,
            start: int,
            end: int,
            expected_numbers: List[str]
    ):
        """Параметризованный тест: Проверяет диапазоны с числами, содержащими много нулей."""
        generator = card_number_generator(start, end)

        for expected in expected_numbers:
            assert next(generator) == expected

    @pytest.mark.parametrize("start, end, expected", [
        (9999999999999999, 9999999999999999, "9999 9999 9999 9999"),
        (9999999999999998, 9999999999999998, "9999 9999 9999 9998"),
        (1000000000000000, 1000000000000000, "1000 0000 0000 0000"),
    ])
    def test_range_with_max_value(
            self,
            start: int,
            end: int,
            expected: str
    ):
        """Параметризованный тест: Проверяет генерацию максимальных номеров карт."""
        generator = card_number_generator(start, end)

        actual = next(generator)
        assert actual == expected

        with pytest.raises(StopIteration):
            next(generator)

    @pytest.mark.parametrize("start, end", [
        (1, 100),
        (500, 600),
        (1000, 1100),
        (9990, 10010),
    ])
    def test_format_consistency(self, start: int, end: int):
        """Параметризованный тест: Проверяет, что все номера имеют одинаковый формат."""
        generator = card_number_generator(start, end)

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

    @pytest.mark.parametrize("number, expected", [
        (1, "0000 0000 0000 0001"),
        (42, "0000 0000 0000 0042"),
        (123, "0000 0000 0000 0123"),
        (1234, "0000 0000 0000 1234"),
        (12345, "0000 0000 0001 2345"),
        (123456, "0000 0000 0012 3456"),
        (1234567, "0000 0000 0123 4567"),
        (12345678, "0000 0000 1234 5678"),  # Исправлено
        (123456789, "0000 0001 2345 6789"),  # 9 цифр → 7 ведущих нулей
        (1234567890, "0000 0012 3456 7890"),
        (12345678901, "0000 0123 4567 8901"),
        (123456789012, "0000 1234 5678 9012"),
        (1234567890123, "0001 2345 6789 0123"),
        (12345678901234, "0012 3456 7890 1234"),
        (123456789012345, "0123 4567 8901 2345"),
        (1234567890123456, "1234 5678 9012 3456"),
    ])
    def test_correct_leading_zeros(self, number: int, expected: str):
        """Параметризованный тест: Проверяет правильность добавления ведущих нулей."""
        generator = card_number_generator(number, number)
        assert next(generator) == expected


    @pytest.mark.parametrize("start, end, expected_sequence", [
        (1, 1, ["0000 0000 0000 0001"]),
        (9999999999999999, 9999999999999999, ["9999 9999 9999 9999"]),
        (9999, 10001, [
            "0000 0000 0000 9999",
            "0000 0000 0001 0000",
            "0000 0000 0001 0001"
        ]),
        (99999, 100001, [
            "0000 0000 0009 9999",
            "0000 0000 0010 0000",
            "0000 0000 0010 0001"
        ]),
    ])
    def test_edge_values_boundaries(
            self,
            start: int,
            end: int,
            expected_sequence: List[str]
    ):
        """Параметризованный тест: Проверяет граничные значения диапазона."""
        generator = card_number_generator(start, end)

        for expected in expected_sequence:
            assert next(generator) == expected

    @pytest.mark.parametrize("start, end", [
        (1, 3),
        (5, 7),
        (100, 102),
        (999, 1001),
    ])
    def test_stop_iteration_after_range_end(self, start: int, end: int):
        """Параметризованный тест: Проверяет StopIteration после окончания."""
        generator = card_number_generator(start, end)

        # Проходим все элементы
        for _ in range(end - start + 1):
            next(generator)

        # Проверяем, что больше нет элементов
        with pytest.raises(StopIteration):
            next(generator)

    @pytest.mark.parametrize("start, end, count", [
        (1, 1000000, 3),
        (5000, 500000, 5),
        (10000, 20000, 10),
    ])
    def test_lazy_evaluation(self, start: int, end: int, count: int):
        """Параметризованный тест: Проверяет, что генератор работает лениво."""
        generator = card_number_generator(start, end)

        # Получаем только первые count элементов
        first_elements = []
        for _ in range(count):
            first_elements.append(next(generator))

        # Проверяем, что генератор все еще жив
        assert hasattr(generator, '__next__')
        assert len(first_elements) == count

    @pytest.mark.parametrize("start, end", [
        (1, 3),
        (10, 15),
        (100, 105),
    ])
    def test_multiple_iterations(self, start: int, end: int):
        """Параметризованный тест: Проверяет создание независимых генераторов."""
        generator1 = card_number_generator(start, end)
        generator2 = card_number_generator(start, end)

        # Оба генератора должны выдавать одинаковые значения
        assert list(generator1) == list(generator2)

    @pytest.mark.parametrize("start, end", [
        (1, 100),
        (1000, 2000),
        (50000, 60000),
    ])
    def test_all_groups_have_four_digits(self, start: int, end: int):
        """Параметризованный тест: Проверяет, что каждая группа содержит ровно 4 цифры."""
        generator = card_number_generator(start, end)

        for card_number in generator:
            groups = card_number.split()
            for group in groups:
                assert len(group) == 4
                assert group.isdigit()

    @pytest.fixture
    def small_range(self) -> Tuple[int, int]:
        """Фикстура с малым диапазоном номеров."""
        return (1, 5)

    @pytest.fixture
    def single_number(self) -> Tuple[int, int]:
        """Фикстура с одним номером."""
        return (42, 42)

    @pytest.mark.parametrize("start, end", [
        (1, 10),
        (100, 110),
        (500, 510),
        (999, 1005),
    ])
    def test_no_extra_spaces(self, start: int, end: int):
        """Параметризованный тест: Проверяет, что в номере нет лишних пробелов."""
        generator = card_number_generator(start, end)

        for card_number in generator:
            # Проверяем, что нет пробелов в начале и конце
            assert not card_number.startswith(' ')
            assert not card_number.endswith(' ')

            # Проверяем, что между группами ровно один пробел
            assert '  ' not in card_number

    @pytest.mark.parametrize("start, end, expected_sequence", [
        (100, 110, list(range(100, 111))),
        (1, 10, list(range(1, 11))),
        (9995, 10005, list(range(9995, 10006))),
        (1000, 1005, list(range(1000, 1006))),
    ])
    def test_sequential_numbers(
            self,
            start: int,
            end: int,
            expected_sequence: List[int]
    ):
        """Параметризованный тест: Проверяет, что номера идут последовательно."""
        generator = card_number_generator(start, end)

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

    @pytest.mark.parametrize("start, end, expected_numbers", [
        (
                1234567890123456, 1234567890123460,
                [
                    "1234 5678 9012 3456",
                    "1234 5678 9012 3457",
                    "1234 5678 9012 3458",
                    "1234 5678 9012 3459",
                    "1234 5678 9012 3460"
                ]
        ),
        (
                9999999999999990, 9999999999999995,
                [
                    "9999 9999 9999 9990",
                    "9999 9999 9999 9991",
                    "9999 9999 9999 9992",
                    "9999 9999 9999 9993",
                    "9999 9999 9999 9994",
                    "9999 9999 9999 9995"
                ]
        ),
        (
                1000000000000000, 1000000000000003,
                [
                    "1000 0000 0000 0000",
                    "1000 0000 0000 0001",
                    "1000 0000 0000 0002",
                    "1000 0000 0000 0003"
                ]
        ),
    ])
    def test_range_with_large_numbers(
            self,
            start: int,
            end: int,
            expected_numbers: List[str]
    ):
        """Параметризованный тест: Проверяет работу с большими числами в диапазоне."""
        generator = card_number_generator(start, end)

        for expected in expected_numbers:
            assert next(generator) == expected

    @pytest.mark.parametrize("number, expected", [
        (7777, "0000 0000 0000 7777"),
        (1, "0000 0000 0000 0001"),
        (9999, "0000 0000 0000 9999"),
        (10000, "0000 0000 0001 0000"),
        (12345678, "0000 0000 1234 5678"),  # Исправлено
        (123456789, "0000 0001 2345 6789"),  # Добавлен правильный пример для 9 цифр
        (9999999999999999, "9999 9999 9999 9999"),
    ])
    def test_start_equals_end(self, number: int, expected: str):
        """Параметризованный тест: Проверяет случай, когда start равен end."""
        generator = card_number_generator(number, number)

        assert next(generator) == expected

        with pytest.raises(StopIteration):
            next(generator)

    @pytest.mark.parametrize("start, end", [
        (1, 5),
        (10, 15),
        (100, 105),
        (999, 1005),
    ])
    def test_card_number_generator_returns_generator(self, start: int, end: int):
        """
        Параметризованный тест 1: Проверяет, что функция возвращает генератор.
        """
        result = card_number_generator(start, end)

        assert isinstance(result, Generator)
        assert hasattr(result, '__iter__')
        assert hasattr(result, '__next__')

    @pytest.mark.parametrize("start, end", [
        (1, 5),
        (100, 105),
        (9995, 10005),
        (42, 42),
    ])
    def test_card_number_generator_correct_format(self, start: int, end: int):
        """
        Параметризованный тест 2: Проверяет корректность форматирования номеров карт.
        """
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

    @pytest.mark.parametrize("test_cases", [
        # Малый диапазон
        [(1, 3, ["0000 0000 0000 0001", "0000 0000 0000 0002", "0000 0000 0000 0003"])],
        # Диапазон с переходом через разряд
        [(9998, 10002, [
            "0000 0000 0000 9998",
            "0000 0000 0000 9999",
            "0000 0000 0001 0000",
            "0000 0000 0001 0001",
            "0000 0000 0001 0002"
        ])],
        # Один номер
        [(42, 42, ["0000 0000 0000 0042"])],
        # Максимальное значение
        [(9999999999999999, 9999999999999999, ["9999 9999 9999 9999"])],
    ])
    def test_card_number_generator_correct_numbers(self, test_cases: List[Tuple]):
        """
        Параметризованный тест 3: Проверяет правильность генерации номеров в различных диапазонах.
        """
        for start, end, expected_numbers in test_cases:
            generator = card_number_generator(start, end)
            for expected in expected_numbers:
                assert next(generator) == expected

    @pytest.mark.parametrize("number, expected", [
        (1, "0000 0000 0000 0001"),
        (123, "0000 0000 0000 0123"),
        (1234, "0000 0000 0000 1234"),
        (12345, "0000 0000 0001 2345"),
        (12345678, "0000 0000 1234 5678"),
        (123456789012, "0000 1234 5678 9012"),
    ])
    def test_leading_zeros_for_different_numbers(self, number: int, expected: str):
        """Параметризованный тест: Проверка ведущих нулей для разных чисел."""
        generator = card_number_generator(number, number)
        assert next(generator) == expected

    @pytest.mark.parametrize("start, end", [
        (1, 1),
        (100, 100),
        (9999, 9999),
    ])
    def test_stop_iteration_after_completion(self, start: int, end: int):
        """Параметризованный тест: Проверяет StopIteration после завершения."""
        generator = card_number_generator(start, end)
        next(generator)

        with pytest.raises(StopIteration):
            next(generator)