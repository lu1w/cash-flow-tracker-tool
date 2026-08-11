from enum import StrEnum


class CategoryResolver(StrEnum):
    RULES = "rules"
    EMBEDDING = "embedding"
    MANUAL = "manual"


if __name__ == "__main__":
    print(CategoryResolver.RULES)
