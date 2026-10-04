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
    except ValueError:
        source_path_str = str(source_file_path)
        if source_dir not in source_path_str:
            raise ValueError(
                f"Source file path must be under {source_dir}, but has path {source_file_path}"
            )

    return destination_dir_path / relative_path
