from httpx._multipart import DataField
import sys
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Tuple
from pathlib import Path
from itertools import chain

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.analyzer.analyzer_ui import THEME_COLOURS
from src.config.config import FileConfig
from src.enum.category import Category, CategoryOutflow, CategoryInflow
from src.enum.column import Column
from src.utils.logger import logger

OUTFLOW_CATEGORIES = [item.name for item in CategoryOutflow]
INFLOW_CATEGORIES = [item.name for item in CategoryInflow]


def _get_amount_by_categories(file_path: Path) -> Tuple[Dict[Category, float], Dict[Category, float]]:
    df = pd.read_csv(file_path, encoding="utf-8")

    amount_per_category: pd.DataFrame = (
        # Getting both columns to verify the amounts are equal, since category can only be inflow or outflow;
        # only exception is "Transaction" column (same for both inflow and outflow),
        # which should have always have net amount 0, but absolute amount can be non-zero.
        df.groupby(Column.CATEGORY)[[Column.AMOUNT_NET, Column.AMOUNT_ABSOLUTE]]
        .sum()
    )

    # TODO(PL21): verify that the amount values are the same

    outflows = {category: amount_per_category.loc[category, Column.AMOUNT_ABSOLUTE]
                for category in amount_per_category.index if category != CategoryOutflow.TRANSACTION.name and category in OUTFLOW_CATEGORIES}
    inflows = {category: amount_per_category.loc[category, Column.AMOUNT_ABSOLUTE]
               for category in amount_per_category.index if category != CategoryInflow.TRANSACTION.name and category in INFLOW_CATEGORIES}

    logger.debug(inflows)
    logger.debug(outflows)

    return outflows, inflows


CATEGORY_COLOURS = {
    category.name: THEME_COLOURS[i % len(THEME_COLOURS)]
    for i, category in enumerate(chain(CategoryOutflow, CategoryInflow))
}  # TODO(AN3): category color tidy up


def _show_pie_chart_on_amount_by_categories(
        amount_by_outflow_categories: Dict[str, float],
        amount_by_inflow_categories: Dict[str, float]
):
    amounts_outflows = amount_by_outflow_categories.values()
    categories_outflows = amount_by_outflow_categories.keys()
    amounts_inflows = amount_by_inflow_categories.values()
    categories_inflows = amount_by_inflow_categories.keys()

    fig, axs = plt.subplots(2, figsize=(7, 8))
    fig.suptitle("Expenditure/Earning Distribution by Category")
    fig.tight_layout()

    def make_autopct_with_value_and_percentage(values):
        def autopct(pct):
            total = sum(values)
            val = round(pct * total / 100.0, 2)
            return f'{pct:.1f}%\n({val})'
        return autopct

    axs[0].set_title("Outflows")
    wedges, texts, autotexts = axs[0].pie(
        amounts_outflows,
        # labels=categories_outflows,
        # labeldistance=1.35,   # Pushes text labels further out
        radius=0.9,
        colors=[CATEGORY_COLOURS.get(category) for category in categories_outflows],
        autopct=make_autopct_with_value_and_percentage(amounts_outflows),
        # Formats and displays percentages automatically
        pctdistance=1.15,       # Push percentage out to avoid overlap
        startangle=90           # Rotates the start of the chart by 90 degrees
    )
    axs[0].legend(
        wedges,
        categories_outflows,
        title="Categories",
        loc="center left",
        bbox_to_anchor=(0.95, 0, 0.5, 1)  # location of the legend box on the figure
    )

    axs[1].set_title("Inflows")
    wedges, texts, autotexts = axs[1].pie(
        amounts_inflows,
        # labels=categories_inflows,
        # labeldistance=1.35,   # Pushes text labels further out
        colors=[CATEGORY_COLOURS.get(category) for category in categories_inflows],
        radius=0.9,
        autopct=make_autopct_with_value_and_percentage(amounts_inflows),
        # Formats and displays percentages automatically
        pctdistance=1.15,       # Push percentage out to avoid overlap
        startangle=90           # Rotates the start of the chart by 90 degrees
    )
    axs[1].legend(
        wedges,
        categories_inflows,
        title="Categories",
        loc="center left",
        bbox_to_anchor=(0.95, 0, 0.5, 1)
    )

    # Fine-tune spaces manually
    plt.subplots_adjust(
        left=0.10,      # Left-edge to the left-border of the leftmost plot
        right=0.70,     # Left-edge to the right-border of the rightmost plot
        bottom=0.05,    # Bottom-edge to the bottom-border of the bottommost plot
        top=0.85,       # Bottom-edge to the top-border of the upmost plot
        wspace=0.10,    # Width padding between subplots (fraction of axes width)
        hspace=0.10     # Height padding between subplots (fraction of axes height)
    )

    # TODO(AN5): Maybe save the graph to avoid generating the same graph again (since historical data won't change)?
    # plt.savefig('account_balance.png', dpi=300, bbox_inches='tight')

    plt.show()


def get_pie_chart_on_amount_by_categories_by_month():
    output_monthly_dir_path = Path(f"{FileConfig.OUTPUT_DATA_MONTHLY_DIR}")

    monthly_cashflow_file_path = output_monthly_dir_path / Path("2025-06.csv")
    amount_by_outflow_categories, amount_by_inflow_categories = _get_amount_by_categories(monthly_cashflow_file_path)
    _show_pie_chart_on_amount_by_categories(amount_by_outflow_categories, amount_by_inflow_categories)


def get_pie_chart_on_amount_by_categories_by_year(year: str):
    # TODO(AN6): Aggregate the data per month, and display the yearly summary;
    #   can just concatenant the CSV file, and call _display_pie_chart_on_amount_by_categories directly on the yearly file,
    #   or dynamically aggregates the data from monthly file
    output_monthly_dir_path = Path(f"{FileConfig.OUTPUT_DATA_MONTHLY_DIR}")

    month_cashflow_file_paths = list(output_monthly_dir_path.glob(pattern=f"{year}*.csv"))
    yearly_amount_by_outflow_categories = {}
    yearly_amount_by_inflow_categories = {}

    for file_path in month_cashflow_file_paths:
        amount_by_outflow_categories, amount_by_inflow_categories = _get_amount_by_categories(file_path)

        # Aggregate fow outflow
        for category, amount in amount_by_outflow_categories.items():
            yearly_amount_by_outflow_categories[category] = \
                yearly_amount_by_outflow_categories.get(category, 0) + amount

        # Aggregate for inflow
        for category, amount in amount_by_inflow_categories.items():
            yearly_amount_by_inflow_categories[category] = \
                yearly_amount_by_inflow_categories.get(category, 0) + amount

    _show_pie_chart_on_amount_by_categories(yearly_amount_by_outflow_categories, yearly_amount_by_inflow_categories)


def display_line_chart_on_accounts_balances():
    # TODO(AN8): implement a line chart that show the changes of different
    # account after support account balance tracking
    pass


if __name__ == "__main__":
    # get_pie_chart_on_amount_by_categories_by_month()
    get_pie_chart_on_amount_by_categories_by_year("2025")
