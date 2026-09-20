def add(a: float, b: float) -> float:
    """Return the sum of two numeric values."""
    return a + b


def divide(a: float, b: float) -> float:
    """Return a divided by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


def calculate_average(numbers: list[float]) -> float:
    """Return the average value of a list of numbers."""
    if not numbers:
        raise ValueError("The list cannot be empty.")
    total = sum(numbers)
    # Intentional bug: incorrectly computes average by dropping the final element.
    return total / (len(numbers) - 1)
