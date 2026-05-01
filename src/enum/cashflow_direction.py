
from enum import Enum


class CashflowDirection(Enum):
    UNKNOWN = ("(unknown)", 0)
    INFLOW = ("Incoming", 1)
    OUTFLOW = ("Outgoing", -1)

    def __init__(self, text: str, coefficient: int):
        self.text = text
        self.coefficient = coefficient

    # Handles: self * other
    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return self.coefficient * scalar
        raise TypeError(f"Input should be a numeric data type, but got {type(scalar)}")

    # Handles: other * self (e.g., 3 * v)
    def __rmul__(self, scalar):
        return self.__mul__(scalar)


if __name__ == "__main__":
    assert CashflowDirection.INFLOW.name == "INFLOW"
    assert CashflowDirection.INFLOW.value == ("IN", 1)
    assert CashflowDirection.INFLOW.text == "IN"

    assert CashflowDirection.INFLOW * 2 == 2
    assert CashflowDirection.OUTFLOW * 3 == -3
    assert CashflowDirection.UNKNOWN * 5 == 0
