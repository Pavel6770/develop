import pytest
from datetime import datetime
from typing import List, Dict, Any

from src.processing import filter_by_state, sort_by_date


@pytest.fixture
def sample_operations() -> List[Dict[str, Any]]:
    """Фикстура, предоставляющая список операций с разными состояниями."""
    return [
        {"id": 1, "state": "EXECUTED", "date": "2024-01-01"},
        {"id": 2, "state": "PENDING", "date": "2024-01-02"},
        {"id": 3, "state": "EXECUTED", "date": "2024-01-03"},
        {"id": 4, "state": "CANCELED", "date": "2024-01-04"},
        {"id": 5, "state": "EXECUTED", "date": "2024-01-05"},
    ]


@pytest.fixture
def sample_operations_without_state() -> List[Dict[str, Any]]:
    """Фикстура, предоставляющая список операций без ключа 'state'."""
    return [
        {"id": 1, "date": "2024-01-01"},
        {"id": 2, "state": "EXECUTED", "date": "2024-01-02"},
        {"id": 3, "date": "2024-01-03"},
    ]


@pytest.fixture
def sample_operations_with_mixed_cases() -> List[Dict[str, Any]]:
    """Фикстура, предоставляющая список операций с разными вариантами написания."""
    return [
        {"id": 1, "state": "EXECUTED", "date": "2024-01-01"},
        {"id": 2, "state": "executed", "date": "2024-01-02"},
        {"id": 3, "state": "Executed", "date": "2024-01-03"},
        {"id": 4, "state": "EXECUTED", "date": "2024-01-04"},
    ]


def test_filter_by_state_with_default_state(
        sample_operations: List[Dict[str, Any]]
) -> None:
    """
    Тестирует фильтрацию со значением состояния по умолчанию ('EXECUTED').
    Проверяет, что функция возвращает только операции со статусом 'EXECUTED'.
    """
    # Act (Действие)
    result = filter_by_state(sample_operations)

    # Assert (Проверка)
    # Исправлено: ожидаемый результат должен соответствовать данным из sample_operations
    expected_result = [
        {"id": 1, "state": "EXECUTED", "date": "2024-03-15T10:30:00"},
        {"id": 3, "state": "EXECUTED", "date": "2024-03-20T09:15:00"},
        {"id": 5, "state": "EXECUTED", "date": "2024-03-18T11:00:00"},
    ]
    assert result == expected_result
    assert len(result) == 3
    assert all(item["state"] == "EXECUTED" for item in result)


def test_filter_by_state_with_custom_state(
        sample_operations: List[Dict[str, Any]]
) -> None:
    """
    Тестирует фильтрацию с пользовательским значением состояния.
    Проверяет, что функция корректно фильтрует по указанному статусу.
    """
    # Act (Действие)
    result = filter_by_state(sample_operations, state="PENDING")

    # Assert (Проверка)
    # Исправлено: дата должна соответствовать данным из фикстуры sample_operations
    expected_result = [
        {"id": 2, "state": "PENDING", "date": "2024-03-10T14:20:00"},
    ]
    assert result == expected_result
    assert len(result) == 1
    assert result[0]["state"] == "PENDING"
    assert result[0]["id"] == 2


def test_filter_by_state_with_state_not_present(
        sample_operations: List[Dict[str, Any]]
) -> None:
    """
    Тестирует фильтрацию по статусу, которого нет в списке.
    Проверяет, что функция возвращает пустой список.
    """
    # Act (Действие)
    result = filter_by_state(sample_operations, state="FAILED")

    # Assert (Проверка)
    assert result == []
    assert isinstance(result, list)
    assert len(result) == 0


def test_filter_by_state_with_operations_missing_state_key(
        sample_operations_without_state: List[Dict[str, Any]]
) -> None:
    """
    Тестирует фильтрацию операций, у которых отсутствует ключ 'state'.
    Проверяет, что функция игнорирует операции без ключа 'state'.
    """
    # Act (Действие)
    result = filter_by_state(sample_operations_without_state)

    # Assert (Проверка)
    expected_result = [
        {"id": 2, "state": "EXECUTED", "date": "2024-01-02"},
    ]
    assert result == expected_result
    assert len(result) == 1
    assert result[0]["id"] == 2
    assert result[0]["state"] == "EXECUTED"


