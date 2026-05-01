import sys
from abc import ABC, abstractmethod
from pathlib import Path
from pandas import DataFrame, Series

# Support import from project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.utils.logger import Logger, logger
from src.enum.account import Account


class ParseStrategyBase(ABC):
    # # NOTE:
    # # cannot add @property - python 3.11 deprecated this beahvior as it causes errors for cpython https://github.com/python/mypy/issues/11619;
    # # so here we get the class attribute from a method.
    # @abstractmethod
    # def account(self) -> Account:
    #     pass

    # @abstractmethod
    # def output_dir_path(self) -> Path:
    #     pass

    @classmethod
    def process_file(cls, file_path: Path) -> None:
        data: DataFrame = cls.load_data(file_path)
        parsed_data = data.apply(cls.parse_row, axis=1, result_type='reduce')

        # write to output
        parsed_data.to_csv(cls.build_output_file_path(file_path), index=False, encoding="utf-8", mode="w")

    @classmethod
    def execute(cls) -> None:
        data_files_path = list(
            cls.data_dir_path.glob(f"*.{cls.file_extension}"))
        logger.info(f"Files to process: {[str(file_path) for file_path in data_files_path]}")

        for file_path in data_files_path:
            cls.process_file(file_path)

        # TODO: combine multiple accounts together
        # TODO: generate yearly file / analysis


if __name__ == "__main__":
    from pprint import pprint
    pprint(ParseStrategyBase.__dict__)
