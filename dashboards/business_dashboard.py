"""
=========================================================
Enterprise AI Business Decision Intelligence Platform
Business Dashboard
Author : Feroz Ali
=========================================================
"""

import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(

    page_title="Enterprise AI Dashboard",

    layout="wide"

)

REPORT_DIR = Path("reports")

OUTPUT_DIR = Path("outputs")


def load_csv(filename):

    filepath = OUTPUT_DIR / filename

    if filepath.exists():

        return pd.read_csv(filepath)

    return pd.DataFrame()


def load_json(filename):

    import json

    filepath = REPORT_DIR / filename

    if filepath.exists():

        with open(filepath, "r") as f:

            return json.load(f)

    return {}


st.title("Enterprise AI Business Decision Intelligence")

st.markdown("---")

menu = st.sidebar.selectbox(

    "Select Dashboard",

    [

        "Overview",

        "Sales",

        "Inventory",

        "Customer",

        "Reports"

    ]

)
# =====================================================
# Overview Dashboard
# =====================================================

if menu == "Overview":

    st.header("Executive Dashboard")

    sales = load_csv("sales_predictions.csv")

    inventory = load_csv("inventory_predictions.csv")

    customer = load_csv("clustered_customers.csv")

    col1, col2, col3, col4 = st.columns(4)

    total_sales = 0

    total_profit = 0

    total_orders = 0

    total_customers = 0

    if not sales.empty:

        if "Sales" in sales.columns:
            total_sales = sales["Sales"].sum()

        if "Profit" in sales.columns:
            total_profit = sales["Profit"].sum()

        total_orders = len(sales)

    if not customer.empty:
        total_customers = len(customer)

    col1.metric(
        "Total Sales",
        f"${total_sales:,.2f}"
    )

    col2.metric(
        "Total Profit",
        f"${total_profit:,.2f}"
    )

    col3.metric(
        "Orders",
        total_orders
    )

    col4.metric(
        "Customers",
        total_customers
    )

    st.markdown("---")

    left, right = st.columns(2)

    with left:

        st.subheader("Sales Dataset")

        if sales.empty:

            st.warning("No Sales Data Found")

        else:

            st.dataframe(
                sales.head(10),
                use_container_width=True
            )

    with right:

        st.subheader("Inventory Dataset")

        if inventory.empty:

            st.warning("No Inventory Data Found")

        else:

            st.dataframe(
                inventory.head(10),
                use_container_width=True
            )

    st.markdown("---")

    st.subheader("Project Information")

    st.success(
        """
        ✔ Customer Segmentation

        ✔ Sales Prediction

        ✔ Demand Forecasting

        ✔ Inventory Prediction

        ✔ Enterprise Reporting

        ✔ Business Dashboard
        """
    )

    # =====================================================
# Sales Dashboard
# =====================================================

elif menu == "Sales":

    st.header("Sales Analytics Dashboard")

    sales = load_csv("sales_predictions.csv")

    if sales.empty():

        st.warning("Sales prediction file not found.")

    else:

        st.subheader("Sales Dataset")

        st.dataframe(
            sales,
            use_container_width=True
        )

        st.markdown("---")

        col1, col2, col3 = st.columns(3)

        total_sales = 0

        avg_sales = 0

        max_sales = 0

        if "Sales" in sales.columns:

            total_sales = sales["Sales"].sum()

            avg_sales = sales["Sales"].mean()

            max_sales = sales["Sales"].max()

        col1.metric(
            "Total Sales",
            f"${total_sales:,.2f}"
        )

        col2.metric(
            "Average Sales",
            f"${avg_sales:,.2f}"
        )

        col3.metric(
            "Maximum Sale",
            f"${max_sales:,.2f}"
        )

        st.markdown("---")

        if "Category" in sales.columns and "Sales" in sales.columns:

            st.subheader("Sales by Category")

            category = (
                sales
                .groupby("Category")["Sales"]
                .sum()
                .reset_index()
            )

            st.bar_chart(
                category.set_index("Category")
            )

        if "Region" in sales.columns and "Sales" in sales.columns:

            st.subheader("Sales by Region")

            region = (
                sales
                .groupby("Region")["Sales"]
                .sum()
                .reset_index()
            )

            st.bar_chart(
                region.set_index("Region")
            )

        if "Order Date" in sales.columns and "Sales" in sales.columns:

            st.subheader("Sales Trend")

            sales["Order Date"] = pd.to_datetime(
                sales["Order Date"],
                errors="coerce"
            )

            trend = (
                sales
                .groupby("Order Date")["Sales"]
                .sum()
            )

            st.line_chart(trend)

        if "Profit" in sales.columns:

            st.subheader("Profit Distribution")

            st.area_chart(
                sales["Profit"]
            )

        if "Predicted Sales" in sales.columns:

            st.subheader("Actual vs Predicted Sales")

            compare = sales[
                ["Sales", "Predicted Sales"]
            ]

            st.line_chart(compare)


            # =====================================================
