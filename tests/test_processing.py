import pytest
from datetime import datetime
from typing import List, Dict, Any

from src.processing import filter_by_state, sort_by_date


# Fixtures for common test data
@pytest.fixture
def sample_operations() -> List[Dict[str, Any]]:
    """Fixture providing a sample list of operations with various states."""
    return [
        {"id": 1, "state": "EXECUTED", "amount": 100, "date": "2024-01-01"},
        {"id": 2, "state": "CANCELED", "amount": 200, "date": "2024-01-02"},
        {"id": 3, "state": "EXECUTED", "amount": 300, "date": "2024-01-03"},
        {"id": 4, "state": "PENDING", "amount": 400, "date": "2024-01-04"},
        {"id": 5, "state": "EXECUTED", "amount": 500, "date": "2024-01-05"},
    ]


@pytest.fixture
def executed_operations() -> List[Dict[str, Any]]:
    """Fixture providing only EXECUTED operations."""
    return [
        {"id": 1, "state": "EXECUTED", "amount": 100, "date": "2024-01-01"},
        {"id": 3, "state": "EXECUTED", "amount": 300, "date": "2024-01-03"},
        {"id": 5, "state": "EXECUTED", "amount": 500, "date": "2024-01-05"},
    ]


@pytest.fixture
def canceled_operations() -> List[Dict[str, Any]]:
    """Fixture providing CANCELED operations."""
    return [
        {"id": 2, "state": "CANCELED", "amount": 200, "date": "2024-01-02"},
    ]


if __name__ == "__main__":
    pytest.main(["-v", __file__])