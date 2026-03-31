import pytest
from typing import Any
from unittest.mock import Mock
from datetime import datetime

from src.widget import mask_account_card, get_date


@pytest.fixture
def mock_mask_account() -> Mock:
    """Фикстура, предоставляющая мок-функцию для маскировки счета."""
    return Mock(return_value="**4305")


@pytest.fixture
def mock_mask_card() -> Mock:
    """Фикстура, предоставляющая мок-функцию для маскировки карты."""
    return Mock(return_value="7000 79** **** 6361")


@pytest.fixture
def mock_mask_functions(mock_mask_account: Mock, mock_mask_card: Mock) -> tuple[Mock, Mock]:
    """Фикстура, предоставляющая обе мок-функции маскировки в виде кортежа."""
    return mock_mask_account, mock_mask_card


def test_mask_card_with_single_word_card_type(
        mock_mask_card: Mock,
        mock_mask_account: Mock
) -> None:
    """
    Тестирует маскировку карты с однословным типом (например, Visa, Maestro).
    Проверяет, что номер карты правильно замаскирован и отформатирован.
    """
    # Arrange (Подготовка)
    account_info = "Visa 7000792289606361"

    # Act (Действие)
    result = mask_account_card(
        account_info,
        mock_mask_account,
        mock_mask_card
    )

    # Assert (Проверка)
    assert result == "Visa 7000 79** **** 6361"
    mock_mask_card.assert_called_once_with("7000792289606361")
    mock_mask_account.assert_not_called()


def test_mask_card_with_multiple_word_card_type(
        mock_mask_card: Mock,
        mock_mask_account: Mock
) -> None:
    """
    Тестирует маскировку карты с многословным типом (например, Visa Platinum).
    Проверяет, что все слова типа карты сохраняются в результате.
    """
    # Arrange (Подготовка)
    account_info = "Visa Platinum 7000792289606361"

    # Act (Действие)
    result = mask_account_card(
        account_info,
        mock_mask_account,
        mock_mask_card
    )

    # Assert (Проверка)
    assert result == "Visa Platinum 7000 79** **** 6361"
    mock_mask_card.assert_called_once_with("7000792289606361")
    mock_mask_account.assert_not_called()


def test_mask_account(
        mock_mask_account: Mock,
        mock_mask_card: Mock
) -> None:
    """
    Тестирует маскировку банковского счета.
    Проверяет, что номер счета правильно замаскирован с использованием
    функции get_mask_account.
    """
    # Arrange (Подготовка)
    account_info = "Счет 73654108430135874305"

    # Act (Действие)
    result = mask_account_card(
        account_info,
        mock_mask_account,
        mock_mask_card
    )

    # Assert (Проверка)
    assert result == "Счет **4305"
    mock_mask_account.assert_called_once_with("73654108430135874305")
    mock_mask_card.assert_not_called()


def test_mask_account_card_raises_index_error_for_empty_string(
        mock_mask_account: Mock,
        mock_mask_card: Mock
) -> None:
    """
    Тестирует, что IndexError возникает при передаче пустой строки.
    Также проверяет строки, состоящие только из пробелов.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(IndexError, match="Передана пустая строка"):
        mask_account_card("", mock_mask_account, mock_mask_card)

    with pytest.raises(IndexError, match="Передана пустая строка"):
        mask_account_card("   ", mock_mask_account, mock_mask_card)

    # Verify no masking functions were called
    # Проверяем, что функции маскировки не вызывались
    mock_mask_account.assert_not_called()
    mock_mask_card.assert_not_called()


def test_mask_account_card_raises_index_error_when_no_card_number(
        mock_mask_account: Mock,
        mock_mask_card: Mock
) -> None:
    """
    Тестирует, что IndexError возникает, когда указан тип карты без номера.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(IndexError, match="Не указан номер карты"):
        mask_account_card("Visa", mock_mask_account, mock_mask_card)

    mock_mask_card.assert_not_called()
    mock_mask_account.assert_not_called()


