# cash-flow-tracker-tool

For personal usage of cashflow records analysis and visualization, based on reports generated from payment apps.

## Getting Started For Developments

<!-- FIXME: switch dependency/venv management from pip + requirements.txt to uv -->

1. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```
2. Install required dependencies
   ```
   pip install -r requirements.txt
   ```
3. Add new dependencies
   ```
   pip install <package-name>
   ```
4. Update requirement.txt
   ```
   pip freeze > requirements.txt
   ```
5. Run the project
   ```
   python -m src.main
   ```

## Flow

1. Parse the account-specific report files to account-monthly-files with pre-defined columns in CSV
   1. Load data from account's CSV/Excel/etc file
   2. Populate column values, with the help of categorizers to handle complex logic to assign cashflow category
2. Combine the account-monthly-files of each and every accounts into one all-accounts-monthly-file
3. Combine the all-accounts-monthly-file to yearly-files
4. Generate monthly analyses based on the all-accounts-monthly-files
5. Generate yearly analyses based on the yearly-files

## Project Structure

- `src/main.py`
  - The entry point of the program
- `src/parser/`
  - The entry point of the parsing stage
- `src/parse_strategy/`
  - Utilizing the Strategy Design Pattern to parse CSV/Excel/etc. files that're formatted differently for different accounts
  - All strategy inherits from `parse_strategy_base.py`
- `src/categorizer/`
  - The categorizers called by parsing strategies, used for determining the category of each cashflow entry

# Testing

Run from root directory:

```
pytest
```

Print stdout for all tests, including successful tests: `pytest -s`

Print test names to terminal: `pytest -o log_cli=true`
