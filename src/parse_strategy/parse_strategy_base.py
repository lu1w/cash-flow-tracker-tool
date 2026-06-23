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
from src.utils.logger import logger, test_log
from src.enum.account import Account
from src.enum.column import Column
from src.enum.currency import Currency


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
        '''Read data from input file.'''
        pass

    @classmethod
    @abstractmethod
    def parse_row(cls, row: Series) -> Series:
        '''Core processing logic where the input data is mapped to the output data.'''
        pass

    @classmethod
    def get_data_dir_path(cls) -> Path:
        return Path(f".data/{str(cls.account.name).lower()}")

    @classmethod
    def get_output_dir_path(cls) -> Path:
        '''Defines where the output file should be stored.'''
        return Path(f".output/.{str(cls.account.name).lower()}")

    @classmethod
    def ensure_output_dir_path(cls) -> Path:
        output_dir_path = cls.get_output_dir_path()
        output_dir_path.mkdir(parents=True, exist_ok=True)
        return output_dir_path

    @classmethod
    def build_output_file_path(cls, date_key: str) -> str:
        # .output/.wechat/WECHAT(202602).csv
        return cls.ensure_output_dir_path() / f"{cls.account.name}({date_key}).csv"


if __name__ == "__main__":
    from pprint import pprint
    pprint(ParseStrategyBase.__dict__)
