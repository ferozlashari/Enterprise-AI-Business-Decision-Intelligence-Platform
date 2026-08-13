
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Copilot Service
Intent-Aware Enterprise AI Copilot
Analytics-First Architecture

Author : Feroz Ali
=========================================================
"""

import logging
import threading

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from backend.orchestrator.orchestrator import (
    EnterpriseOrchestrator
)

from backend.services.prediction_service import (
    PredictionService
)

from rag.rag_manager import (
    RAGManager
)


logger = logging.getLogger(
    "CopilotService"
)


class CopilotService:

    # =====================================================
    # SINGLETON
    # =====================================================

    _instance = None

    _lock = threading.Lock()

    _orchestrator = None

    _rag = None

    # =====================================================
    # SUPPORTED BUSINESS INTENTS
    # =====================================================

    INTENTS = (
        "SALES",
        "INVENTORY",
        "FORECAST",
        "CUSTOMER",
        "RISK",
        "DECISION",
        "EXECUTIVE",
    )

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __new__(cls):

        if cls._instance is None:

            with cls._lock:

                if cls._instance is None:

                    cls._instance = super(
                        CopilotService,
                        cls
                    ).__new__(cls)

        return cls._instance

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        if getattr(
            self,
            "_initialized",
            False
        ):

            return

        with CopilotService._lock:

            try:

                # -------------------------------------------------
                # Enterprise Orchestrator
                # -------------------------------------------------

                if CopilotService._orchestrator is None:

                    logger.info(
                        "Loading Enterprise Orchestrator..."
                    )

                    CopilotService._orchestrator = (
                        EnterpriseOrchestrator()
                    )

                # -------------------------------------------------
                # Enterprise RAG
                # -------------------------------------------------

                if CopilotService._rag is None:

                    logger.info(
                        "Loading Enterprise RAG..."
                    )

                    CopilotService._rag = RAGManager

                self.orchestrator = (
                    CopilotService._orchestrator
                )

                self.rag = (
                    CopilotService._rag
                )

                self._initialized = True

                logger.info(
                    "CopilotService initialized successfully"
                )

            except Exception:

                logger.exception(
                    "Copilot initialization failed"
                )

                raise

    # =====================================================
    # NORMALIZE QUESTION
    # =====================================================

    @staticmethod
    def normalize_question(
        question: str
    ) -> str:

        return str(
            question or ""
        ).strip()

    # =====================================================
    # INTENT DETECTION
    # =====================================================

    @classmethod
    def detect_intent(
        cls,
        question: str
    ) -> str:

        q = (
            question
            .lower()
            .strip()
        )

        # =================================================
        # INVENTORY
        # =================================================

        inventory_keywords = (

            "inventory",
            "stock",
            "stocks",
            "warehouse",
            "warehouses",
            "reorder",
            "re-order",
            "restock",
            "safety stock",
            "stockout",
            "stock out",
            "out of stock",
            "overstock",
            "understock",
            "inventory risk",
            "inventory level",
            "inventory levels",
            "available stock",
            "current stock",
            "stock level",
            "stock levels",
            "inventory demand",
        )

        if any(
            keyword in q
            for keyword in inventory_keywords
        ):

            return "INVENTORY"

        # =================================================
        # FORECAST
        # =================================================

        forecast_keywords = (

            "forecast",
            "forecasting",
            "future sales",
            "future demand",
            "predicted sales",
            "predicted demand",
            "prediction",
            "predict",
            "next month",
            "next quarter",
            "next year",
            "expected sales",
            "expected demand",
            "sales outlook",
            "demand outlook",
            "trend projection",
            "projected sales",
            "projected demand",
        )

        if any(
            keyword in q
            for keyword in forecast_keywords
        ):

            return "FORECAST"

        # =================================================
        # CUSTOMER
        # =================================================

        customer_keywords = (

            "customer",
            "customers",
            "client",
            "clients",
            "customer value",
            "valuable customer",
            "valuable customers",
            "customer segment",
            "customer segmentation",
            "customer retention",
            "customer churn",
            "churn",
            "customer lifetime",
            "customer behavior",
            "customer loyalty",
            "customer profitability",
        )

        if any(
            keyword in q
            for keyword in customer_keywords
        ):

            return "CUSTOMER"

        # =================================================
        # DECISION
        # =================================================

        decision_keywords = (

            "decision",
            "decisions",
            "recommend",
            "recommendation",
            "recommendations",
            "what should we",
            "what should i",
            "should we",
            "should management",
            "prioritize",
            "priority",
            "priorities",
            "action plan",
            "actions",
            "strategy",
            "strategic",
            "optimize",
            "optimization",
            "improve",
            "improvement",
            "what do you recommend",
            "how should we",
        )

        if any(
            keyword in q
            for keyword in decision_keywords
        ):

            return "DECISION"

        # =================================================
        # RISK
        # =================================================

        risk_keywords = (

            "risk",
            "risks",
            "business risk",
            "business risks",
            "financial risk",
            "financial risks",
            "operational risk",
            "operational risks",
            "loss",
            "losses",
            "negative profit",
            "declining",
            "decline",
            "danger",
            "threat",
            "warning",
            "critical issue",
            "critical issues",
            "problem",
            "problems",
        )

        if any(
            keyword in q
            for keyword in risk_keywords
        ):

            return "RISK"

        # =================================================
        # SALES
        # =================================================

        sales_keywords = (

            "sales",
            "sale",
            "revenue",
            "profit",
            "profits",
            "product",
            "products",
            "category",
            "categories",
            "top product",
            "top products",
            "best product",
            "best products",
            "top category",
            "top categories",
            "best category",
            "best categories",
            "selling",
            "sold",
            "order",
            "orders",
            "region",
            "regions",
            "market",
            "markets",
            "sales performance",
            "sales trend",
            "sales trends",
            "discount",
            "discounts",
            "margin",
            "margins",
        )

        if any(
            keyword in q
            for keyword in sales_keywords
        ):

            return "SALES"

        # =================================================
        # EXECUTIVE
        # =================================================

        executive_keywords = (

            "executive",
            "management",
            "leadership",
            "ceo",
            "cfo",
            "board",
            "quarter",
            "quarterly",
            "business overview",
            "executive summary",
            "company performance",
            "overall performance",
            "overall business",
            "enterprise overview",
            "business priorities",
        )

        if any(
            keyword in q
            for keyword in executive_keywords
        ):

            return "EXECUTIVE"

        return "EXECUTIVE"

    # =====================================================
    # INTENT DESCRIPTION
    # =====================================================

    @staticmethod
    def get_intent_description(
        intent: str
    ) -> str:

        descriptions = {

            "SALES":
                "Sales performance, revenue, profit, products, categories, regions and discounts.",

            "INVENTORY":
                "Inventory levels, stock risk, warehouses, reorder points and stock demand.",

            "FORECAST":
                "Future sales, demand predictions, trends and forecast risks.",

            "CUSTOMER":
                "Customer value, segmentation, retention, churn and customer behavior.",

            "RISK":
                "Business, financial and operational risks.",

            "DECISION":
                "Strategic recommendations, actions, optimization and business decisions.",

            "EXECUTIVE":
                "Enterprise-wide business performance and management priorities.",
        }

        return descriptions.get(
            intent,
            descriptions["EXECUTIVE"]
        )

    # =====================================================
    # FIND SALES DATA
    # =====================================================

    @staticmethod
    def get_sales_dataframe():

        """
        Load the generated sales prediction dataset.

        This is preferred over RAG because structured
        numerical questions must use the actual dataset.
        """

        candidates = [

            PredictionService.OUTPUT_DIR
            / "sales_predictions.csv",

            PredictionService.OUTPUT_DIR
            / "sales_prediction.csv",

            PredictionService.OUTPUT_DIR
            / "superstore_predictions.csv",

        ]

        for file in candidates:

            try:

                if file.exists():

                    df = pd.read_csv(
                        file
                    )

                    if not df.empty:

                        logger.info(
                            "Copilot loaded sales analytics: %s | rows=%s",
                            file,
                            len(df)
                        )

                        return df

            except Exception as error:

                logger.warning(
                    "Unable to load sales file %s: %s",
                    file,
                    error
                )

        return pd.DataFrame()

    # =====================================================
    # SAFE NUMBER
    # =====================================================

    @staticmethod
    def safe_float(
        value,
        default=0.0
    ):

        try:

            if pd.isna(value):

                return default

            return float(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            return default

    # =====================================================
    # SALES ANALYTICS
    # =====================================================

    def sales_analytics(
        self,
        question: str
    ):

        """
        Answer structured sales questions directly
        from enterprise sales data.

        RAG is NOT used as the source of truth here.
        """

        df = self.get_sales_dataframe()

        # -------------------------------------------------
        # Fallback to sales_summary.json
        # -------------------------------------------------

        if df.empty:

            summary = (
                PredictionService
                .get_sales_prediction()
            )

            return {

                "status":
                    "success",

                "analytics_source":
                    "sales_summary.json",

                "answer":
                    self.format_sales_summary(
                        summary
                    ),

                "data":
                    summary

            }

        # -------------------------------------------------
        # Normalize columns
        # -------------------------------------------------

        if "Sales" in df.columns:

            df["Sales"] = pd.to_numeric(
                df["Sales"],
                errors="coerce"
            ).fillna(0)

        if "Profit" in df.columns:

            df["Profit"] = pd.to_numeric(
                df["Profit"],
                errors="coerce"
            ).fillna(0)

        # =================================================
        # TOP CATEGORIES
        # =================================================

        category_phrases = (

            "top category",
            "top categories",
            "best category",
            "best categories",
            "performing category",
            "performing categories",
            "product categories",
            "category performance",
            "category sales",
        )

        if any(
            phrase in question.lower()
            for phrase in category_phrases
        ):

            if "Category" not in df.columns:

                return self.analytics_unavailable(
                    "Category data is not available."
                )

            result = (

                df.groupby(
                    "Category",
                    dropna=False
                )["Sales"]

                .sum()

                .sort_values(
                    ascending=False
                )

                .reset_index()
            )

            result.columns = [
                "category",
                "sales"
            ]

            result["sales"] = result[
                "sales"
            ].round(2)

            records = (
                result
                .to_dict(
                    orient="records"
                )
            )

            lines = [
                "Top performing product categories based on total sales:"
            ]

            for index, row in enumerate(
                records[:10],
                start=1
            ):

                lines.append(
                    f"{index}. "
                    f"{row['category']}: "
                    f"${row['sales']:,.2f}"
                )

            return {

                "status":
                    "success",

                "analytics_source":
                    "sales_predictions.csv",

                "analysis_type":
                    "category_performance",

                "answer":
                    "\n".join(lines),

                "data":
                    records

            }

        # =================================================
        # REGIONAL SALES
        # =================================================

        region_phrases = (

            "sales by region",
            "sales by regions",
            "regional sales",
            "region performance",
            "regional performance",
            "top region",
            "top regions",
            "best region",
            "best regions",
            "which region",
            "which regions",
        )

        if any(
            phrase in question.lower()
            for phrase in region_phrases
        ):

            if "Region" not in df.columns:

                return self.analytics_unavailable(
                    "Region data is not available."
                )

            result = (

                df.groupby(
                    "Region",
                    dropna=False
                )["Sales"]

                .sum()

                .sort_values(
                    ascending=False
                )

                .reset_index()
            )

            result.columns = [
                "region",
                "sales"
            ]

            result["sales"] = result[
                "sales"
            ].round(2)

            records = (
                result
                .to_dict(
                    orient="records"
                )
            )

            lines = [
                "Regional sales performance:"
            ]

            for index, row in enumerate(
                records,
                start=1
            ):

                lines.append(
                    f"{index}. "
                    f"{row['region']}: "
                    f"${row['sales']:,.2f}"
                )

            return {

                "status":
                    "success",

                "analytics_source":
                    "sales_predictions.csv",

                "analysis_type":
                    "regional_sales",

                "answer":
                    "\n".join(lines),

                "data":
                    records

            }

        # =================================================
        # DECLINING REGIONS
        # =================================================

        declining_phrases = (

            "declining sales",
            "declining regions",
            "declining region",
            "sales decline",
            "sales declining",
            "which regions show declining",
            "which region shows declining",
            "regions declining",
            "region declining",
        )

        if any(
            phrase in question.lower()
            for phrase in declining_phrases
        ):

            return self.find_declining_regions(
                df
            )

        # =================================================
        # TOP PRODUCTS
        # =================================================

        product_phrases = (

            "top product",
            "top products",
            "best product",
            "best products",
            "best selling product",
            "best selling products",
            "highest selling product",
            "highest selling products",
            "product performance",
            "product sales",
        )

        if any(
            phrase in question.lower()
            for phrase in product_phrases
        ):

            product_column = None

            if "Product Name" in df.columns:

                product_column = "Product Name"

            elif "Product" in df.columns:

                product_column = "Product"

            if product_column is None:

                return self.analytics_unavailable(
                    "Product-level data is not available."
                )

            result = (

                df.groupby(
                    product_column,
                    dropna=False
                )["Sales"]

                .sum()

                .sort_values(
                    ascending=False
                )

                .head(10)

                .reset_index()
            )

            result.columns = [
                "product",
                "sales"
            ]

            result["sales"] = result[
                "sales"
            ].round(2)

            records = (
                result
                .to_dict(
                    orient="records"
                )
            )

            lines = [
                "Top performing products based on total sales:"
            ]

            for index, row in enumerate(
                records,
                start=1
            ):

                lines.append(
                    f"{index}. "
                    f"{row['product']}: "
                    f"${row['sales']:,.2f}"
                )

            return {

                "status":
                    "success",

                "analytics_source":
                    "sales_predictions.csv",

                "analysis_type":
                    "product_performance",

                "answer":
                    "\n".join(lines),

                "data":
                    records

            }

        # =================================================
        # TOTAL REVENUE
        # =================================================

        revenue_phrases = (

            "total revenue",
            "total sales",
            "overall sales",
            "how much revenue",
            "how much sales",
            "revenue generated",
        )

        if any(
            phrase in question.lower()
            for phrase in revenue_phrases
        ):

            total_sales = self.safe_float(
                df["Sales"].sum()
            )

            profit = (
                self.safe_float(
                    df["Profit"].sum()
                )
                if "Profit" in df.columns
                else 0
            )

            return {

                "status":
                    "success",

                "analytics_source":
                    "sales_predictions.csv",

                "analysis_type":
                    "sales_summary",

                "answer":
                    (
                        f"Total recorded sales revenue is "
                        f"${total_sales:,.2f}."
                        f"\nTotal recorded profit is "
                        f"${profit:,.2f}."
                        f"\nTotal sales records: "
                        f"{len(df):,}."
                    ),

                "data": {

                    "total_sales":
                        total_sales,

                    "profit":
                        profit,

                    "records":
                        len(df)

                }

            }

        # =================================================
        # SALES TREND
        # =================================================

        trend_phrases = (

            "sales trend",
            "sales trends",
            "monthly sales",
            "monthly trend",
            "sales over time",
            "sales history",
            "historical sales",
        )

        if any(
            phrase in question.lower()
            for phrase in trend_phrases
        ):

            if "Order Date" not in df.columns:

                return self.analytics_unavailable(
                    "Historical Order Date data is not available."
                )

            dates = pd.to_datetime(
                df["Order Date"],
                errors="coerce"
            )

            valid = df.loc[
                dates.notna()
            ].copy()

            valid["Order Date"] = dates[
                dates.notna()
            ]

            if valid.empty:

                return self.analytics_unavailable(
                    "No valid sales dates are available."
                )

            trend = (

                valid.groupby(
                    valid["Order Date"].dt.to_period("M")
                )["Sales"]

                .sum()

                .reset_index()
            )

            trend["month"] = (
                trend["Order Date"]
                .astype(str)
            )

            trend["sales"] = (
                trend["Sales"]
                .round(2)
            )

            records = trend[
                [
                    "month",
                    "sales"
                ]
            ].to_dict(
                orient="records"
            )

            lines = [
                "Historical monthly sales trend:"
            ]

            for row in records:

                lines.append(
                    f"{row['month']}: "
                    f"${row['sales']:,.2f}"
                )

            return {

                "status":
                    "success",

                "analytics_source":
                    "sales_predictions.csv",

                "analysis_type":
                    "sales_trend",

                "answer":
                    "\n".join(lines),

                "data":
                    records

            }

        # =================================================
        # GENERAL SALES SUMMARY
        # =================================================

        total_sales = self.safe_float(
            df["Sales"].sum()
        )

        profit = (

            self.safe_float(
                df["Profit"].sum()
            )

            if "Profit" in df.columns

            else 0
        )

        return {

            "status":
                "success",

            "analytics_source":
                "sales_predictions.csv",

            "analysis_type":
                "general_sales",

            "answer":
                (
                    f"Enterprise sales analysis found "
                    f"{len(df):,} records with total sales "
                    f"of ${total_sales:,.2f} and recorded "
                    f"profit of ${profit:,.2f}."
                ),

            "data": {

                "records":
                    len(df),

                "total_sales":
                    total_sales,

                "profit":
                    profit

            }

        }

    # =====================================================
    # FIND DECLINING REGIONS
    # =====================================================

    def find_declining_regions(
        self,
        df
    ):

        if df.empty:

            return self.analytics_unavailable(
                "No sales data is available."
            )

        if (
            "Region" not in df.columns
            or "Order Date" not in df.columns
        ):

            return {

                "status":
                    "insufficient_data",

                "answer":
                    (
                        "I cannot reliably determine "
                        "declining regions because both "
                        "Region and historical Order Date "
                        "data are required."
                    ),

                "data":
                    []

            }

        work = df.copy()

        work["Order Date"] = pd.to_datetime(
            work["Order Date"],
            errors="coerce"
        )

        work["Sales"] = pd.to_numeric(
            work["Sales"],
            errors="coerce"
        ).fillna(0)

        work = work.dropna(
            subset=[
                "Order Date",
                "Region"
            ]
        )

        if work.empty:

            return {

                "status":
                    "insufficient_data",

                "answer":
                    (
                        "There is not enough valid "
                        "historical regional sales data "
                        "to determine declining regions."
                    ),

                "data":
                    []

            }

        # -------------------------------------------------
        # Monthly regional sales
        # -------------------------------------------------

        monthly = (

            work.groupby(
                [
                    "Region",
                    work["Order Date"].dt.to_period("M")
                ]
            )["Sales"]

            .sum()

            .reset_index()
        )

        monthly.columns = [
            "Region",
            "Month",
            "Sales"
        ]

        results = []

        for region, group in monthly.groupby(
            "Region"
        ):

            group = group.sort_values(
                "Month"
            )

            if len(group) < 2:

                continue

            first_sales = self.safe_float(
                group.iloc[0]["Sales"]
            )

            latest_sales = self.safe_float(
                group.iloc[-1]["Sales"]
            )

            change = (
                latest_sales
                - first_sales
            )

            if first_sales != 0:

                change_pct = (
                    change
                    / first_sales
                    * 100
                )

            else:

                change_pct = 0

            # -------------------------------------------------
            # Declining = latest < earliest
            # -------------------------------------------------

            if change < 0:

                results.append({

                    "region":
                        str(region),

                    "first_month":
                        str(group.iloc[0]["Month"]),

                    "latest_month":
                        str(group.iloc[-1]["Month"]),

                    "first_sales":
                        round(
                            first_sales,
                            2
                        ),

                    "latest_sales":
                        round(
                            latest_sales,
                            2
                        ),

                    "change":
                        round(
                            change,
                            2
                        ),

                    "change_percent":
                        round(
                            change_pct,
                            2
                        )

                })

        results.sort(
            key=lambda x:
                x["change_percent"]
        )

        # -------------------------------------------------
        # No declining regions
        # -------------------------------------------------

        if not results:

            return {

                "status":
                    "success",

                "analytics_source":
                    "sales_predictions.csv",

                "analysis_type":
                    "declining_regions",

                "answer":
                    (
                        "No declining regions were detected "
                        "when comparing the earliest and latest "
                        "available monthly sales for each region."
                    ),

                "data":
                    []

            }

        # -------------------------------------------------
        # Format response
        # -------------------------------------------------

        lines = [
            "Regions showing declining sales based on the earliest versus latest available monthly sales:"
        ]

        for index, item in enumerate(
            results,
            start=1
        ):

            lines.append(

                f"{index}. "
                f"{item['region']}: "
                f"${item['first_sales']:,.2f} → "
                f"${item['latest_sales']:,.2f} "
                f"({item['change_percent']:.2f}%)"

            )

        return {

            "status":
                "success",

            "analytics_source":
                "sales_predictions.csv",

            "analysis_type":
                "declining_regions",

            "answer":
                "\n".join(lines),

            "data":
                results

        }

    # =====================================================
    # SALES SUMMARY FALLBACK
    # =====================================================

    @staticmethod
    def format_sales_summary(
        summary
    ):

        if not isinstance(
            summary,
            dict
        ):

            return (
                "Sales analytics data is currently unavailable."
            )

        revenue = (
            summary.get(
                "total_sales",
                summary.get(
                    "Revenue",
                    0
                )
            )
        )

        profit = (
            summary.get(
                "profit",
                summary.get(
                    "Profit",
                    0
                )
            )
        )

        return (

            "Sales analytics summary:\n"
            f"Revenue: ${float(revenue):,.2f}\n"
            f"Profit: ${float(profit):,.2f}"

        )

    # =====================================================
    # ANALYTICS UNAVAILABLE
    # =====================================================

    @staticmethod
    def analytics_unavailable(
        message
    ):

        return {

            "status":
                "analytics_unavailable",

            "answer":
                message,

            "data":
                []

        }

    # =====================================================
    # INVENTORY ANALYTICS
    # =====================================================

    def inventory_analytics(
        self,
        question
    ):

        try:

            result = (
                PredictionService
                .get_inventory_prediction()
            )

            if not result:

                return {

                    "status":
                        "analytics_unavailable",

                    "answer":
                        (
                            "Inventory analytics data "
                            "is currently unavailable."
                        ),

                    "data":
                        {}

                }

            inventory_records = (
                result.get(
                    "inventory",
                    []
                )
            )

            return {

                "status":
                    "success",

                "analytics_source":
                    "inventory_predictions.csv",

                "analysis_type":
                    "inventory",

                "answer":
                    (
                        f"Inventory prediction data contains "
                        f"{result.get('records', len(inventory_records)):,} "
                        f"records."
                    ),

                "data":
                    result

            }

        except Exception as error:

            logger.exception(
                "Inventory analytics failed"
            )

            return {

                "status":
                    "analytics_error",

                "answer":
                    "Unable to load inventory analytics.",

                "message":
                    str(error),

                "data":
                    {}

            }

    # =====================================================
    # CUSTOMER ANALYTICS
    # =====================================================

    def customer_analytics(
        self,
        question
    ):

        try:

            result = (
                PredictionService
                .get_customer_segments()
            )

            if not result:

                return {

                    "status":
                        "analytics_unavailable",

                    "answer":
                        (
                            "Customer segmentation data "
                            "is currently unavailable."
                        ),

                    "data":
                        {}

                }

            segments = result.get(
                "customer_segments",
                []
            )

            lines = [
                "Customer segmentation analysis:"
            ]

            for segment in segments:

                lines.append(

                    f"{segment.get('segment', 'Unknown')}: "
                    f"{segment.get('customers', 0):,} customers"

                )

            return {

                "status":
                    "success",

                "analytics_source":
                    "customer_segments.csv",

                "analysis_type":
                    "customer_segmentation",

                "answer":
                    "\n".join(lines),

                "data":
                    result

            }

        except Exception as error:

            logger.exception(
                "Customer analytics failed"
            )

            return {

                "status":
                    "analytics_error",

                "answer":
                    "Unable to load customer analytics.",

                "message":
                    str(error),

                "data":
                    {}

            }

    # =====================================================
    # FORECAST ANALYTICS
    # =====================================================

    def forecast_analytics(
        self,
        question
    ):

        try:

            result = (
                PredictionService
                .get_forecast()
            )

            if not result:

                return {

                    "status":
                        "analytics_unavailable",

                    "answer":
                        (
                            "Forecast analytics data "
                            "is currently unavailable."
                        ),

                    "data":
                        {}

                }

            forecast_records = result.get(
                "forecast",
                []
            )

            return {

                "status":
                    "success",

                "analytics_source":
                    "sales_forecast.csv",

                "analysis_type":
                    "forecast",

                "answer":
                    (
                        f"Forecast model: "
                        f"{result.get('model', 'Unknown')}\n"
                        f"Forecast records available: "
                        f"{result.get('records', len(forecast_records)):,}."
                    ),

                "data":
                    result

            }

        except Exception as error:

            logger.exception(
                "Forecast analytics failed"
            )

            return {

                "status":
                    "analytics_error",

                "answer":
                    "Unable to load forecast analytics.",

                "message":
                    str(error),

                "data":
                    {}

            }

    # =====================================================
    # SAFE RAG
    # =====================================================

    def safe_rag_ask(
        self,
        question: str,
        intent: str
    ):

        try:

            rag_question = (

                f"Business domain: {intent}\n"

                f"Domain description: "
                f"{self.get_intent_description(intent)}\n\n"

                f"User business question:\n"
                f"{question}\n\n"

                "IMPORTANT:\n"
                "Use only evidence actually present "
                "in the retrieved enterprise documents. "
                "Do not invent regions, categories, sales "
                "values, trends, customers, or forecasts."

            )

            result = self.rag.ask(
                rag_question
            )

            if isinstance(
                result,
                dict
            ):

                return result

            if isinstance(
                result,
                str
            ):

                return {

                    "status":
                        "success",

                    "answer":
                        result,

                    "context":
                        ""

                }

            return {

                "status":
                    "success",

                "answer":
                    str(result),

                "context":
                    ""

            }

        except Exception as error:

            logger.warning(
                "RAG failed for %s: %s",
                intent,
                error
            )

            return {

                "status":
                    "rag_unavailable",

                "answer":
                    "",

                "context":
                    "",

                "message":
                    str(error)

            }

    # =====================================================
    # SAFE BUSINESS ORCHESTRATOR
    # =====================================================

    def safe_business_analysis(
        self,
        question: str,
        intent: str
    ):

        try:

            enriched_question = (

                f"Business Intent: {intent}\n"

                f"Business Domain: "
                f"{self.get_intent_description(intent)}\n\n"

                f"User Question:\n"
                f"{question}"

            )

            result = self.orchestrator.chat(
                enriched_question
            )

            return result

        except Exception as error:

            logger.exception(
                "Business analysis failed for %s",
                intent
            )

            return {

                "status":
                    "business_analysis_unavailable",

                "answer":
                    "",

                "message":
                    str(error)

            }

    # =====================================================
    # STRUCTURED ANALYTICS ROUTER
    # =====================================================

    def run_structured_analytics(
        self,
        question,
        intent
    ):

        """
        Structured enterprise analytics has priority
        over RAG for numerical/business-data questions.
        """

        try:

            if intent == "SALES":

                return self.sales_analytics(
                    question
                )

            if intent == "INVENTORY":

                return self.inventory_analytics(
                    question
                )

            if intent == "CUSTOMER":

                return self.customer_analytics(
                    question
                )

            if intent == "FORECAST":

                return self.forecast_analytics(
                    question
                )

            return None

        except Exception as error:

            logger.exception(
                "Structured analytics failed"
            )

            return {

                "status":
                    "analytics_error",

                "answer":
                    "Structured business analytics failed.",

                "message":
                    str(error)

            }

    # =====================================================
    # COMBINE RESPONSE
    # =====================================================

    def build_final_response(
        self,
        question,
        intent,
        analytics_result,
        business_result,
        rag_result
    ):

        if not isinstance(
            rag_result,
            dict
        ):

            rag_result = {}

        if not isinstance(
            business_result,
            dict
        ):

            business_result = {

                "status":
                    "success",

                "answer":
                    str(
                        business_result
                    )

            }

        # -------------------------------------------------
        # Analytics-first response
        # -------------------------------------------------

        if isinstance(
            analytics_result,
            dict
        ):

            analytics_answer = (
                analytics_result.get(
                    "answer",
                    ""
                )
            )

            analytics_status = (
                analytics_result.get(
                    "status",
                    ""
                )
            )

            if analytics_answer and analytics_status in (
                "success",
                "insufficient_data",
                "analytics_unavailable",
            ):

                return {

                    "status":
                        "success",

                    "question":
                        question,

                    "intent":
                        intent,

                    "intent_description":
                        self.get_intent_description(
                            intent
                        ),

                    # Frontend-friendly answer
                    "answer":
                        analytics_answer,

                    # Structured analytics
                    "analytics":
                        analytics_result,

                    # Keep compatibility
                    "business_analysis":
                        analytics_result,

                    # RAG becomes supporting evidence
                    "rag_insight":
                        {

                            "answer":
                                rag_result.get(
                                    "answer",
                                    ""
                                ),

                            "context":
                                rag_result.get(
                                    "context",
                                    ""
                                ),

                            "rag_status":
                                rag_result.get(
                                    "status",
                                    "inactive"
                                )

                        },

                    "source":
                        [

                            analytics_result.get(
                                "analytics_source",
                                "Enterprise Analytics"
                            ),

                            "Enterprise ML Models",

                            "FAISS Knowledge Base",

                            "Groq LLM"

                        ]

                }

        # -------------------------------------------------
        # General AI response
        # -------------------------------------------------

        business_answer = (
            business_result.get(
                "answer",
                ""
            )
        )

        rag_answer = (
            rag_result.get(
                "answer",
                ""
            )
        )

        final_answer = (
            business_answer
            or rag_answer
            or
            "Insufficient business data available."
        )

        return {

            "status":
                "success",

            "question":
                question,

            "intent":
                intent,

            "intent_description":
                self.get_intent_description(
                    intent
                ),

            "answer":
                final_answer,

            "analytics":
                None,

            "business_analysis":
                business_result,

            "rag_insight":
                {

                    "answer":
                        rag_answer,

                    "context":
                        rag_result.get(
                            "context",
                            ""
                        ),

                    "rag_status":
                        rag_result.get(
                            "status",
                            "active"
                        )

                },

            "source":
                [

                    "LangGraph Multi-Agent System",

                    "FAISS Knowledge Base",

                    "Groq LLM"

                ]

        }

    # =====================================================
    # ASK COPILOT
    # =====================================================

    def ask(
        self,
        question: str
    ):

        question = self.normalize_question(
            question
        )

        # -------------------------------------------------
        # Validation
        # -------------------------------------------------

        if not question:

            return {

                "status":
                    "error",

                "message":
                    "Question cannot be empty."

            }

        # -------------------------------------------------
        # Intent
        # -------------------------------------------------

        intent = self.detect_intent(
            question
        )

        logger.info(
            "Copilot Intent: %s | Question: %s",
            intent,
            question
        )

        try:

            # =================================================
            # FIRST PRIORITY:
            # STRUCTURED ENTERPRISE ANALYTICS
            # =================================================

            analytics_result = (
                self.run_structured_analytics(
                    question,
                    intent
                )
            )

            # -------------------------------------------------
            # If structured analytics produced a real answer,
            # do NOT allow RAG to replace it.
            # -------------------------------------------------

            if (
                isinstance(
                    analytics_result,
                    dict
                )
                and analytics_result.get(
                    "answer"
                )
                and analytics_result.get(
                    "status"
                ) in (
                    "success",
                    "insufficient_data",
                    "analytics_unavailable",
                )
            ):

                # RAG is only supporting evidence.
                with ThreadPoolExecutor(
                    max_workers=1
                ) as executor:

                    rag_task = (
                        executor.submit(
                            self.safe_rag_ask,
                            question,
                            intent
                        )
                    )

                    rag_result = (
                        rag_task.result()
                    )

                return self.build_final_response(

                    question=
                        question,

                    intent=
                        intent,

                    analytics_result=
                        analytics_result,

                    business_result=
                        analytics_result,

                    rag_result=
                        rag_result

                )

            # =================================================
            # SECOND PRIORITY:
            # ORCHESTRATOR + RAG
            # =================================================

            with ThreadPoolExecutor(
                max_workers=2
            ) as executor:

                business_task = (
                    executor.submit(
                        self.safe_business_analysis,
                        question,
                        intent
                    )
                )

                rag_task = (
                    executor.submit(
                        self.safe_rag_ask,
                        question,
                        intent
                    )
                )

                business_result = (
                    business_task.result()
                )

                rag_result = (
                    rag_task.result()
                )

            return self.build_final_response(

                question=
                    question,

                intent=
                    intent,

                analytics_result=
                    None,

                business_result=
                    business_result,

                rag_result=
                    rag_result

            )

        except Exception as error:

            logger.exception(
                "Enterprise Copilot Failed"
            )

            return {

                "status":
                    "error",

                "message":
                    str(error),

                "question":
                    question,

                "intent":
                    intent,

                "answer":
                    "Enterprise Copilot encountered an internal error."

            }

    # =====================================================
    # HEALTH
    # =====================================================

    def health(
        self
    ):

        return {

            "service":
                "Executive AI Copilot",

            "orchestrator":
                self.orchestrator is not None,

            "rag":
                self.rag is not None,

            "analytics":
                True,

            "supported_intents":
                list(
                    self.INTENTS
                )

        }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    service = CopilotService()

    print(
        "\n========================================"
    )

    print(
        "Enterprise AI Copilot"
    )

    print(
        "========================================"
    )

    print(
        "\nHealth:"
    )

    print(
        service.health()
    )

    questions = [

        "What are our top performing product categories?",

        "Which regions show declining sales?",

        "What are our top products?",

        "What is our total revenue?",

    ]

    for question in questions:

        print(
            "\n----------------------------------------"
        )

        print(
            "QUESTION:",
            question
        )

        print(
            "----------------------------------------"
        )

        result = service.ask(
            question
        )

        print(
            result.get(
                "answer",
                result
            )
        )