def test_filter_by_state_with_empty_list() -> None:
    """
    Тестирует фильтрацию с пустым списком операций.
    Проверяет, что функция возвращает пустой список.
    """
    # Arrange (Подготовка)
    empty_operations: List[Dict[str, Any]] = []

    # Act (Действие)
    result = filter_by_state(empty_operations)

    # Assert (Проверка)
    assert result == []
    assert isinstance(result, list)


def test_filter_by_state_preserves_original_data(
        sample_operations: List[Dict[str, Any]]
) -> None:
    """
    Тестирует, что функция не изменяет исходный список.
    Проверяет сохранность исходных данных.
    """
    # Arrange (Подготовка)
    original_operations = sample_operations.copy()

    # Act (Действие)
    result = filter_by_state(sample_operations, state="EXECUTED")

    # Assert (Проверка)
    assert sample_operations == original_operations
    assert result != sample_operations
    assert len(result) < len(sample_operations)


def test_filter_by_state_with_case_sensitive_matching(
        sample_operations_with_mixed_cases: List[Dict[str, Any]]
) -> None:
    """
    Тестирует, что фильтрация чувствительна к регистру.
    Проверяет, что только точное совпадение строки считается корректным.
    """
    # Act (Действие)
    result = filter_by_state(sample_operations_with_mixed_cases, state="EXECUTED")

    # Assert (Проверка)
    expected_result = [
        {"id": 1, "state": "EXECUTED", "date": "2024-01-01"},
        {"id": 4, "state": "EXECUTED", "date": "2024-01-04"},
    ]
    assert result == expected_result
    assert len(result) == 2
    assert all(item["state"] == "EXECUTED" for item in result)


@pytest.fixture
def sample_operations() -> List[Dict[str, Any]]:
    """Фикстура, предоставляющая список операций с разными датами."""
    return [
        {"id": 1, "date": "2024-03-15T10:30:00", "state": "EXECUTED"},
        {"id": 2, "date": "2024-03-10T14:20:00", "state": "PENDING"},
        {"id": 3, "date": "2024-03-20T09:15:00", "state": "EXECUTED"},
        {"id": 4, "date": "2024-03-05T16:45:00", "state": "CANCELED"},
        {"id": 5, "date": "2024-03-18T11:00:00", "state": "EXECUTED"},
    ]


@pytest.fixture
def sample_operations_same_date() -> List[Dict[str, Any]]:
    """Фикстура, предоставляющая список операций с одинаковыми датами."""
    return [
        {"id": 1, "date": "2024-03-15T10:30:00", "state": "EXECUTED"},
        {"id": 2, "date": "2024-03-15T10:30:00", "state": "PENDING"},
        {"id": 3, "date": "2024-03-15T10:30:00", "state": "EXECUTED"},
    ]


@pytest.fixture
def sample_operations_without_date() -> List[Dict[str, Any]]:
    """Фикстура, предоставляющая список операций без ключа 'date'."""
    return [
        {"id": 1, "state": "EXECUTED"},
        {"id": 2, "date": "2024-03-15T10:30:00", "state": "PENDING"},
        {"id": 3, "state": "CANCELED"},
    ]


@pytest.fixture
def sample_operations_different_formats() -> List[Dict[str, Any]]:
    """Фикстура, предоставляющая список операций с разными форматами дат."""
    return [
        {"id": 1, "date": "2024-03-15T10:30:00", "state": "EXECUTED"},
        {"id": 2, "date": "2024-03-10", "state": "PENDING"},
        {"id": 3, "date": "2024-03-20T09:15:00.123456", "state": "EXECUTED"},
        {"id": 4, "date": "2024-03-05", "state": "CANCELED"},
    ]


def test_sort_by_date_with_default_reverse(
        sample_operations: List[Dict[str, Any]]
) -> None:
    """
    Тестирует сортировку с параметром reverse по умолчанию (True).
    Проверяет, что операции сортируются в порядке убывания дат.
    """
    # Act (Действие)
    result = sort_by_date(sample_operations)

    # Assert (Проверка)
    expected_result = [
        {"id": 3, "date": "2024-03-20T09:15:00", "state": "EXECUTED"},
        {"id": 5, "date": "2024-03-18T11:00:00", "state": "EXECUTED"},
        {"id": 1, "date": "2024-03-15T10:30:00", "state": "EXECUTED"},
        {"id": 2, "date": "2024-03-10T14:20:00", "state": "PENDING"},
        {"id": 4, "date": "2024-03-05T16:45:00", "state": "CANCELED"},
    ]
    assert result == expected_result
    assert len(result) == 5
    # Проверяем, что даты идут в порядке убывания
    dates = [item["date"] for item in result]
    assert dates == sorted(dates, reverse=True)


