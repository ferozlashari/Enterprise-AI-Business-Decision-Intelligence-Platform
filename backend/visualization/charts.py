"""
=========================================================
Enterprise AI Business Decision Intelligence Platform
Visualization Engine
Author : Feroz Ali
=========================================================
"""

from pathlib import Path
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from config.logger import get_logger

logger = get_logger("Visualization")


class ChartGenerator:

    def __init__(self):

        self.figure_dir = Path("figures")
        self.output_dir = Path("outputs")

        self.figure_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

        plt.style.use("ggplot")

    # =====================================================
    # Read CSV
    # =====================================================

    def read_csv(self, filename):

        filepath = self.output_dir / filename

        if not filepath.exists():

            logger.warning(f"{filename} not found.")

            return pd.DataFrame()

        return pd.read_csv(filepath)

    # =====================================================
    # Save Figure
    # =====================================================

    def save_figure(self, filename):

        plt.tight_layout()

        plt.savefig(
            self.figure_dir / filename,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        logger.info(f"{filename} Saved")


            # =====================================================
    # Sales Trend
    # =====================================================

    def sales_trend_chart(self):

        df = self.read_csv("sales_predictions.csv")

        if df.empty:
            return

        if "Order Date" not in df.columns:
            logger.warning("Order Date column not found.")
            return

        df["Order Date"] = pd.to_datetime(df["Order Date"])

        trend = (
            df.groupby(df["Order Date"].dt.to_period("M"))["Sales"]
            .sum()
            .reset_index()
        )

        trend["Order Date"] = trend["Order Date"].astype(str)

        plt.figure(figsize=(12, 6))

        plt.plot(
            trend["Order Date"],
            trend["Sales"],
            marker="o",
            linewidth=2
        )

        plt.xticks(rotation=45)

        plt.title("Monthly Sales Trend")

        plt.xlabel("Month")

        plt.ylabel("Sales")

        self.save_figure("sales_trend.png")


    # =====================================================
    # Top Products
    # =====================================================

    def top_products_chart(self):

        df = self.read_csv("sales_predictions.csv")

        if df.empty:
            return

        if "Product Name" not in df.columns:
            logger.warning("Product Name column not found.")
            return

        top = (
            df.groupby("Product Name")["Sales"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        plt.figure(figsize=(12, 7))

        top.sort_values().plot(kind="barh")

        plt.title("Top 10 Products by Sales")

        plt.xlabel("Sales")

        self.save_figure("top_products.png")


    # =====================================================
    # Category Sales
    # =====================================================

    def category_sales_chart(self):

        df = self.read_csv("sales_predictions.csv")

        if df.empty:
            return

        if "Category" not in df.columns:
            logger.warning("Category column not found.")
            return

        category = (
            df.groupby("Category")["Sales"]
            .sum()
            .sort_values(ascending=False)
        )

        plt.figure(figsize=(8, 8))

        plt.pie(
            category.values,
            labels=category.index,
            autopct="%1.1f%%",
            startangle=90
        )

        plt.title("Sales by Category")

        self.save_figure("category_sales.png")

            # =====================================================
    # Inventory Status
    # =====================================================

    def inventory_status_chart(self):

        df = self.read_csv("inventory_predictions.csv")

        if df.empty:
            return

        if "Inventory Status" not in df.columns:
            logger.warning("Inventory Status column not found.")
            return

        status = (
            df["Inventory Status"]
            .value_counts()
        )

        plt.figure(figsize=(8, 6))

        status.plot(
            kind="bar",
            color=["green", "orange", "red"]
        )

        plt.title("Inventory Status")

        plt.xlabel("Status")

        plt.ylabel("Count")

        self.save_figure("inventory_status.png")


    # =====================================================
    # Stock Level Distribution
    # =====================================================

    def stock_level_chart(self):

        df = self.read_csv("inventory_predictions.csv")

        if df.empty:
            return

        if "Stock Quantity" not in df.columns:
            logger.warning("Stock Quantity column not found.")
            return

        plt.figure(figsize=(10, 6))

        plt.hist(
            df["Stock Quantity"],
            bins=20
        )

        plt.title("Stock Quantity Distribution")

        plt.xlabel("Stock Quantity")

        plt.ylabel("Frequency")

        self.save_figure("stock_distribution.png")


    # =====================================================
    # Warehouse Analysis
    # =====================================================

    def warehouse_inventory_chart(self):

        df = self.read_csv("inventory_predictions.csv")

        if df.empty:
            return

        if "Warehouse" not in df.columns:
            logger.warning("Warehouse column not found.")
            return

        warehouse = (

            df.groupby("Warehouse")["Stock Quantity"]

            .sum()

            .sort_values(ascending=False)

        )

        plt.figure(figsize=(12, 6))

        warehouse.plot(kind="bar")

        plt.title("Warehouse Inventory")

        plt.xlabel("Warehouse")

        plt.ylabel("Stock Quantity")

        self.save_figure("warehouse_inventory.png")


    # =====================================================
    # Reorder Level Chart
    # =====================================================

    def reorder_level_chart(self):

        df = self.read_csv("inventory_predictions.csv")

        if df.empty:
            return

        required = [
            "Product Name",
            "Stock Quantity",
            "Reorder Level"
        ]

        if not all(col in df.columns for col in required):

            logger.warning("Required reorder columns not found.")

            return

        low_stock = df[
            df["Stock Quantity"] <= df["Reorder Level"]
        ].head(15)

        if low_stock.empty:

            logger.info("No products below reorder level.")

            return

        plt.figure(figsize=(12, 7))

        plt.barh(
            low_stock["Product Name"],
            low_stock["Stock Quantity"]
        )

        plt.title("Products Below Reorder Level")

        plt.xlabel("Current Stock")

        self.save_figure("reorder_level.png")


            # =====================================================
    # Inventory Status
    # =====================================================

    def inventory_status_chart(self):

        df = self.read_csv("inventory_predictions.csv")

        if df.empty:
            return

        if "Inventory Status" not in df.columns:
            logger.warning("Inventory Status column not found.")
            return

        status = (
            df["Inventory Status"]
            .value_counts()
        )

        plt.figure(figsize=(8, 6))

        status.plot(
            kind="bar",
            color=["green", "orange", "red"]
        )

        plt.title("Inventory Status")

        plt.xlabel("Status")

        plt.ylabel("Count")

        self.save_figure("inventory_status.png")


    # =====================================================
    # Stock Level Distribution
    # =====================================================

    def stock_level_chart(self):

        df = self.read_csv("inventory_predictions.csv")

        if df.empty:
            return

        if "Stock Quantity" not in df.columns:
            logger.warning("Stock Quantity column not found.")
            return

        plt.figure(figsize=(10, 6))

        plt.hist(
            df["Stock Quantity"],
            bins=20
        )

        plt.title("Stock Quantity Distribution")

        plt.xlabel("Stock Quantity")

        plt.ylabel("Frequency")

        self.save_figure("stock_distribution.png")


    # =====================================================
    # Warehouse Analysis
    # =====================================================

    def warehouse_inventory_chart(self):

        df = self.read_csv("inventory_predictions.csv")

        if df.empty:
            return

        if "Warehouse" not in df.columns:
            logger.warning("Warehouse column not found.")
            return

        warehouse = (

            df.groupby("Warehouse")["Stock Quantity"]

            .sum()

            .sort_values(ascending=False)

        )

        plt.figure(figsize=(12, 6))

        warehouse.plot(kind="bar")

        plt.title("Warehouse Inventory")

        plt.xlabel("Warehouse")

        plt.ylabel("Stock Quantity")

        self.save_figure("warehouse_inventory.png")


    # =====================================================
    # Reorder Level Chart
    # =====================================================

    def reorder_level_chart(self):

        df = self.read_csv("inventory_predictions.csv")

        if df.empty:
            return

        required = [
            "Product Name",
            "Stock Quantity",
            "Reorder Level"
        ]

        if not all(col in df.columns for col in required):

            logger.warning("Required reorder columns not found.")

            return

        low_stock = df[
            df["Stock Quantity"] <= df["Reorder Level"]
        ].head(15)

        if low_stock.empty:

            logger.info("No products below reorder level.")

            return

        plt.figure(figsize=(12, 7))

        plt.barh(
            low_stock["Product Name"],
            low_stock["Stock Quantity"]
        )

        plt.title("Products Below Reorder Level")

        plt.xlabel("Current Stock")

        self.save_figure("reorder_level.png")

            # =====================================================
    # Customer Segmentation
    # =====================================================

    def customer_segmentation_chart(self):

        df = self.read_csv("customer_segments.csv")

        if df.empty:
            return

        if "Cluster" not in df.columns:

            logger.warning("Cluster column not found.")

            return

        cluster = df["Cluster"].value_counts().sort_index()

        plt.figure(figsize=(8, 6))

        cluster.plot(
            kind="bar",
            color="steelblue"
        )

        plt.title("Customer Segments")

        plt.xlabel("Cluster")

        plt.ylabel("Customers")

        self.save_figure("customer_segments.png")


    # =====================================================
    # Customer Spending
    # =====================================================

    def customer_spending_chart(self):

        df = self.read_csv("customer_segments.csv")

        if df.empty:
            return

        if "Cluster" not in df.columns or "Sales" not in df.columns:

            logger.warning("Required customer columns not found.")

            return

        spending = (

            df.groupby("Cluster")["Sales"]

            .mean()

        )

        plt.figure(figsize=(8, 6))

        spending.plot(
            kind="bar",
            color="darkgreen"
        )

        plt.title("Average Customer Spending")

        plt.xlabel("Cluster")

        plt.ylabel("Average Sales")

        self.save_figure("customer_spending.png")


    # =====================================================
    # Demand Forecast
    # =====================================================

    def demand_forecast_chart(self):

        df = self.read_csv("demand_forecast.csv")

        if df.empty:
            return

        required = ["Date", "Forecast"]

        if not all(col in df.columns for col in required):

            logger.warning("Forecast columns not found.")

            return

        df["Date"] = pd.to_datetime(df["Date"])

        plt.figure(figsize=(12, 6))

        plt.plot(

            df["Date"],

            df["Forecast"],

            linewidth=2,

            marker="o"

        )

        plt.title("Demand Forecast")

        plt.xlabel("Date")

        plt.ylabel("Forecast")

        plt.xticks(rotation=45)

        self.save_figure("demand_forecast.png")


    # =====================================================
    # Revenue Forecast
    # =====================================================

    def revenue_forecast_chart(self):

        df = self.read_csv("sales_predictions.csv")

        if df.empty:
            return

        if "Predicted Sales" not in df.columns:

            logger.warning("Predicted Sales column not found.")

            return

        forecast = (

            df["Predicted Sales"]

            .head(30)

        )

        plt.figure(figsize=(12, 6))

        plt.plot(

            forecast.values,

            marker="o"

        )

        plt.title("Revenue Forecast")

        plt.xlabel("Prediction")

        plt.ylabel("Sales")

        self.save_figure("revenue_forecast.png")

            # =====================================================
    # Feature Importance
    # =====================================================

    def feature_importance_chart(self):

        df = self.read_csv("feature_importance.csv")

        if df.empty:
            return

        required = ["Feature", "Importance"]

        if not all(col in df.columns for col in required):

            logger.warning("Feature importance file not found.")

            return

        feature = (
            df.sort_values(
                "Importance",
                ascending=False
            )
            .head(15)
        )

        plt.figure(figsize=(10, 8))

        plt.barh(
            feature["Feature"],
            feature["Importance"]
        )

        plt.title("Top Feature Importance")

        plt.xlabel("Importance")

        plt.gca().invert_yaxis()

        self.save_figure("feature_importance.png")


    # =====================================================
    # Business KPI Chart
    # =====================================================

    def business_kpi_chart(self):

        report = self.output_dir / "business_kpi_report.json"

        if not report.exists():

            logger.warning("Business KPI Report not found.")

            return

        import json

        with open(report, "r") as f:

            data = json.load(f)

        keys = []
        values = []

        for key, value in data.items():

            if isinstance(value, (int, float)):

                keys.append(key)

                values.append(value)

        if len(keys) == 0:

            logger.warning("No numeric KPI found.")

            return

        plt.figure(figsize=(10, 6))

        plt.bar(
            keys,
            values
        )

        plt.xticks(rotation=45)

        plt.title("Business KPI")

        self.save_figure("business_kpi.png")


    # =====================================================
    # Generate All Charts
    # =====================================================

    def generate_all_charts(self):

        logger.info("Generating Enterprise Charts")

        self.sales_trend_chart()

        self.top_products_chart()

        self.category_sales_chart()

        self.inventory_status_chart()

        self.stock_level_chart()

        self.warehouse_inventory_chart()

        self.reorder_level_chart()

        self.customer_segmentation_chart()

        self.customer_spending_chart()

        self.demand_forecast_chart()

        self.revenue_forecast_chart()

        self.feature_importance_chart()

        self.business_kpi_chart()

        logger.info("All Charts Generated")


    # =====================================================
    # Run
    # =====================================================

    def run(self):

        print("\n========== Enterprise Visualization ==========\n")

        self.generate_all_charts()

        print("Enterprise Charts Generated Successfully")

        print(f"Figures Folder : {self.figure_dir.resolve()}")
if __name__ == "__main__":

    generator = ChartGenerator()

    generator.run()        