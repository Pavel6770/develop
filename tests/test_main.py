import pytest

def add_numbers(a, b):
    """Функция, которую тестируем."""
    return a + b

@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add_numbers(a, b, expected):
    """Тест для функции сложения."""
    assert add_numbers(a, b) == expected