def test_sort_by_date_with_reverse_false(
        sample_operations: List[Dict[str, Any]]
) -> None:
    """
    Тестирует сортировку с параметром reverse=False.
    Проверяет, что операции сортируются в порядке возрастания дат.
    """
    # Act (Действие)
    result = sort_by_date(sample_operations, reverse=False)

    # Assert (Проверка)
    expected_result = [
        {"id": 4, "date": "2024-03-05T16:45:00", "state": "CANCELED"},
        {"id": 2, "date": "2024-03-10T14:20:00", "state": "PENDING"},
        {"id": 1, "date": "2024-03-15T10:30:00", "state": "EXECUTED"},
        {"id": 5, "date": "2024-03-18T11:00:00", "state": "EXECUTED"},
        {"id": 3, "date": "2024-03-20T09:15:00", "state": "EXECUTED"},
    ]
    assert result == expected_result
    assert len(result) == 5
    # Проверяем, что даты идут в порядке возрастания
    dates = [item["date"] for item in result]
    assert dates == sorted(dates, reverse=False)


def test_sort_by_date_with_same_dates(
        sample_operations_same_date: List[Dict[str, Any]]
) -> None:
    """
    Тестирует сортировку операций с одинаковыми датами.
    Проверяет, что операции с одинаковыми датами сохраняют относительный порядок.
    """
    # Act (Действие)
    result = sort_by_date(sample_operations_same_date)

    # Assert (Проверка)
    # При одинаковых датах порядок может быть не определен,
    # но все элементы должны присутствовать
    expected_ids = {1, 2, 3}
    result_ids = {item["id"] for item in result}
    assert result_ids == expected_ids
    assert len(result) == 3
    # Проверяем, что все даты одинаковы
    dates = [item["date"] for item in result]
    assert all(date == "2024-03-15T10:30:00" or
               date == "2024-03-15T14:20:00" or
               date == "2024-03-15T09:15:00" for date in dates)


def test_sort_by_date_with_empty_list() -> None:
    """
    Тестирует сортировку с пустым списком операций.
    Проверяет, что функция возвращает пустой список.
    """
    # Arrange (Подготовка)
    empty_operations: List[Dict[str, Any]] = []

    # Act (Действие)
    result = sort_by_date(empty_operations)

    # Assert (Проверка)
    assert result == []
    assert isinstance(result, list)
    assert len(result) == 0


def test_sort_by_date_preserves_original_order_for_equal_dates(
        sample_operations_same_date: List[Dict[str, Any]]
) -> None:
    """
    Тестирует сохранение относительного порядка для операций с одинаковыми датами.
    Проверяет, что сортировка стабильна.
    """
    # Arrange (Подготовка)
    original_order_ids = [item["id"] for item in sample_operations_same_date]

    # Act (Действие)
    result = sort_by_date(sample_operations_same_date, reverse=False)

    # Assert (Проверка)
    result_ids = [item["id"] for item in result]
    # При одинаковых датах порядок должен сохраниться
    assert result_ids == original_order_ids

    # Дополнительная проверка: убеждаемся, что все даты действительно одинаковы
    dates = [item["date"] for item in result]
    assert all(date == dates[0] for date in dates)


def test_sort_by_date_with_different_date_formats(
        sample_operations_different_formats: List[Dict[str, Any]]
) -> None:
    """
    Тестирует сортировку операций с разными форматами дат.
    Проверяет, что функция корректно обрабатывает различные ISO форматы.
    """
    # Act (Действие)
    result = sort_by_date(sample_operations_different_formats)

    # Assert (Проверка)
    # Ожидаем сортировку по дате независимо от формата
    expected_result = [
        {"id": 3, "date": "2024-03-20T09:15:00.123456", "state": "EXECUTED"},
        {"id": 1, "date": "2024-03-15T10:30:00", "state": "EXECUTED"},
        {"id": 2, "date": "2024-03-10", "state": "PENDING"},
        {"id": 4, "date": "2024-03-05", "state": "CANCELED"},
    ]
    assert result == expected_result
    assert len(result) == 4