def test_mask_account_card_raises_index_error_when_no_account_number(
        mock_mask_account: Mock,
        mock_mask_card: Mock
) -> None:
    """
    Тестирует, что IndexError возникает, когда указано "Счет" без номера.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(IndexError, match="Не указан номер счета"):
        mask_account_card("Счет", mock_mask_account, mock_mask_card)

    mock_mask_account.assert_not_called()
    mock_mask_card.assert_not_called()


@pytest.fixture
def valid_iso_date_string() -> str:
    """Фикстура, предоставляющая корректную строку с датой в формате ISO."""
    return "2024-12-25T14:30:00"


@pytest.fixture
def valid_date_only_string() -> str:
    """Фикстура, предоставляющая строку только с датой (без времени)."""
    return "2024-12-25"


@pytest.fixture
def expected_formatted_date() -> str:
    """Фикстура, предоставляющая ожидаемый форматированный результат."""
    return "25.12.2024"


def test_get_date_with_full_iso_format(
        valid_iso_date_string: str,
        expected_formatted_date: str
) -> None:
    """
    Тестирует преобразование полной ISO строки с временем.
    Проверяет, что дата правильно извлекается и форматируется.
    """
    # Act (Действие)
    result = get_date(valid_iso_date_string)

    # Assert (Проверка)
    assert result == expected_formatted_date
    assert isinstance(result, str)
    assert result.count(".") == 2  # Проверяем формат ДД.ММ.ГГГГ


def test_get_date_with_date_only_format(
        valid_date_only_string: str,
        expected_formatted_date: str
) -> None:
    """
    Тестирует преобразование строки только с датой (без времени).
    Проверяет, что функция корректно обрабатывает формат YYYY-MM-DD.
    """
    # Act (Действие)
    result = get_date(valid_date_only_string)

    # Assert (Проверка)
    assert result == expected_formatted_date
    assert len(result) == 10  # ДД.ММ.ГГГГ = 10 символов


def test_get_date_with_iso_with_zulu_format() -> None:
    """
    Тестирует преобразование ISO строки с Z (Zulu time).
    Проверяет, что символ Z корректно заменяется на +00:00.
    """
    # Arrange (Подготовка)
    iso_with_z = "2024-12-25T14:30:00Z"

    # Act (Действие)
    result = get_date(iso_with_z)

    # Assert (Проверка)
    assert result == "25.12.2024"


def test_get_date_raises_type_error_for_non_string() -> None:
    """
    Тестирует, что TypeError возникает при передаче не строкового типа.
    Проверяет обработку datetime объекта и других типов.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(TypeError, match="Ожидалась строка, получен int"):
        get_date(12345)

    with pytest.raises(TypeError, match="Ожидалась строка, получен datetime"):
        get_date(datetime(2024, 12, 25))

    with pytest.raises(TypeError, match="Ожидалась строка, получен NoneType"):
        get_date(None)


def test_get_date_raises_value_error_for_empty_string() -> None:
    """
    Тестирует, что ValueError возникает при передаче пустой строки
    или строки, состоящей только из пробелов.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(ValueError, match="не соответствует формату ISO"):
        get_date("")

    with pytest.raises(ValueError, match="не соответствует формату ISO"):
        get_date("   ")


def test_get_date_raises_value_error_for_invalid_format() -> None:
    """
    Тестирует, что ValueError возникает при передаче строки,
    не соответствующей ISO формату.
    """
    # Act & Assert (Действие и Проверка)
    with pytest.raises(ValueError, match="не соответствует формату ISO"):
        get_date("25.12.2024")

    with pytest.raises(ValueError, match="не соответствует формату ISO"):
        get_date("2024/12/25")

    with pytest.raises(ValueError, match="не соответствует формату ISO"):
        get_date("invalid-date")


def test_get_date_with_microseconds_in_iso_format() -> None:
    """
    Тестирует преобразование ISO строки с микросекундами.
    Проверяет, что функция корректно обрабатывает микросекунды.
    """
    # Arrange (Подготовка)
    iso_with_microseconds = "2024-12-25T14:30:00.123456"

    # Act (Действие)
    result = get_date(iso_with_microseconds)

    # Assert (Проверка)
    assert result == "25.12.2024"


def test_get_date_with_timezone_offset() -> None:
    """
    Тестирует преобразование ISO строки с часовым поясом.
    Проверяет, что функция корректно обрабатывает временную зону.
    """
    # Arrange (Подготовка)
    iso_with_tz = "2024-12-25T14:30:00+03:00"

    # Act (Действие)
    result = get_date(iso_with_tz)

    # Assert (Проверка)
    assert result == "25.12.2024"


if __name__ == "__main__":
    pytest.main(["-v", __file__])