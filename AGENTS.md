# Agent guide

Personal cash-flow tool. It turns payment-app exports (e.g. Alipay, WeChat, HSBC) into standardized CSVs, assigns categories, merges accounts by month, and charts the result. Python 3.12+, managed with `uv`.

## Pipeline

Keep stages separate. Do not fold categorizing into parsing.

1. **Preparse** (`src/parser/parser.py` `Preparser` + `PreparseStrategyBase`): raw exports under `.data/input/<account>-raw/` become CSV.
2. **Parse** (`Parser` + `ParseStrategyBase`): account CSVs become `TransactionEntryModel` rows in `.data/standardized/<account>/`.
3. **Categorize** (`src/categorizer/categorizer.py`): embedding similarity against `.data/category-reference/<account>/*.csv` writes `.data/categorized/`.
4. **Combine** (`src/combiner/combiner.py` `merge_by_month`): one monthly file across accounts in `.data/output/monthly/`.
5. **Analyze** (`src/analyzer/`): reads monthly files and charts with matplotlib. Yearly files are optional; the analyzer can aggregate on the fly.

`src/main.py` is the entry point. It currently `exit()`s after parsing, so categorizer and combiner do not run unless that call is removed. `ParserConfig.ALLOWED_YEAR_MONTH` in `src/config/config.py` filters which `yyyy-mm` keys are processed. An empty list means all months.

Active accounts: `ALL_ACTIVE_ACCOUNTS` in `src/enum/account.py` (Alipay, WeChat, HSBC HKD).

## Layout

| Path | Role |
| --- | --- |
| `src/parse_strategy/` | One strategy class per platform. New platforms subclass the base and implement `load_data` / `parse_entry`. |
| `src/parse_strategy/*_v1.py` | Older parsers. Prefer the non-`_v1` modules. Do not extend v1 unless the task is explicitly about them. |
| `src/models/` | Pydantic input models and `TransactionEntryModel`. New row fields belong on the model, with a `Column` alias. |
| `src/enum/` | `Column`, `Account`, `Category` / `CategoryInflow` / `CategoryOutflow`, `CategoryResolver`, `Currency`, `CashflowDirection`. |
| `src/cleanser/` | Marks human-edited categories as `category_resolver = manual`. |
| `src/config/config.py` | Env-backed paths and parser month filter. Loaded via `python-dotenv`. |
| `tests/` | Pytest. `conftest.py` loads `.env.test` before any production import. |

Directory names for data come from `FileConfig` and can be overridden with env vars. Defaults live under `.data/`.

## Data rules

- `.data/`, `.env`, and `*.priv*` are gitignored. They hold real transactions and keys. Do not commit them, print full rows into logs or commits, or copy private paths into tracked files.
- Tests read `tests/.test_data/` via `.env.test`. Write test output to a temp dir (`tmp_path` / monkeypatched `FileConfig`), not into fixture inputs.
- Fixture names: `data_file__<dir>_<file>` for paths, `data_models__<same suffix>` for pydantic rows. See `tests/README.md`.
- A row with `CategoryResolver.MANUAL` is human-owned. Later automatic steps must not overwrite its category. New automatic assignments use `RULES` or `EMBEDDING`, and set `category_confidence`.
- `Absolute Amount` and `Net Amount` share the same absolute value. `Net Amount` carries the sign. Aggregated rows (`Is Aggregated`) and refunded originals (`Refunded`) are excluded from spend analysis.

## Models and columns

`Column` is a `StrEnum`, so `Column.ACCOUNT == "Account"` and `.value` is unnecessary. CSV headers match those strings.

`TransactionEntryModel` field aliases match `Column` values. Construct with field names or aliases (`validate_by_name=True`). `model_dump(by_alias=True)` is what gets written to CSV. Empty strings are dropped before validation so defaults apply.

`CategoryInflow` and `CategoryOutflow` are separate enums. The same label can exist on both sides (`TRANSACTION`, `GIFT`). Do not collapse them unless the task is the category-enum redesign. Display text is the title-cased member name (`TAX` → `Tax`).

Embedding categorizer uses `Qwen/Qwen3-Embedding-0.6B` and `EMBEDDING_THRESHOLD = 0.50`. Reference CSVs need `Description` and `Category`.

## Commands

```bash
uv sync --locked
uv run python -m src.main
uv run pytest tests/
uv run pytest tests/parse_strategy_tests/test_alipay_parse_strategy.py
```

CI (`.github/workflows/ci.yml`) runs `uv sync --locked` then `uv run pytest tests/`. A lockfile mismatch should fail the install, not be papered over.

## Style

- Imports are rooted at the repo (`from src....`). Several modules append the project root to `sys.path` before those imports. Formatter ignores E402 for that pattern. Do not "fix" those imports to the top of the file.
- Format with autopep8, aggressive, line length 120 (`.vscode/settings.json`).
- Strategies are classes of classmethods, passed as types (`Parser(AlipayParseStrategy)`), not instances.
- Prefer pydantic models over raw dicts or new column enums for row shape.
- Match existing logging via `src.utils.logger`. Do not add a second logger.
- Leave `TODO` markers when touching unfinished pipeline work; do not delete them as drive-by cleanup.

## When changing behavior

- A new payment source needs an input pydantic model, a parse strategy, an `Account` member, and a test that loads a small fixture through `load_data` and `parse_entry`.
- Parsing, categorizing, and combining stay as separate steps.
- Money fields use `Decimal` on the model. Do not switch them to `float`.
- Confirm tests with `uv run pytest` on the modules you touched. Embedding tests download a model; do not require network in tests that only check parsing or models.
