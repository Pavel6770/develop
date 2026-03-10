import pytest
from datetime import datetime
from typing import List, Dict, Any

from src.processing import filter_by_state, sort_by_date


class TestFilterByState:
    """Класс с тестами для функции фильтрации по статусу."""

    # Тестирование фильтрации по статусу EXECUTED (по умолчанию)
    def test_filter_by_default_state(self) -> None:
        """Тестирование фильтрации со статусом по умолчанию (EXECUTED)."""
        operations: List[Dict[str, Any]] = [
            {"id": 1, "state": "EXECUTED", "amount": 100},
            {"id": 2, "state": "CANCELED", "amount": 200},
            {"id": 3, "state": "EXECUTED", "amount": 300},
            {"id": 4, "state": "PENDING", "amount": 400},
            {"id": 5, "state": "EXECUTED", "amount": 500},
        ]

        expected: List[Dict[str, Any]] = [
            {"id": 1, "state": "EXECUTED", "amount": 100},
            {"id": 3, "state": "EXECUTED", "amount": 300},
            {"id": 5, "state": "EXECUTED", "amount": 500},
        ]

        result = filter_by_state(operations)
        assert result == expected
        assert len(result) == 3

    # Параметризованные тесты для различных значений статуса
    @pytest.mark.parametrize(
        "operations,state,expected",
        [
            # Фильтрация по статусу EXECUTED
            (
                [
                    {"id": 1, "state": "EXECUTED", "date": "2024-01-01"},
                    {"id": 2, "state": "CANCELED", "date": "2024-01-02"},
                    {"id": 3, "state": "EXECUTED", "date": "2024-01-03"},
                ],
                "EXECUTED",
                [
                    {"id": 1, "state": "EXECUTED", "date": "2024-01-01"},
                    {"id": 3, "state": "EXECUTED", "date": "2024-01-03"},
                ],
            ),
            # Фильтрация по статусу CANCELED
            (
                [
                    {"id": 1, "state": "EXECUTED", "date": "2024-01-01"},
                    {"id": 2, "state": "CANCELED", "date": "2024-01-02"},
                    {"id": 3, "state": "CANCELED", "date": "2024-01-03"},
                    {"id": 4, "state": "EXECUTED", "date": "2024-01-04"},
                ],
                "CANCELED",
                [
                    {"id": 2, "state": "CANCELED", "date": "2024-01-02"},
                    {"id": 3, "state": "CANCELED", "date": "2024-01-03"},
                ],
            ),
            # Фильтрация по статусу PENDING
            (
                [
                    {"id": 1, "state": "EXECUTED", "date": "2024-01-01"},
                    {"id": 2, "state": "CANCELED", "date": "2024-01-02"},
                    {"id": 3, "state": "PENDING", "date": "2024-01-03"},
                ],
                "PENDING",
                [
                    {"id": 3, "state": "PENDING", "date": "2024-01-03"},
                ],
            ),
            # Фильтрация по нестандартному статусу
            (
                [
                    {"id": 1, "state": "EXECUTED", "date": "2024-01-01"},
                    {"id": 2, "state": "PROCESSING", "date": "2024-01-02"},
                    {"id": 3, "state": "COMPLETED", "date": "2024-01-03"},
                    {"id": 4, "state": "PROCESSING", "date": "2024-01-04"},
                ],
                "PROCESSING",
                [
                    {"id": 2, "state": "PROCESSING", "date": "2024-01-02"},
                    {"id": 4, "state": "PROCESSING", "date": "2024-01-04"},
                ],
            ),
        ],
    )
    def test_filter_by_various_states(
        self,
        operations: List[Dict[str, Any]],
        state: str,
        expected: List[Dict[str, Any]],
    ) -> None:
        """Параметризованные тесты для различных значений статуса."""
        result = filter_by_state(operations, state)
        assert result == expected

    # Проверка работы функции при отсутствии словарей с указанным статусом
    @pytest.mark.parametrize(
        "operations,state,expected",
        [
            # Нет операций со статусом EXECUTED
            (
                [
                    {"id": 1, "state": "CANCELED", "amount": 100},
                    {"id": 2, "state": "PENDING", "amount": 200},
                    {"id": 3, "state": "CANCELED", "amount": 300},
                ],
                "EXECUTED",
                [],
            ),
            # Нет операций со статусом CANCELED
            (
                [
                    {"id": 1, "state": "EXECUTED", "amount": 100},
                    {"id": 2, "state": "PENDING", "amount": 200},
                    {"id": 3, "state": "EXECUTED", "amount": 300},
                ],
                "CANCELED",
                [],
            ),
            # Нет операций с несуществующим статусом
            (
                [
                    {"id": 1, "state": "EXECUTED", "amount": 100},
                    {"id": 2, "state": "CANCELED", "amount": 200},
                ],
                "APPROVED",
                [],
            ),
            # Пустой список операций
            (
                [],
                "EXECUTED",
                [],
            ),
        ],
    )
    def test_no_matching_state(
        self,
        operations: List[Dict[str, Any]],
        state: str,
        expected: List[Dict[str, Any]],
    ) -> None:
        """Проверка работы функции при отсутствии словарей с указанным статусом."""
        result = filter_by_state(operations, state)
        assert result == expected
        assert isinstance(result, list)
        assert len(result) == 0

    # Дополнительные тесты для граничных случаев
    @pytest.mark.parametrize(
        "operations,state,expected",
        [
            # Операции с отсутствующим ключом 'state'
            (
                [
                    {"id": 1, "state": "EXECUTED", "amount": 100},
                    {"id": 2, "amount": 200},  # Нет ключа 'state'
                    {"id": 3, "state": "EXECUTED", "amount": 300},
                    {"id": 4, "status": "EXECUTED", "amount": 400},  # Другой ключ
                ],
                "EXECUTED",
                [
                    {"id": 1, "state": "EXECUTED", "amount": 100},
                    {"id": 3, "state": "EXECUTED", "amount": 300},
                ],
            ),
            # Регистр значения status
            (
                [
                    {"id": 1, "state": "EXECUTED", "amount": 100},
                    {"id": 2, "state": "executed", "amount": 200},  # Нижний регистр
                    {"id": 3, "state": "Executed", "amount": 300},  # Смешанный регистр
                ],
                "EXECUTED",
                [
                    {"id": 1, "state": "EXECUTED", "amount": 100},
                ],
            ),
            # Значение None в статусе
            (
                [
                    {"id": 1, "state": "EXECUTED", "amount": 100},
                    {"id": 2, "state": None, "amount": 200},
                    {"id": 3, "state": "EXECUTED", "amount": 300},
                ],
                "EXECUTED",
                [
                    {"id": 1, "state": "EXECUTED", "amount": 100},
                    {"id": 3, "state": "EXECUTED", "amount": 300},
                ],
            ),
            # Пустая строка в статусе
            (
                [
                    {"id": 1, "state": "EXECUTED", "amount": 100},
                    {"id": 2, "state": "", "amount": 200},
                    {"id": 3, "state": "EXECUTED", "amount": 300},
                ],
                "EXECUTED",
                [
                    {"id": 1, "state": "EXECUTED", "amount": 100},
                    {"id": 3, "state": "EXECUTED", "amount": 300},
                ],
            ),
        ],
    )
    def test_edge_cases(
        self,
        operations: List[Dict[str, Any]],
        state: str,
        expected: List[Dict[str, Any]],
    ) -> None:
        """Тестирование граничных случаев."""
        result = filter_by_state(operations, state)
        assert result == expected

    # Тест с большим количеством операций
    def test_large_operations_list(self) -> None:
        """Тестирование фильтрации большого списка операций."""
        operations: List[Dict[str, Any]] = []

        # Создаем 1000 операций
        for i in range(1000):
            if i % 3 == 0:
                state = "EXECUTED"
            elif i % 3 == 1:
                state = "CANCELED"
            else:
                state = "PENDING"

            operations.append({"id": i, "state": state, "amount": i * 100})

        # Фильтруем по статусу EXECUTED
        result = filter_by_state(operations, "EXECUTED")

        # Проверяем, что все элементы имеют правильный статус
        assert all(item["state"] == "EXECUTED" for item in result)
        # Проверяем количество (примерно 334 элемента)
        assert len(result) == 334  # 1000 // 3 + (1 если 1000 % 3 > 0)

    # Тест на сохранение исходного порядка
    def test_preserves_original_order(self) -> None:
        """Тестирование сохранения исходного порядка элементов."""
        operations: List[Dict[str, Any]] = [
            {"id": 5, "state": "EXECUTED", "date": "2024-01-05"},
            {"id": 1, "state": "CANCELED", "date": "2024-01-01"},
            {"id": 3, "state": "EXECUTED", "date": "2024-01-03"},
            {"id": 2, "state": "EXECUTED", "date": "2024-01-02"},
            {"id": 4, "state": "CANCELED", "date": "2024-01-04"},
        ]

        expected: List[Dict[str, Any]] = [
            {"id": 5, "state": "EXECUTED", "date": "2024-01-05"},
            {"id": 3, "state": "EXECUTED", "date": "2024-01-03"},
            {"id": 2, "state": "EXECUTED", "date": "2024-01-02"},
        ]

        result = filter_by_state(operations, "EXECUTED")

        # Проверяем, что порядок соответствует исходному
        assert result == expected
        assert [item["id"] for item in result] == [5, 3, 2]

    # Тест с использованием значения по умолчанию
    def test_default_state_parameter(self) -> None:
        """Тестирование использования значения параметра state по умолчанию."""
        operations: List[Dict[str, Any]] = [
            {"id": 1, "state": "EXECUTED", "amount": 100},
            {"id": 2, "state": "CANCELED", "amount": 200},
            {"id": 3, "state": "PENDING", "amount": 300},
        ]

        # Вызов без указания state (должен использовать "EXECUTED")
        result1 = filter_by_state(operations)
        # Явное указание "EXECUTED"
        result2 = filter_by_state(operations, "EXECUTED")

        assert result1 == result2
        assert len(result1) == 1
        assert result1[0]["id"] == 1

    # Тест на неизменяемость исходного списка
    def test_does_not_modify_original(self) -> None:
        """Тестирование, что функция не изменяет исходный список."""
        original: List[Dict[str, Any]] = [
            {"id": 1, "state": "EXECUTED", "amount": 100},
            {"id": 2, "state": "CANCELED", "amount": 200},
            {"id": 3, "state": "EXECUTED", "amount": 300},
        ]

        original_copy = original.copy()

        filter_by_state(original, "EXECUTED")

        # Проверяем, что исходный список не изменился
        assert original == original_copy


