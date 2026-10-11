
from decimal import Decimal
from enum import Enum
from pandas import Series
from typing import override

from src.utils.logger import logger

# TODO(null): maybe change this to an IntEnum


class CashflowDirection(Enum):
    UNKNOWN = ("(unknown)", 0)
    INFLOW = ("Incoming", 1)
    OUTFLOW = ("Outgoing", -1)

    def __init__(self, display_name: str, multiplier: int):
        self.display_name = display_name
        self.multiplier = multiplier

    @property
    def value(self):
        return str(self)

    def __str__(self):
        return self.display_name

    def __int__(self):
        return self.multiplier

    # Handles: self * other
    def __mul__(self, scalar):
        supported_types = (int, Decimal)
        if isinstance(scalar, supported_types):
            return Decimal(self.multiplier * scalar)
        raise TypeError(f"Input should be a type from {supported_types}, but got {type(scalar)}")

    # Handles: other * self (e.g., 3 * v)
    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    @override
    @classmethod
    def _missing_(cls, value: object):
        """Allows lookup using just the display_text value or the multiplier."""
        if isinstance(value, (str, int)):
            for member in cls:
                if value == member.value[0] or value == member.value[1]:
                    return member
        return super()._missing_(value)

    @classmethod
    def get_unknown(cls, row: Series):
        logger.warning(f"Unknown cashflow direction for row:\n{row}\n")
        return cls.UNKNOWN


if __name__ == "__main__":
    assert CashflowDirection.INFLOW.name == "INFLOW"
    assert CashflowDirection.INFLOW.value == ("Inflow", 1)
    assert CashflowDirection.INFLOW.display_name == "Inflow"

    assert CashflowDirection.INFLOW * 2 == 2
    assert CashflowDirection.OUTFLOW * 3 == -3
    assert CashflowDirection.UNKNOWN * 5 == 0
