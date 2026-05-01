from pandas import DataFrame


class Analyzer:
    def filter_by_category(self, category: str) -> DataFrame | str:
        """
        Filters transactions by status (e.g., 'Completed', 'Pending').
        """
        if self.data is not None:
            return self.data[self.data[AlipayColumns.CATEGORY] == category]
        return "No data loaded."

    def total_spent(self) -> float:
        """
        Calculates the total amount spent (assuming negative values are expenses).
        """
        if self.data is not None:
            return float(self.data[self.data["Amount"] < 0]["Amount"].sum())
        return 0.0

    def total_received(self) -> float:
        """
        Calculates the total amount received (positive values).
        """
        if self.data is not None:
            return float(self.data[self.data['Amount'] > 0]['Amount'].sum())
        return 0.0
