# How to interact with data files

- All data files are stored as fixtures under `tests/fixtures/` directory, which must have the same file hierarchy as the actual data files 
- File name convention: `<optional-prefix-for-easier-distinction>_<type-of-data>_data.csv`
    - The type-of-data is the equivalent of the directory name of the step in the data processing pipeline, e.g. `input`, `standardized`, `output`
- If a test file requires the usage of a data file, create a fixture of the test data path, with `data_file__<optional-directory-name>_<name-of-file>` as the fixture name.
    - e.g. the test data file stored as `tests/fixtures/standardized_data_no_category.csv` maps to a fixture named `data_file_standardized_data_no_category_csv: Path`
- When creating fixture of pydantic models that represents the actual data, use naming convension `data_models__<data-file-fixture-suffix>`
    - e.g. the data that gets read from `data_file__alipay_input_data` should be named `data_models__alipay_input_data` 