# Inventory Dashboard
# =====================================================

elif menu == "Inventory":

    st.header("Inventory Analytics Dashboard")

    inventory = load_csv("inventory_predictions.csv")

    if inventory.empty:

        st.warning("Inventory prediction file not found.")

    else:

        st.subheader("Inventory Dataset")

        st.dataframe(
            inventory,
            use_container_width=True
        )

        st.markdown("---")

        col1, col2, col3 = st.columns(3)

        total_inventory = 0

        average_inventory = 0

        max_inventory = 0

        if "Predicted Inventory" in inventory.columns:

            total_inventory = inventory[
                "Predicted Inventory"
            ].sum()

            average_inventory = inventory[
                "Predicted Inventory"
            ].mean()

            max_inventory = inventory[
                "Predicted Inventory"
            ].max()

        col1.metric(
            "Total Inventory",
            f"{total_inventory:,.0f}"
        )

        col2.metric(
            "Average Inventory",
            f"{average_inventory:,.2f}"
        )

        col3.metric(
            "Maximum Inventory",
            f"{max_inventory:,.0f}"
        )

        st.markdown("---")

        # Inventory by Category
        if (
            "Category" in inventory.columns
            and
            "Predicted Inventory" in inventory.columns
        ):

            st.subheader("Inventory by Category")

            category = (

                inventory

                .groupby("Category")["Predicted Inventory"]

                .sum()

                .reset_index()

            )

            st.bar_chart(

                category.set_index("Category")

            )

        # Inventory by Region
        if (
            "Region" in inventory.columns
            and
            "Predicted Inventory" in inventory.columns
        ):

            st.subheader("Inventory by Region")

            region = (

                inventory

                .groupby("Region")["Predicted Inventory"]

                .sum()

                .reset_index()

            )

            st.bar_chart(

                region.set_index("Region")

            )

        # Inventory Trend
        if (
            "Order Date" in inventory.columns
            and
            "Predicted Inventory" in inventory.columns
        ):

            inventory["Order Date"] = pd.to_datetime(

                inventory["Order Date"],

                errors="coerce"

            )

            trend = (

                inventory

                .groupby("Order Date")["Predicted Inventory"]

                .sum()

            )

            st.subheader("Inventory Trend")

            st.line_chart(trend)

        # Top Products
        if (
            "Product Name" in inventory.columns
            and
            "Predicted Inventory" in inventory.columns
        ):

            st.subheader("Top 10 Products")

            top_products = (

                inventory

                .sort_values(

                    "Predicted Inventory",

                    ascending=False

                )

                .head(10)

            )

            st.dataframe(

                top_products,

                use_container_width=True

            )

        # ABC Analysis
        abc_file = REPORT_DIR / "abc_analysis.csv"

        if abc_file.exists():

            st.subheader("ABC Inventory Analysis")

            abc = pd.read_csv(abc_file)

            st.dataframe(

                abc,

                use_container_width=True

            )

            # =====================================================