class TestSortByDate:
    """Тесты для функции sort_by_date."""

    def test_sort_by_date_descending_default(self) -> None:
        """Тест сортировки по убыванию (по умолчанию)."""
        operations = [
            {'id': 1, 'date': '2023-01-01'},
            {'id': 2, 'date': '2023-03-15'},
            {'id': 3, 'date': '2023-02-10'},
        ]

        expected = [
            {'id': 2, 'date': '2023-03-15'},
            {'id': 3, 'date': '2023-02-10'},
            {'id': 1, 'date': '2023-01-01'},
        ]

        assert sort_by_date(operations) == expected

    def test_sort_by_date_ascending(self) -> None:
        """Тест сортировки по возрастанию."""
        operations = [
            {'id': 1, 'date': '2023-03-15'},
            {'id': 2, 'date': '2023-01-01'},
            {'id': 3, 'date': '2023-02-10'},
        ]

        expected = [
            {'id': 2, 'date': '2023-01-01'},
            {'id': 3, 'date': '2023-02-10'},
            {'id': 1, 'date': '2023-03-15'},
        ]

        assert sort_by_date(operations, reverse=False) == expected

    def test_sort_with_different_date_formats(self) -> None:
        """Тест сортировки с разными форматами дат."""
        operations = [
            {'id': 1, 'date': '2023-01-01T10:30:00'},
            {'id': 2, 'date': '2023-01-01T09:15:00'},
            {'id': 3, 'date': '2023-01-02'},
        ]

        expected_desc = [
            {'id': 3, 'date': '2023-01-02'},
            {'id': 1, 'date': '2023-01-01T10:30:00'},
            {'id': 2, 'date': '2023-01-01T09:15:00'},
        ]

        assert sort_by_date(operations) == expected_desc

    def test_empty_list(self) -> None:
        """Тест с пустым списком."""
        assert sort_by_date([]) == []

    def test_single_element_list(self) -> None:
        """Тест со списком из одного элемента."""
        operations = [{'id': 1, 'date': '2023-01-01'}]
        assert sort_by_date(operations) == operations

    def test_elements_with_additional_fields(self) -> None:
        """Тест с элементами, содержащими дополнительные поля."""
        operations = [
            {'id': 1, 'date': '2023-01-01', 'amount': 100, 'description': 'Payment 1'},
            {'id': 2, 'date': '2023-03-15', 'amount': 200, 'description': 'Payment 2'},
            {'id': 3, 'date': '2023-02-10', 'amount': 150, 'description': 'Payment 3'},
        ]

        expected = [
            {'id': 2, 'date': '2023-03-15', 'amount': 200, 'description': 'Payment 2'},
            {'id': 3, 'date': '2023-02-10', 'amount': 150, 'description': 'Payment 3'},
            {'id': 1, 'date': '2023-01-01', 'amount': 100, 'description': 'Payment 1'},
        ]

        assert sort_by_date(operations) == expected

    @pytest.mark.parametrize(
        "reverse,expected_order",
        [
            (True, [3, 2, 1]),   # По убыванию
            (False, [1, 2, 3]),  # По возрастанию
        ],
    )
    def test_reverse_parameter(self, reverse: bool, expected_order: List[int]) -> None:
        """Параметризованный тест для проверки параметра reverse."""
        operations = [
            {'id': 1, 'date': '2023-01-01'},
            {'id': 2, 'date': '2023-02-01'},
            {'id': 3, 'date': '2023-03-01'},
        ]

        result = sort_by_date(operations, reverse=reverse)
        result_ids = [item['id'] for item in result]

        assert result_ids == expected_order

    def test_preserves_original_order_for_equal_dates(self) -> None:
        """Тест сохранения исходного порядка для одинаковых дат."""
        operations = [
            {'id': 1, 'date': '2023-01-01'},
            {'id': 2, 'date': '2023-01-01'},
            {'id': 3, 'date': '2023-01-01'},
        ]

        # Так как сортировка стабильная, порядок должен сохраниться
        assert sort_by_date(operations) == operations

    def test_dates_from_different_years(self) -> None:
        """Тест сортировки дат из разных годов."""
        operations = [
            {'id': 1, 'date': '2023-01-01'},
            {'id': 2, 'date': '2022-12-31'},
            {'id': 3, 'date': '2024-01-01'},
            {'id': 4, 'date': '2021-06-15'},
        ]

        expected_desc = [
            {'id': 3, 'date': '2024-01-01'},
            {'id': 1, 'date': '2023-01-01'},
            {'id': 2, 'date': '2022-12-31'},
            {'id': 4, 'date': '2021-06-15'},
        ]

        expected_asc = [
            {'id': 4, 'date': '2021-06-15'},
            {'id': 2, 'date': '2022-12-31'},
            {'id': 1, 'date': '2023-01-01'},
            {'id': 3, 'date': '2024-01-01'},
        ]

        assert sort_by_date(operations) == expected_desc
        assert sort_by_date(operations, reverse=False) == expected_asc


class TestSortByDateExceptions:
    """Тесты для проверки исключительных ситуаций."""

    def test_missing_date_key(self) -> None:
        """Тест на отсутствие ключа 'date'."""
        operations = [
            {'id': 1, 'date': '2023-01-01'},
            {'id': 2, 'amount': 100},  # Нет ключа 'date'
        ]

        with pytest.raises(KeyError):
            sort_by_date(operations)

    def test_invalid_date_format(self) -> None:
        """Тест с некорректным форматом даты."""
        operations = [
            {'id': 1, 'date': '2023-01-01'},
            {'id': 2, 'date': 'invalid_date'},
        ]

        # Строковое сравнение все равно будет работать, но логически это неверно
        # В реальном проекте здесь может быть ожидаемое исключение при парсинге даты
        result = sort_by_date(operations)
        # Проверяем, что сортировка произошла (строковое сравнение)
        assert result[0]['id'] == 2  # 'invalid_date' > '2023-01-01' при строковом сравнении


if __name__ == "__main__":
    pytest.main(["-v", __file__])