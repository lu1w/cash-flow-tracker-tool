import sys
import traceback
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
from pandas import DataFrame, Series
from typing import Dict

# Support import from project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.config.config import FileConfig
from src.enum.account import Account
from src.enum.column import Column
from src.enum.currency import Currency
from src.utils.logger import logger, test_log


class ParseStrategyBase(ABC):
    # to be replaced
    account = Account.UNKNOWN
    currency = Currency.UNKNOWN
    file_extension = "REPLACE_ME"

    # optional config
    require_data_type_validation = True

    @classmethod
    @abstractmethod
    def load_data(cls, file_path: Path) -> DataFrame:
        """Read data from input file."""
        pass

    @classmethod
    @abstractmethod
    def parse_row(cls, row: Series) -> Series:
        """Core processing logic where the input data is mapped to the output data."""
        pass

    @classmethod
    def get_input_data_dir_path(cls) -> Path:
        return Path(f"{FileConfig.INPUT_DATA_DIR}/{str(cls.account.name).lower()}")

    @classmethod
    def get_parsed_data_dir_path(cls) -> Path:
        """Defines where the standardized file should be stored."""
        return Path(f"{FileConfig.STANDARDIZED_DATA_DIR}/{str(cls.account.name).lower()}")

    @classmethod
    def ensure_standardized_data_dir_path(cls) -> Path:
        standardized_dir_path = cls.get_parsed_data_dir_path()
        standardized_dir_path.mkdir(parents=True, exist_ok=True)
        return standardized_dir_path

    @classmethod
    def build_output_file_path(cls, date_key: str) -> str:
        # .data/standardized/.wechat/WECHAT(202602).csv
        return cls.ensure_standardized_data_dir_path() / f"{cls.account.name}({date_key}).csv"


if __name__ == "__main__":
    from pprint import pprint
    pprint(ParseStrategyBase.__dict__)
