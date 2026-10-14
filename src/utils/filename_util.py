from pathlib import Path


def map_file_path(source_file_path: Path, source_dir: str, destination_dir: str) -> Path:
    """
    :param source_file_path: the original file path that needs to be mapped to a file under `destination_dir`
    :param source_dir: value from FileConfig
    :param destination_dir: value from FileConfig
    """
    source_dir_path = Path(source_dir)
    destination_dir_path = Path(destination_dir)

    try:
        relative_path = source_file_path.relative_to(source_dir_path)
        return destination_dir_path / relative_path
    except ValueError:
        source_path_str = str(source_file_path)
        if source_dir not in source_path_str:
            raise ValueError(
                f"Source file path must be under {source_dir}, but has path {source_file_path}"
            )
        raise


def validate_year_month_key(maybe_year_month_key: str) -> bool:
    from re import match
    pattern = r"^(\d{4})-(\d{2})$"
    if match(pattern, maybe_year_month_key):
        return True
    return False


def get_year_month_key(year: str | int, month: str | int) -> str:
    """Return year-month in the format `yyyy-mm` (e.g. `2026-09`)"""
    year_month_key = f"{year:4}-{month:02}"

    # Calling for validation here to keep the generation and the validation in sync
    if not validate_year_month_key(year_month_key):
        # TODO: maybe customize an error type
        raise ValueError(f"Invalid year_month_key {year_month_key}")

    return year_month_key