# Customer Dashboard
# =====================================================

elif menu == "Customer":

    st.header("Customer Segmentation Dashboard")

    customer = load_csv("clustered_customers.csv")

    if customer.empty:

        st.warning("Customer segmentation file not found.")

    else:

        st.subheader("Customer Dataset")

        st.dataframe(

            customer,

            use_container_width=True

        )

        st.markdown("---")

        col1, col2, col3 = st.columns(3)

        total_customers = len(customer)

        total_clusters = 0

        average_sales = 0

        cluster_column = None

        for col in customer.columns:

            if "cluster" in col.lower():

                cluster_column = col

                break

        if cluster_column:

            total_clusters = customer[
                cluster_column
            ].nunique()

        if "Sales" in customer.columns:

            average_sales = customer[
                "Sales"
            ].mean()

        col1.metric(

            "Customers",

            total_customers

        )

        col2.metric(

            "Clusters",

            total_clusters

        )

        col3.metric(

            "Average Sales",

            f"${average_sales:,.2f}"

        )

        st.markdown("---")

        if cluster_column:

            st.subheader("Cluster Distribution")

            cluster_df = (

                customer

                .groupby(cluster_column)

                .size()

                .reset_index(name="Customers")

            )

            st.bar_chart(

                cluster_df.set_index(cluster_column)

            )

        if (

            "Region" in customer.columns

            and cluster_column

        ):

            st.subheader("Customers by Region")

            region_df = (

                customer

                .groupby("Region")

                .size()

                .reset_index(name="Customers")

            )

            st.bar_chart(

                region_df.set_index("Region")

            )

        if (

            "Segment" in customer.columns

            and

            "Sales" in customer.columns

        ):

            st.subheader("Sales by Segment")

            segment_df = (

                customer

                .groupby("Segment")["Sales"]

                .sum()

                .reset_index()

            )

            st.bar_chart(

                segment_df.set_index("Segment")

            )

        if (

            cluster_column

            and

            "Sales" in customer.columns

        ):

            st.subheader("Average Sales per Cluster")

            cluster_sales = (

                customer

                .groupby(cluster_column)["Sales"]

                .mean()

                .reset_index()

            )

            st.line_chart(

                cluster_sales.set_index(cluster_column)

            )

        st.markdown("---")

        st.subheader("Customer Insights")

        st.success("""

✔ High Value Customers Identified

✔ Customer Segments Created

✔ Regional Distribution Available

✔ Cluster Performance Generated

✔ Enterprise Customer Analytics Ready

        """)


        # =====================================================
# Reports Dashboard
# =====================================================

elif menu == "Reports":

    st.header("Enterprise Reports")

    report_files = [

        "enterprise_model_report.json",

        "enterprise_metrics.json",

        "sales_summary.json",

        "inventory_summary.json",

        "customer_summary.json",

        "business_kpi_report.json",

        "executive_summary.json"

    ]

    for report in report_files:

        filepath = REPORT_DIR / report

        if filepath.exists():

            st.success(f"Available : {report}")

            data = load_json(report)

            if data:

                st.json(data)

            with open(filepath, "rb") as file:

                st.download_button(

                    label=f"Download {report}",

                    data=file,

                    file_name=report,

                    mime="application/json"

                )

        else:

            st.warning(f"{report} not found.")

    st.markdown("---")

    st.subheader("Enterprise Project Summary")

    st.info("""

### Enterprise AI Business Decision Intelligence Platform

**Completed Modules**

- Sales Prediction
- Inventory Prediction
- Demand Forecasting
- Customer Segmentation
- Enterprise Report Generator
- Business Dashboard

**Machine Learning Models**

- Random Forest
- Gradient Boosting
- XGBoost
- LightGBM

**Explainability**

- Feature Importance
- SHAP Analysis

**Generated Outputs**

- CSV Prediction Files
- JSON Reports
- HTML Report
- Saved Models
- KPI Dashboard

""")

    st.success("Enterprise AI Platform Ready")