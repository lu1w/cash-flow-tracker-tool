from enum import Enum, auto


class Category(Enum):
    @property
    def name(self):
        return ' '.join(self._name_.title().split('_'))


class CategoryInflow(Category):
    UNKNOWN = 0
    TRANSACTION = auto()
    SALARY = auto()
    GIFT = auto()
    INTEREST = auto()
    CASH_REBATE = auto()
    PART_TIME_JOB = auto()
    REFUND = auto()  # means there should be human intervene to revert the original expenditure


class CategoryOutflow(Category):
    UNKNOWN = 0
    TRANSACTION = auto()

    HOUSING = auto()
    FURNITURE_APPLIANCES = auto()
    BILL = auto()
    TRANSPORTATION = auto()
    TELECOMMUNICATION = auto()
    DELIVERY = auto()

    GOVERNMENT_SERVICE = auto()
    TAX = auto()
    LIVING = auto()
    HEALTH = auto()

    EDUCATION = auto()
    CAREER_GROWTH = auto()
    HOBBIES = auto()

    FITNESS = auto()
    FOOD = auto()
    ELECTRONICS = auto()
    STATIONERY = auto()
    APPAREL = auto()
    BEAUTY = auto()
    ENTERTAINMENT = auto()

    GIFT = auto()

    def __repr__(self):
        return super().__repr__()


if __name__ == "__main__":
    print(repr(CategoryOutflow.TAX))
    print(CategoryOutflow.TAX)
    print(CategoryOutflow.DAILY_NECESSITY.name)
