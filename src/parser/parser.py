import sys
import os
import csv
from pathlib import Path
import pandas as pd
from pandas import DataFrame, Series
from typing import Dict, List

# Support import from project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.parse_strategy.parse_strategy_base import ParseStrategyBase
from src.models.input_model import InputModel
from src.models.transaction_entry_model import TransactionEntryModel
from src.utils.logger import logger, debug_log
from src.enum.column import Column


class Parser:
    def __init__(self, parse_strategy: ParseStrategyBase):
        self.parse_strategy = parse_strategy

    def _process_file(self, file_path: Path) -> None:
        try:
            # Load data
            logger.info(f"Start loading data for file `{file_path}`")
            data_entries: List[InputModel] = self.parse_strategy.load_data(file_path)

            logger.info(f"Data loaded, start parsing file `{file_path}`")

            # Parse data
            parsed_data_entries: List[TransactionEntryModel] = [self.parse_strategy.parse_entry(entry)
                                                                for entry in data_entries]

            # Group data based on the year and month
            monthly_cashflows: Dict[str, list[TransactionEntryModel]] = {}
            for entry in parsed_data_entries:
                year_month_key = f"{entry.date.year:4}-{entry.date.month:02}"
                if year_month_key in monthly_cashflows:
                    monthly_cashflows[year_month_key].append(entry)
                else:
                    monthly_cashflows[year_month_key] = [entry]

            # Writ data to monthly fileentry
            fieldnames = [
                # potentialy cleaner version: model_json_schema()['properties'] extracts the aliases automatically
                # fieldnames = list(UserProfile.model_json_schema(by_alias=True)["properties"].keys())
                field.alias or name
                for name, field in TransactionEntryModel.model_fields.items()
            ]
            for year_month, entries in monthly_cashflows.items():
                monthly_file = self.parse_strategy.build_output_file_path(year_month)
                logger.info(f"Writing {len(entries)} entries to {monthly_file}")
                with open(monthly_file, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)

                    # Write the header row (id, name, price, is_available)
                    writer.writeheader()

                    # Write the rows
                    for entry in entries:
                        # .model_dump() converts the Pydantic object into a clean Python dict
                        writer.writerow(entry.model_dump(by_alias=True))
                break  # TODO(this) remove this after testing

            logger.info(f"Successfully generated monthly reports from file `{file_path}`")
        except Exception as e:
            logger.exception(f"Error in processing file `{file_path}`: {e}")

    def execute(self) -> None:
        """Get the files from the input data directory, and parse into standardized format."""

        input_data_dir_path = self.parse_strategy.get_input_data_dir_path()
        pattern = f"[!_]*.{self.parse_strategy.file_extension}"
        data_file_paths = list(input_data_dir_path.glob(pattern=pattern))

        logger.info(
            f"Start parsing files with pattern {pattern} in {os.getcwd()}/{input_data_dir_path}: \n"
            + f"{'\n'.join(['- ' + str(file_path) for file_path in data_file_paths])}")

        for file_path in data_file_paths:
            self._process_file(file_path)

        # TODO: combine multiple accounts together
        # TODO: generate yearly file / analysis

        logger.info(f"Successfully processed all files in {input_data_dir_path}")
