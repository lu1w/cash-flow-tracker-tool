import sys
import os
import traceback
from pathlib import Path
import pandas as pd
from pandas import DataFrame, Series
from typing import Dict

# Support import from project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.parse_strategy.parse_strategy_base import ParseStrategyBase
from src.utils.logger import logger, debug_log
from src.enum.column import Column


class Parser:
    monthly_cashflow: Dict[str, DataFrame] = {}

    require_data_type_validation = True

    def __init__(self, parse_strategy: ParseStrategyBase):
        self.parse_strategy = parse_strategy

    def _process_file(self, file_path: Path) -> None:
        try:
            # Load data
            logger.info(f"Start loading data for file `{file_path}`")
            data: DataFrame = self.parse_strategy.load_data(file_path)

            logger.info(f"Data loaded, start parsing file `{file_path}`")

            # Parse data
            parsed_data: DataFrame = data.apply(self.parse_strategy.parse_row, axis=1, result_type='reduce')
            if self.parse_strategy.require_data_type_validation:
                Column.verify_columns_data_type(parsed_data)

            # Group data based on the year and month
            self.monthly_cashflow: Dict[str, DataFrame] = {
                f"{year:4}-{month:02}": row
                for (year, month), row
                in parsed_data.groupby([parsed_data['Date'].dt.year, parsed_data['Date'].dt.month])
            }

            # Writ data to monthly file
            for year_month, df in self.monthly_cashflow.items():
                df.to_csv(self.parse_strategy.build_output_file_path(year_month),
                          index=False, encoding="utf-8", mode="w")

            logger.info(f"Successfully generated monthly reports from file `{file_path}`")
        except Exception as e:
            logger.exception(f"Error in processing file `{file_path}`: {e}")

    def execute(self) -> None:
        """Get the files from the input data directory, and parse into standardized format."""

        input_data_dir_path = self.parse_strategy.get_input_data_dir_path()
        pattern = f"[!_]*.{self.parse_strategy.file_extension}"
        data_files_path = list(input_data_dir_path.glob(pattern=pattern))

        logger.info(
            f"Start parsing files with pattern {pattern} in {os.getcwd()}/{input_data_dir_path}: \n"
            + f"{'\n'.join(['- ' + str(file_path) for file_path in data_files_path])}")

        for file_path in data_files_path:
            self._process_file(file_path)

        # TODO: combine multiple accounts together
        # TODO: generate yearly file / analysis

        logger.info(f"Successfully processed all files in {input_data_dir_path}")
