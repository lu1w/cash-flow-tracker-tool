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
    BILL = auto()
    FOOD = auto()
    TRANSPORTATION = auto()
    BEAUTY = auto()
    CLOTHING = auto()
    JEWELRY = auto()
    ENTERTAINMENT = auto()
    GIFT = auto()
    FURNITURE_APPLIANCES = auto()
    LIVING = auto()
    FITNESS = auto()
    HEALTH = auto()
    TELECOMMUNICATION = auto()
    ELECTRONICS = auto()
    DELIVERY = auto()
    GOVERNMENT_SERVICE = auto()
    STATIONERY = auto()
    EDUCATION = auto()
    CAREER_GROWTH = auto()
    TAX = auto()
    HOBBIES = auto()

    def __repr__(self):
        return super().__repr__()


if __name__ == "__main__":
    print(repr(CategoryOutflow.TAX))
    print(CategoryOutflow.TAX)
    print(CategoryOutflow.DAILY_NECESSITY.name)
