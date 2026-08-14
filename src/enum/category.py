from enum import Enum, auto


class Category(Enum):
    @property
    def name(self):
        name = self._name_.replace('_AND_', '_&_')
        return ' '.join(name.title().split('_'))


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
    TRANSPORTATION = auto()
    TELECOMMUNICATION = auto()
    DELIVERY = auto()

    GOVERNMENT_SERVICE = auto()
    TAX = auto()
    LIVING = auto()
    HEALTH = auto()

    PERSONAL_GROWTH = auto()
    CAREER = auto()
    HOBBIES = auto()

    FITNESS = auto()
    FOOD = auto()
    ELECTRONICS = auto()
    STATIONERY = auto()
    CLOTHING_AND_ACCESSORIES = auto()
    BEAUTY = auto()
    ENTERTAINMENT = auto()

    GIFT = auto()

    def __repr__(self):
        return super().__repr__()


if __name__ == "__main__":
    print(CategoryOutflow.UNKNOWN)
    print(repr(CategoryOutflow.TAX))
    print(CategoryOutflow.TAX)
    print(CategoryOutflow.ENTERTAINMENT.name)
    print(CategoryOutflow.CLOTHING_AND_ACCESSORIES.name)
    print(CategoryOutflow.GOVERNMENT_SERVICE.name)