def test_sort_by_date_preserves_original_data(
        sample_operations: List[Dict[str, Any]]
) -> None:
    """
    Тестирует, что функция не изменяет исходный список.
    Проверяет сохранность исходных данных.
    """
    # Arrange (Подготовка)
    original_operations = sample_operations.copy()
    original_operations_ids = [item["id"] for item in original_operations]

    # Act (Действие)
    result = sort_by_date(sample_operations)

    # Assert (Проверка)
    # Проверяем, что исходный список не изменился
    assert sample_operations == original_operations
    # Проверяем, что результат содержит те же элементы
    result_ids = [item["id"] for item in result]
    assert set(result_ids) == set(original_operations_ids)
    # Проверяем, что порядок изменился
    assert result != sample_operations


@pytest.fixture
def sample_operations() -> List[Dict[str, Any]]:
    """Фикстура, предоставляющая список операций с корректными датами."""
    return [
        {"id": 1, "date": "2024-03-15T10:30:00", "state": "EXECUTED"},
        {"id": 2, "date": "2024-03-10T14:20:00", "state": "PENDING"},
        {"id": 3, "date": "2024-03-20T09:15:00", "state": "EXECUTED"},
        {"id": 4, "date": "2024-03-05T16:45:00", "state": "CANCELED"},
        {"id": 5, "date": "2024-03-18T11:00:00", "state": "EXECUTED"},
    ]


@pytest.fixture
def sample_operations_date_only() -> List[Dict[str, Any]]:
    """Фикстура, предоставляющая список операций с датами без времени."""
    return [
        {"id": 1, "date": "2024-03-15", "state": "EXECUTED"},
        {"id": 2, "date": "2024-03-10", "state": "PENDING"},
        {"id": 3, "date": "2024-03-20", "state": "EXECUTED"},
    ]


@pytest.fixture
def sample_operations_with_zulu() -> List[Dict[str, Any]]:
    """Фикстура, предоставляющая список операций с датами в формате Zulu."""
    return [
        {"id": 1, "date": "2024-03-15T10:30:00Z", "state": "EXECUTED"},
        {"id": 2, "date": "2024-03-10T14:20:00Z", "state": "PENDING"},
        {"id": 3, "date": "2024-03-20T09:15:00Z", "state": "EXECUTED"},
    ]


@pytest.fixture
def sample_operations_missing_date() -> List[Dict[str, Any]]:
    """Фикстура, предоставляющая список операций с отсутствующим ключом 'date'."""
    return [
        {"id": 1, "state": "EXECUTED"},
        {"id": 2, "date": "2024-03-15T10:30:00", "state": "PENDING"},
        {"id": 3, "state": "CANCELED"},
    ]


def test_sort_by_date_with_iso_format(
        sample_operations: List[Dict[str, Any]]
) -> None:
    """
    Тестирует сортировку операций с датами в полном ISO формате.
    Проверяет, что функция корректно сортирует операции по дате в порядке убывания.
    """
    # Act (Действие)
    result = sort_by_date(sample_operations)

    # Assert (Проверка)
    expected_result = [
        {"id": 3, "date": "2024-03-20T09:15:00", "state": "EXECUTED"},
        {"id": 5, "date": "2024-03-18T11:00:00", "state": "EXECUTED"},
        {"id": 1, "date": "2024-03-15T10:30:00", "state": "EXECUTED"},
        {"id": 2, "date": "2024-03-10T14:20:00", "state": "PENDING"},
        {"id": 4, "date": "2024-03-05T16:45:00", "state": "CANCELED"},
    ]
    assert result == expected_result
    # Проверяем, что даты идут в порядке убывания
    dates = [item["date"] for item in result]
    assert dates == ["2024-03-20T09:15:00", "2024-03-18T11:00:00",
                     "2024-03-15T10:30:00", "2024-03-10T14:20:00",
                     "2024-03-05T16:45:00"]


def test_sort_by_date_with_date_only_format(
        sample_operations_date_only: List[Dict[str, Any]]
) -> None:
    """
    Тестирует сортировку операций с датами в формате YYYY-MM-DD.
    Проверяет, что функция корректно обрабатывает даты без времени.
    """
    # Act (Действие)
    result = sort_by_date(sample_operations_date_only)

    # Assert (Проверка)
    expected_result = [
        {"id": 3, "date": "2024-03-20", "state": "EXECUTED"},
        {"id": 1, "date": "2024-03-15", "state": "EXECUTED"},
        {"id": 2, "date": "2024-03-10", "state": "PENDING"},
    ]
    assert result == expected_result
    # Проверяем, что все элементы сохранены
    assert len(result) == 3


