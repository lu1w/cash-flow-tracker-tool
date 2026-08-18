import os
import sys
import re
import glob
import pandas as pd
from pathlib import Path
from collections import defaultdict

# Support import from project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.config.config import FileConfig
from src.enum.column import Column
from src.utils.logger import logger


def merge_by_month():
    """
    Group CSV files by the YYYY-MM pattern found in their filenames,
    and merges matching months into individual sorted files.
    """
    search_path = os.path.join(FileConfig.CATEGORIZED_DATA_DIR, '**', '*.csv')
    all_files = glob.glob(search_path, recursive=True)

    if not all_files:
        logger.error(f"No CSV files found with path '{search_path}'")
        return

    monthly_files: defaultdict[str, list[str]] = defaultdict(list)
    month_regex = re.compile(r"^.*\((20\d{2}-(?:0[1-9]|1[0-2]))\)\.csv$")

    for file_path in all_files:
        filename = os.path.basename(file_path)
        match = month_regex.search(filename)

        if match:
            yyyymm = match.group(1)
            monthly_files[yyyymm].append(file_path)
        else:
            logger.warning(f"Skipping file without `(YYYY-MM).csv` pattern in the filename: {filename}")

    # Ensure output directory exists before writing files
    os.makedirs(FileConfig.OUTPUT_DATA_MONTHLY_DIR, exist_ok=True)

    # Process each month individually
    for month_key, files in monthly_files.items():
        logger.info(f"Processing Group [{month_key}] with {len(files)} files...")
        df_list = []

        for file in files:
            try:
                df = pd.read_csv(file)
                if Column.DATE not in df.columns:
                    logger.warning(f"Column '{Column.DATE}' missing in {os.path.basename(file)}. Skipping.")
                    continue
                df_list.append(df)
            except Exception as e:
                logger.exception(f"Error reading {os.path.basename(file)}: {e}")

        if not df_list:
            logger.warning(f"No valid data for month {month_key}. Skipping compilation.")
            continue

        # Concatenate, parse dates, and sort the monthly block
        combined_df = pd.concat(df_list, ignore_index=True)
        combined_df[Column.DATE] = pd.to_datetime(
            combined_df[Column.DATE],
            format='mixed',  # `mixed` since some accounts have time information, and some doesn't
            errors='raise'  # or `coerce` to treat bad value as NaT instead of failing the script
        )
        combined_df = combined_df.sort_values(by=Column.DATE, ascending=False)

        final_filename = f"{month_key}.csv"
        final_output_path = os.path.join(FileConfig.OUTPUT_DATA_MONTHLY_DIR, final_filename)

        combined_df.to_csv(final_output_path, index=False)
        logger.info(f"Saved monthly file to: {final_output_path}")


# --- RUN EXECUTION ---
if __name__ == "__main__":
    merge_by_month()
