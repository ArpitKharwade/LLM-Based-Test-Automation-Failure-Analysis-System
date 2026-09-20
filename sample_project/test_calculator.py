import pytest

from sample_project.calculator import add, calculate_average, divide


def test_add_basic():
    assert add(2, 3) == 5


def test_add_negative_values():
    assert add(-1, 5) == 4


def test_divide_basic():
    assert divide(10, 2) == 5


def test_divide_zero_raises():
    with pytest.raises(ValueError):
        divide(4, 0)


def test_calculate_average_valid():
    assert calculate_average([1, 2, 3, 4]) == 2.5


def test_calculate_average_empty_raises():
    with pytest.raises(ValueError):
        calculate_average([])