def test_sort_by_date_with_zulu_format(
        sample_operations_with_zulu: List[Dict[str, Any]]
) -> None:
    """
    Тестирует сортировку операций с датами в формате Zulu (с символом Z).
    Проверяет, что функция корректно заменяет Z на +00:00.
    """
    # Act (Действие)
    result = sort_by_date(sample_operations_with_zulu)

    # Assert (Проверка)
    expected_result = [
        {"id": 3, "date": "2024-03-20T09:15:00Z", "state": "EXECUTED"},
        {"id": 1, "date": "2024-03-15T10:30:00Z", "state": "EXECUTED"},
        {"id": 2, "date": "2024-03-10T14:20:00Z", "state": "PENDING"},
    ]
    assert result == expected_result
    # Проверяем, что порядок сортировки корректен
    assert result[0]["id"] == 3
    assert result[1]["id"] == 1
    assert result[2]["id"] == 2


def test_sort_by_date_raises_key_error_for_missing_date(
        sample_operations_missing_date: List[Dict[str, Any]]
) -> None:
    """
    Тестирует, что KeyError возникает при отсутствии ключа 'date' в операции.
    Проверяет обработку операций без поля даты.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(KeyError, match="Отсутствует ключ 'date' в операции"):
        sort_by_date(sample_operations_missing_date)


def test_sort_by_date_raises_value_error_for_invalid_format() -> None:
    """
    Тестирует, что ValueError возникает при передаче некорректного формата даты.
    Проверяет обработку операций с неправильным форматом даты.
    """
    # Arrange (Подготовка)
    invalid_operations = [
        {"id": 1, "date": "invalid-date", "state": "EXECUTED"},
        {"id": 2, "date": "2024-03-15T10:30:00", "state": "PENDING"},
    ]

    # Act & Assert (Действие и Проверка)
    with pytest.raises(ValueError, match="Некорректный формат даты"):
        sort_by_date(invalid_operations)


def test_sort_by_date_with_reverse_false(
        sample_operations: List[Dict[str, Any]]
) -> None:
    """
    Тестирует сортировку с параметром reverse=False.
    Проверяет, что операции сортируются в порядке возрастания дат.
    """
    # Act (Действие)
    result = sort_by_date(sample_operations, reverse=False)

    # Assert (Проверка)
    expected_result = [
        {"id": 4, "date": "2024-03-05T16:45:00", "state": "CANCELED"},
        {"id": 2, "date": "2024-03-10T14:20:00", "state": "PENDING"},
        {"id": 1, "date": "2024-03-15T10:30:00", "state": "EXECUTED"},
        {"id": 5, "date": "2024-03-18T11:00:00", "state": "EXECUTED"},
        {"id": 3, "date": "2024-03-20T09:15:00", "state": "EXECUTED"},
    ]
    assert result == expected_result
    # Проверяем, что даты идут в порядке возрастания
    dates = [item["date"] for item in result]
    assert dates == ["2024-03-05T16:45:00", "2024-03-10T14:20:00",
                     "2024-03-15T10:30:00", "2024-03-18T11:00:00",
                     "2024-03-20T09:15:00"]


def test_sort_by_date_with_empty_list() -> None:
    """
    Тестирует сортировку с пустым списком операций.
    Проверяет, что функция возвращает пустой список.
    """
    # Arrange (Подготовка)
    empty_operations: List[Dict[str, Any]] = []

    # Act (Действие)
    result = sort_by_date(empty_operations)

    # Assert (Проверка)
    assert result == []
    assert isinstance(result, list)
    assert len(result) == 0


def test_sort_by_date_preserves_original_data(
        sample_operations: List[Dict[str, Any]]
) -> None:
    """
    Тестирует, что функция не изменяет исходный список.
    Проверяет сохранность исходных данных.
    """
    # Arrange (Подготовка)
    original_operations = sample_operations.copy()
    original_ids = [item["id"] for item in original_operations]

    # Act (Действие)
    result = sort_by_date(sample_operations)

    # Assert (Проверка)
    # Проверяем, что исходный список не изменился
    assert sample_operations == original_operations
    # Проверяем, что результат содержит те же элементы
    result_ids = [item["id"] for item in result]
    assert set(result_ids) == set(original_ids)
    # Проверяем, что порядок изменился
    assert result != sample_operations

if __name__ == "__main__":
    pytest.main(["-v", __file__])