
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Enterprise Report Service

Responsible for:
- Sales Reports
- Inventory Reports
- Customer Segmentation Reports
- Forecast Reports
- KPI Reports
- Executive Summary
- Dashboard Analytics
- AI Copilot Analytics Context

Author : Feroz Ali
=========================================================
"""

from __future__ import annotations

import json
import logging
import math

from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd

from config.settings import settings


# =========================================================
# REDIS CACHE
# =========================================================

try:
    from backend.cache.decorators import redis_cache

except ImportError:

    def redis_cache(expire: int = 600):
        """
        Safe fallback when Redis/cache is unavailable.

        The fallback simply executes the original function.
        """

        def decorator(func: Callable):

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator


# =========================================================
# LOGGER
# =========================================================

logger = logging.getLogger("ReportService")


# =========================================================
# REPORT SERVICE
# =========================================================

class ReportService:
    """
    Centralized enterprise reporting service.

    Responsibilities:
        - Load generated reports
        - Normalize report structures
        - Calculate business KPIs
        - Prepare dashboard analytics
        - Prepare AI Copilot context
        - Provide frontend-friendly responses
    """

    # =====================================================
    # DIRECTORIES
    # =====================================================

    REPORT_DIR = Path(
        getattr(
            settings,
            "REPORT_DIR",
            "reports",
        )
    )

    JSON_REPORT_DIR = REPORT_DIR / "json"

    OUTPUT_DIR = Path(
        getattr(
            settings,
            "OUTPUT_DIR",
            "outputs",
        )
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    JSON_REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # =====================================================
    # GENERIC HELPERS
    # =====================================================

    @staticmethod
    def first_value(
        data: dict[str, Any],
        *keys: str,
        default: Any = None,
    ) -> Any:
        """
        Return the first non-None value from a dictionary.
        """

        if not isinstance(data, dict):
            return default

        for key in keys:

            if key in data and data[key] is not None:
                return data[key]

        return default

    # =====================================================

    @staticmethod
    def to_float(
        value: Any,
    ) -> float:
        """
        Safely convert a value to float.
        """

        try:

            if value is None:
                return 0.0

            if isinstance(value, bool):
                return float(value)

            if isinstance(value, str):

                cleaned = (
                    value
                    .replace(",", "")
                    .replace("$", "")
                    .replace("%", "")
                    .strip()
                )

                if not cleaned:
                    return 0.0

                value = cleaned

            result = float(value)

            if not math.isfinite(result):
                return 0.0

            return result

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):

            return 0.0

    # =====================================================

    @staticmethod
    def to_int(
        value: Any,
    ) -> int:
        """
        Safely convert a value to integer.
        """

        try:

            if value is None:
                return 0

            if isinstance(value, bool):
                return int(value)

            if isinstance(value, str):

                value = (
                    value
                    .replace(",", "")
                    .strip()
                )

                if not value:
                    return 0

            result = float(value)

            if not math.isfinite(result):
                return 0

            return int(result)

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):

            return 0

    # =====================================================

    @staticmethod
    def safe_round(
        value: Any,
        digits: int = 2,
    ) -> float:
        """
        Safely round numeric values.
        """

        return round(
            ReportService.to_float(value),
            digits,
        )

    # =====================================================

    @staticmethod
    def utc_now_iso() -> str:
        """
        Return timezone-aware UTC timestamp.
        """

        return datetime.now(
            timezone.utc
        ).isoformat()

    # =====================================================

    @staticmethod
    def _json_safe(
        value: Any,
    ) -> Any:
        """
        Convert pandas/numpy/datetime objects into
        JSON-compatible values.

        Also converts NaN and Infinity to None.
        """

        if value is None:
            return None

        if isinstance(value, dict):

            return {
                str(key): ReportService._json_safe(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple, set)):

            return [
                ReportService._json_safe(item)
                for item in value
            ]

        if isinstance(
            value,
            (
                pd.Timestamp,
                datetime,
            ),
        ):

            if isinstance(value, datetime):

                if value.tzinfo is None:
                    value = value.replace(
                        tzinfo=timezone.utc
                    )

                return value.isoformat()

            return value.isoformat()

        if isinstance(value, pd.Timedelta):
            return str(value)

        if hasattr(value, "item"):

            try:

                return ReportService._json_safe(
                    value.item()
                )

            except Exception:
                pass

        if isinstance(value, float):

            if not math.isfinite(value):
                return None

            return value

        return value

    # =====================================================
    # READ JSON REPORT
    # =====================================================

    @staticmethod
    def read_report(
        filename: str,
    ) -> Any:
        """
        Read a JSON report from supported report directories.

        Search order:

            1. REPORT_DIR / filename
            2. REPORT_DIR / json / filename
            3. reports / filename
            4. reports / json / filename
        """

        try:

            if not filename:
                return {}

            filename_path = Path(filename)

            paths = [
                ReportService.REPORT_DIR / filename_path,
                ReportService.JSON_REPORT_DIR / filename_path,
                Path("reports") / filename_path,
                Path("reports/json") / filename_path,
            ]

            file_path: Optional[Path] = None

            for path in paths:

                if path.exists() and path.is_file():

                    file_path = path
                    break

            if file_path is None:

                logger.warning(
                    "Missing report: %s",
                    filename,
                )

                return {}

            with file_path.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            # -------------------------------------------------
            # Handle wrapped reports
            # -------------------------------------------------

            if isinstance(data, dict):

                nested_data = data.get("data")

                if isinstance(
                    nested_data,
                    dict,
                ):

                    return nested_data

                nested_report = data.get("report")

                if isinstance(
                    nested_report,
                    dict,
                ):

                    return nested_report

            return data

        except json.JSONDecodeError:

            logger.exception(
                "Invalid JSON report: %s",
                filename,
            )

            return {}

        except (
            OSError,
            TypeError,
            ValueError,
        ):

            logger.exception(
                "Report read failed: %s",
                filename,
            )

            return {}

        except Exception:

            logger.exception(
                "Unexpected report read failure: %s",
                filename,
            )

            return {}

    # =====================================================
    # SERVICE HEALTH
    # =====================================================

    @staticmethod
    def health() -> dict[str, Any]:
        """
        Return Report Service health information.
        """

        return {
            "service": "Report Service",
            "status": "healthy",

            "directory": str(
                ReportService.REPORT_DIR
            ),

            "json_directory": str(
                ReportService.JSON_REPORT_DIR
            ),

            "output_directory": str(
                ReportService.OUTPUT_DIR
            ),

            "reports_directory_exists":
                ReportService.REPORT_DIR.exists(),

            "json_directory_exists":
                ReportService.JSON_REPORT_DIR.exists(),

            "output_directory_exists":
                ReportService.OUTPUT_DIR.exists(),
        }

    # =====================================================
    # SALES REPORT
    # =====================================================

    @staticmethod
    @redis_cache(expire=600)
    def sales_report() -> dict[str, Any]:
        """
        Generate normalized sales report.
        """

        data = ReportService.read_report(
            "sales_summary.json"
        )

        if not isinstance(data, dict):
            data = {}

        # -------------------------------------------------
        # CORE SALES VALUES
        # -------------------------------------------------

        revenue = ReportService.first_value(
            data,
            "total_sales",
            "Total Sales",
            "Total Revenue",
            "Revenue",
            "revenue",
            default=0,
        )

        profit = ReportService.first_value(
            data,
            "profit",
            "Profit",
            "Total Profit",
            "Estimated Profit",
            default=0,
        )

        prediction = ReportService.first_value(
            data,
            "prediction",
            "Prediction",
            "Predicted Sales",
            "predicted_sales",
            default=0,
        )

        growth = ReportService.first_value(
            data,
            "growth",
            "Growth",
            "growth_rate",
            "Growth Rate",
            default=0,
        )

        # -------------------------------------------------
        # SALES TREND
        # -------------------------------------------------

        sales_trend = ReportService.first_value(
            data,
            "sales_trend",
            "Sales Trend",
            "trend",
            "monthly_sales",
            "monthly_revenue",
            default=[],
        )

        if not isinstance(
            sales_trend,
            list,
        ):
            sales_trend = []

        fixed_sales_trend = []

        for index, item in enumerate(
            sales_trend
        ):

            if not isinstance(item, dict):
                continue

            month = ReportService.first_value(
                item,
                "month",
                "date",
                "Date",
                "period",
                "Period",
                "category",
                "name",
                default=f"Period {index + 1}",
            )

            sales_value = ReportService.first_value(
                item,
                "sales",
                "Sales",
                "value",
                "revenue",
                "Revenue",
                default=0,
            )

            fixed_sales_trend.append(
                {
                    "month": str(month),
                    "sales":
                        ReportService.safe_round(
                            sales_value
                        ),
                }
            )

        # -------------------------------------------------
        # CATEGORY SALES
        # -------------------------------------------------

        category_sales = ReportService.first_value(
            data,
            "category_sales",
            "Category Sales",
            default=[],
        )

        if not isinstance(
            category_sales,
            list,
        ):
            category_sales = []

        fixed_category_sales = []

        for item in category_sales:

            if not isinstance(item, dict):
                continue

            category = ReportService.first_value(
                item,
                "Category",
                "category",
                "name",
                default="Unknown",
            )

            sales_value = ReportService.first_value(
                item,
                "Sales",
                "sales",
                "value",
                "revenue",
                default=0,
            )

            fixed_category_sales.append(
                {
                    "category": str(category),
                    "sales":
                        ReportService.safe_round(
                            sales_value
                        ),
                }
            )

        # -------------------------------------------------
        # REGION SALES
        # -------------------------------------------------

        region_sales = ReportService.first_value(
            data,
            "region_sales",
            "Region Sales",
            default=[],
        )

        if not isinstance(
            region_sales,
            list,
        ):
            region_sales = []

        fixed_region_sales = []

        for item in region_sales:

            if not isinstance(item, dict):
                continue

            region = ReportService.first_value(
                item,
                "Region",
                "region",
                "name",
                default="Unknown",
            )

            sales_value = ReportService.first_value(
                item,
                "Sales",
                "sales",
                "value",
                "revenue",
                default=0,
            )

            fixed_region_sales.append(
                {
                    "region": str(region),
                    "sales":
                        ReportService.safe_round(
                            sales_value
                        ),
                }
            )

        # -------------------------------------------------
        # NORMALIZE CORE VALUES
        # -------------------------------------------------

        revenue = ReportService.to_float(
            revenue
        )

        profit = ReportService.to_float(
            profit
        )

        prediction = ReportService.to_float(
            prediction
        )

        growth = ReportService.to_float(
            growth
        )

        # -------------------------------------------------
        # RECORD COUNT
        # -------------------------------------------------

        records = ReportService.to_int(
            ReportService.first_value(
                data,
                "records",
                "Records",
                "count",
                "Count",
                "total_records",
                default=0,
            )
        )

        # -------------------------------------------------
        # DERIVED METRICS
        # -------------------------------------------------

        average_sales = (
            revenue / records
            if records > 0
            else 0.0
        )

        profit_margin = (
            (profit / revenue) * 100
            if revenue > 0
            else 0.0
        )

        forecast_difference = (
            prediction - revenue
        )

        forecast_difference_percent = (
            (
                forecast_difference / revenue
            ) * 100
            if revenue > 0
            else 0.0
        )

        # -------------------------------------------------
        # BEST CATEGORY
        # -------------------------------------------------

        best_category = "N/A"

        if fixed_category_sales:

            best_category = max(
                fixed_category_sales,
                key=lambda item:
                    ReportService.to_float(
                        item.get(
                            "sales",
                            0,
                        )
                    ),
            ).get(
                "category",
                "N/A",
            )

        # -------------------------------------------------
        # BEST REGION
        # -------------------------------------------------

        best_region = "N/A"

        if fixed_region_sales:

            best_region = max(
                fixed_region_sales,
                key=lambda item:
                    ReportService.to_float(
                        item.get(
                            "sales",
                            0,
                        )
                    ),
            ).get(
                "region",
                "N/A",
            )

        # -------------------------------------------------
        # FINAL REPORT
        # -------------------------------------------------

        result = {
            **data,

            "status": data.get(
                "status",
                "success",
            ),

            "revenue": round(
                revenue,
                2,
            ),

            "total_sales": round(
                revenue,
                2,
            ),

            "profit": round(
                profit,
                2,
            ),

            "profit_margin": round(
                profit_margin,
                2,
            ),

            "prediction": round(
                prediction,
                2,
            ),

            "predicted_sales": round(
                prediction,
                2,
            ),

            "growth": round(
                growth,
                2,
            ),

            "growth_rate": round(
                growth,
                2,
            ),

            "average_sales": round(
                average_sales,
                2,
            ),

            "records": records,

            "forecast_difference": round(
                forecast_difference,
                2,
            ),

            "forecast_difference_percent":
                round(
                    forecast_difference_percent,
                    2,
                ),

            "best_category":
                best_category,

            "best_region":
                best_region,

            "sales_trend":
                fixed_sales_trend,

            "category_sales":
                fixed_category_sales,

            "region_sales":
                fixed_region_sales,
        }

        return ReportService._json_safe(
            result
        )

    # =====================================================
    # INVENTORY REPORT
    # =====================================================

    @staticmethod
    @redis_cache(expire=600)
    def inventory_report() -> dict[str, Any]:
        """
        Generate normalized inventory report.
        """

        data = ReportService.read_report(
            "inventory_summary.json"
        )

        if not isinstance(data, dict):
            data = {}

        # -------------------------------------------------
        # INVENTORY UNITS
        # -------------------------------------------------

        raw_inventory = ReportService.first_value(
            data,
            "inventory_units",
            "Inventory Units",
            "inventory_quantity",
            "Inventory Quantity",
            "Inventory",
            "inventory",
            "inventory_count",
            default=0,
        )

        # -------------------------------------------------
        # DEMAND
        # -------------------------------------------------

        raw_demand = ReportService.first_value(
            data,
            "Demand",
            "demand",
            "predicted_demand",
            "Predicted Demand",
            "inventory_demand",
            default=0,
        )

        # -------------------------------------------------
        # PRODUCT COUNT
        # -------------------------------------------------

        raw_products = ReportService.first_value(
            data,
            "Products",
            "products",
            "product_count",
            "Product Count",
            "records",
            "Records",
            default=0,
        )

        inventory_units = ReportService.to_float(
            raw_inventory
        )

        demand = ReportService.to_float(
            raw_demand
        )

        products = ReportService.to_int(
            raw_products
        )

        # -------------------------------------------------
        # INVENTORY DATA
        # -------------------------------------------------

        inventory_data = ReportService.first_value(
            data,
            "inventory_data",
            "Inventory Data",
            "products_data",
            "items",
            default=[],
        )

        if not isinstance(
            inventory_data,
            list,
        ):
            inventory_data = []

        fixed_inventory = []

        for index, item in enumerate(
            inventory_data
        ):

            if not isinstance(item, dict):
                continue

            product = ReportService.first_value(
                item,
                "product",
                "name",
                "Product",
                "Product Name",
                default=f"Product {index + 1}",
            )

            quantity = ReportService.first_value(
                item,
                "quantity",
                "stock",
                "Inventory",
                "inventory",
                "available_stock",
                default=0,
            )

            item_demand = ReportService.first_value(
                item,
                "demand",
                "predictedDemand",
                "predicted_demand",
                "predicted",
                default=0,
            )

            fixed_inventory.append(
                {
                    "product": str(product),

                    "quantity":
                        ReportService.safe_round(
                            quantity
                        ),

                    "demand":
                        ReportService.safe_round(
                            item_demand
                        ),
                }
            )

        # -------------------------------------------------
        # FALLBACK INVENTORY ROW
        # -------------------------------------------------

        if not fixed_inventory:

            fixed_inventory = [
                {
                    "product": "Total Inventory",

                    "quantity":
                        round(
                            inventory_units,
                            2,
                        ),

                    "demand":
                        round(
                            demand,
                            2,
                        ),
                }
            ]

        # -------------------------------------------------
        # INVENTORY ANALYTICS
        # -------------------------------------------------

        demand_gap = (
            demand - inventory_units
        )

        inventory_surplus = (
            inventory_units - demand
        )

        inventory_coverage = (
            inventory_units / demand
            if demand > 0
            else 0.0
        )

        # -------------------------------------------------
        # STOCK STATUS
        # -------------------------------------------------

        if demand > inventory_units:

            stock_status = "Risk"

        elif inventory_units > demand * 1.20:

            stock_status = "Overstock"

        else:

            stock_status = "Balanced"

        # -------------------------------------------------
        # FINAL REPORT
        # -------------------------------------------------

        result = {
            **data,

            "status": data.get(
                "status",
                "success",
            ),

            "inventory_units":
                round(
                    inventory_units,
                    2,
                ),

            "Inventory Units":
                round(
                    inventory_units,
                    2,
                ),

            "inventory":
                round(
                    inventory_units,
                    2,
                ),

            "Inventory":
                round(
                    inventory_units,
                    2,
                ),

            "inventory_count":
                round(
                    inventory_units,
                    2,
                ),

            "products":
                products,

            "Products":
                products,

            "product_count":
                products,

            "Demand":
                round(
                    demand,
                    2,
                ),

            "demand":
                round(
                    demand,
                    2,
                ),

            "inventory_demand":
                round(
                    demand,
                    2,
                ),

            "demand_gap":
                round(
                    demand_gap,
                    2,
                ),

            "inventory_surplus":
                round(
                    inventory_surplus,
                    2,
                ),

            "inventory_coverage":
                round(
                    inventory_coverage,
                    4,
                ),

            "stock_status":
                stock_status,

            "inventory_data":
                fixed_inventory,
        }

        return ReportService._json_safe(
            result
        )

    # =====================================================
    # CUSTOMER REPORT
    # =====================================================

    @staticmethod
    @redis_cache(expire=600)
    def customer_report() -> dict[str, Any]:
        """
        Generate normalized customer segmentation report.
        """

        summary = ReportService.read_report(
            "customer_summary.json"
        )

        report = ReportService.read_report(
            "customer_segmentation_report.json"
        )

        if not isinstance(summary, dict):
            summary = {}

        if not isinstance(report, dict):
            report = {}

        # -------------------------------------------------
        # CUSTOMER COUNT
        # -------------------------------------------------

        customers = ReportService.to_int(
            ReportService.first_value(
                summary,
                "Customers",
                "customers",
                "customer_count",
                "total_customers",
                default=ReportService.first_value(
                    report,
                    "Customers",
                    "customers",
                    "customer_count",
                    "total_customers",
                    default=0,
                ),
            )
        )

        # -------------------------------------------------
        # SEGMENT DISTRIBUTION
        # -------------------------------------------------

        distribution = ReportService.first_value(
            summary,
            "Segment Distribution",
            "Clusters",
            "clusters",
            "segment_distribution",
            default={},
        )

        if not isinstance(
            distribution,
            dict,
        ):
            distribution = {}

        normalized_distribution = {}

        for key, value in distribution.items():

            normalized_distribution[
                str(key)
            ] = ReportService.to_int(
                value
            )

        # -------------------------------------------------
        # RAW SEGMENTS
        # -------------------------------------------------

        raw_segments = (
            report.get("segments")
            or summary.get("segments")
            or []
        )

        segments: list[
            dict[str, Any]
        ] = []

        # -------------------------------------------------
        # NORMALIZE SEGMENTS
        # -------------------------------------------------

        if isinstance(
            raw_segments,
            list,
        ):

            for index, item in enumerate(
                raw_segments
            ):

                if not isinstance(item, dict):
                    continue

                cluster = ReportService.first_value(
                    item,
                    "cluster",
                    "Cluster",
                    default=index,
                )

                count = ReportService.first_value(
                    item,
                    "customers",
                    "Customers",
                    "count",
                    default=normalized_distribution.get(
                        str(cluster),
                        0,
                    ),
                )

                average_age = ReportService.first_value(
                    item,
                    "average_age",
                    "Average Age",
                    "age",
                    default=0,
                )

                average_income = ReportService.first_value(
                    item,
                    "average_income",
                    "Average Income",
                    "income",
                    default=0,
                )

                average_spending = ReportService.first_value(
                    item,
                    "average_spending_score",
                    "Average Spending Score",
                    "spending_score",
                    "spending",
                    default=0,
                )

                existing_name = ReportService.first_value(
                    item,
                    "name",
                    "segment",
                    "Segment",
                    default=None,
                )

                segment = {
                    "cluster":
                        ReportService.to_int(
                            cluster
                        ),

                    "customers":
                        ReportService.to_int(
                            count
                        ),

                    "average_age":
                        ReportService.safe_round(
                            average_age
                        ),

                    "average_income":
                        ReportService.safe_round(
                            average_income
                        ),

                    "average_spending_score":
                        ReportService.safe_round(
                            average_spending
                        ),
                }

                if existing_name:
                    segment["name"] = str(
                        existing_name
                    )

                segments.append(
                    segment
                )

        # -------------------------------------------------
        # CSV FALLBACK
        # -------------------------------------------------

        if not segments:

            segments = (
                ReportService
                ._customer_segments_from_csv()
            )

        # -------------------------------------------------
        # CUSTOMER COUNT FALLBACK
        # -------------------------------------------------

        if customers == 0 and segments:

            customers = sum(
                ReportService.to_int(
                    segment.get(
                        "customers",
                        0,
                    )
                )
                for segment in segments
            )

        # -------------------------------------------------
        # BUSINESS CLASSIFICATION
        # -------------------------------------------------

        segments = (
            ReportService
            ._classify_customer_segments(
                segments
            )
        )

        # -------------------------------------------------
        # HIGHEST SPENDING SEGMENT
        # -------------------------------------------------

        highest_spending_segment = None

        if segments:

            highest_spending_segment = max(
                segments,
                key=lambda item:
                    ReportService.to_float(
                        item.get(
                            "average_spending_score",
                            0,
                        )
                    ),
            )

        # -------------------------------------------------
        # HIGH-INCOME / LOW-SPENDING
        # -------------------------------------------------

        high_income_low_spending = []

        if segments:

            incomes = [
                ReportService.to_float(
                    item.get(
                        "average_income",
                        0,
                    )
                )
                for item in segments
            ]

            spending = [
                ReportService.to_float(
                    item.get(
                        "average_spending_score",
                        0,
                    )
                )
                for item in segments
            ]

            income_threshold = (
                sum(incomes) / len(incomes)
                if incomes
                else 0.0
            )

            spending_threshold = (
                sum(spending) / len(spending)
                if spending
                else 0.0
            )

            high_income_low_spending = [
                segment
                for segment in segments
                if (
                    ReportService.to_float(
                        segment.get(
                            "average_income",
                            0,
                        )
                    )
                    >= income_threshold
                    and
                    ReportService.to_float(
                        segment.get(
                            "average_spending_score",
                            0,
                        )
                    )
                    <= spending_threshold
                )
            ]

        # -------------------------------------------------
        # FRONTEND-FRIENDLY SEGMENTS
        # -------------------------------------------------

        customer_segments = [
            {
                "segment":
                    segment.get(
                        "name",
                        "Unknown",
                    ),

                "cluster":
                    segment.get(
                        "cluster",
                        0,
                    ),

                "customers":
                    segment.get(
                        "customers",
                        0,
                    ),

                "average_age":
                    segment.get(
                        "average_age",
                        0,
                    ),

                "average_income":
                    segment.get(
                        "average_income",
                        0,
                    ),

                "average_spending_score":
                    segment.get(
                        "average_spending_score",
                        0,
                    ),
            }
            for segment in segments
        ]

        # -------------------------------------------------
        # SILHOUETTE SCORE
        # -------------------------------------------------

        silhouette_score = ReportService.to_float(
            ReportService.first_value(
                report,
                "silhouette_score",
                "Silhouette Score",
                default=ReportService.first_value(
                    summary,
                    "silhouette_score",
                    "Silhouette Score",
                    default=0,
                ),
            )
        )

        # -------------------------------------------------
        # FINAL REPORT
        # -------------------------------------------------

        result = {
            **summary,
            **report,

            "status":
                report.get(
                    "status",
                    summary.get(
                        "status",
                        "success",
                    ),
                ),

            "customers":
                customers,

            "Customers":
                customers,

            "Clusters":
                normalized_distribution,

            "clusters":
                normalized_distribution,

            "Segments":
                len(segments),

            "segments_count":
                len(segments),

            "Segment Distribution":
                normalized_distribution,

            "customer_segments":
                customer_segments,

            "segments":
                segments,

            "highest_spending_segment":
                highest_spending_segment,

            "high_income_low_spending":
                high_income_low_spending,

            "silhouette_score":
                round(
                    silhouette_score,
                    4,
                ),
        }

        return ReportService._json_safe(
            result
        )

    # =====================================================
    # CUSTOMER CSV FALLBACK
    # =====================================================

    @staticmethod
    def _customer_segments_from_csv() -> list[
        dict[str, Any]
    ]:
        """
        Fallback customer segmentation loader.

        Expected CSV columns:

            - Cluster
            - Annual Income (k$)
            - Spending Score (1-100)
            - Age
        """

        try:

            csv_paths = [
                ReportService.OUTPUT_DIR
                / "customer_segments.csv",

                ReportService.OUTPUT_DIR
                / "customer_segmentation.csv",

                Path("outputs")
                / "customer_segments.csv",
            ]

            csv_path: Optional[Path] = None

            for path in csv_paths:

                if path.exists() and path.is_file():

                    csv_path = path
                    break

            if csv_path is None:

                logger.warning(
                    "Customer segmentation CSV not found"
                )

                return []

            df = pd.read_csv(
                csv_path
            )

            if df.empty:

                logger.warning(
                    "Customer segmentation CSV is empty: %s",
                    csv_path,
                )

                return []

            if "Cluster" not in df.columns:

                logger.warning(
                    "Cluster column missing from customer CSV"
                )

                return []

            segments: list[
                dict[str, Any]
            ] = []

            for cluster, group in df.groupby(
                "Cluster",
                dropna=False,
            ):

                # -----------------------------------------
                # AGE
                # -----------------------------------------

                if "Age" in group.columns:

                    age = pd.to_numeric(
                        group["Age"],
                        errors="coerce",
                    )

                    average_age = (
                        float(age.mean())
                        if not age.dropna().empty
                        else 0.0
                    )

                else:

                    average_age = 0.0

                # -----------------------------------------
                # INCOME
                # -----------------------------------------

                if "Annual Income (k$)" in group.columns:

                    income = pd.to_numeric(
                        group[
                            "Annual Income (k$)"
                        ],
                        errors="coerce",
                    )

                    average_income = (
                        float(income.mean())
                        if not income.dropna().empty
                        else 0.0
                    )

                else:

                    average_income = 0.0

                # -----------------------------------------
                # SPENDING
                # -----------------------------------------

                if (
                    "Spending Score (1-100)"
                    in group.columns
                ):

                    spending = pd.to_numeric(
                        group[
                            "Spending Score (1-100)"
                        ],
                        errors="coerce",
                    )

                    average_spending = (
                        float(spending.mean())
                        if not spending.dropna().empty
                        else 0.0
                    )

                else:

                    average_spending = 0.0

                # -----------------------------------------
                # BUILD SEGMENT
                # -----------------------------------------

                segments.append(
                    {
                        "cluster":
                            ReportService.to_int(
                                cluster
                            ),

                        "customers":
                            int(len(group)),

                        "average_age":
                            round(
                                average_age,
                                2,
                            ),

                        "average_income":
                            round(
                                average_income,
                                2,
                            ),

                        "average_spending_score":
                            round(
                                average_spending,
                                2,
                            ),
                    }
                )

            logger.info(
                "Customer segmentation fallback loaded: %s clusters",
                len(segments),
            )

            return segments

        except (
            FileNotFoundError,
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
        ):

            logger.exception(
                "Customer segmentation CSV could not be read"
            )

            return []

        except Exception:

            logger.exception(
                "Customer CSV segmentation fallback failed"
            )

            return []

    # =====================================================
    # CUSTOMER SEGMENT CLASSIFICATION
    # =====================================================

    @staticmethod
    def _classify_customer_segments(
        segments: list[
            dict[str, Any]
        ],
    ) -> list[
        dict[str, Any]
    ]:
        """
        Convert numerical customer clusters into
        business-friendly segment names.

        Classification is based on average income
        and average spending score.
        """

        if not segments:
            return []

        spending_values = [
            ReportService.to_float(
                segment.get(
                    "average_spending_score",
                    0,
                )
            )
            for segment in segments
        ]

        income_values = [
            ReportService.to_float(
                segment.get(
                    "average_income",
                    0,
                )
            )
            for segment in segments
        ]

        spending_mean = (
            sum(spending_values)
            / len(spending_values)
            if spending_values
            else 0.0
        )

        income_mean = (
            sum(income_values)
            / len(income_values)
            if income_values
            else 0.0
        )

        classified_segments = []

        for segment in segments:

            spending = ReportService.to_float(
                segment.get(
                    "average_spending_score",
                    0,
                )
            )

            income = ReportService.to_float(
                segment.get(
                    "average_income",
                    0,
                )
            )

            existing_name = segment.get(
                "name"
            )

            # Preserve explicitly supplied
            # business-friendly names.
            if existing_name:

                name = str(
                    existing_name
                )

            elif (
                income >= income_mean
                and
                spending < spending_mean
            ):

                name = (
                    "High Income - Low Spending"
                )

            elif (
                income >= income_mean
                and
                spending >= spending_mean
            ):

                name = "High Value"

            elif (
                income < income_mean
                and
                spending >= spending_mean
            ):

                name = "Potential Value"

            else:

                name = "Low Value"

            classified_segments.append(
                {
                    **segment,
                    "name": name,
                }
            )

        return classified_segments

    # =====================================================
    # FORECAST REPORT
    # =====================================================

    @staticmethod
    @redis_cache(expire=600)
    def forecast_report() -> dict[str, Any]:
        """
        Generate normalized enterprise forecast report.
        """

        data = ReportService.read_report(
            "forecast_summary.json"
        )

        if not isinstance(data, dict):
            data = {}

        # -------------------------------------------------
        # RAW FORECAST DATA
        # -------------------------------------------------

        forecast_data = ReportService.first_value(
            data,
            "forecast",
            "forecasts",
            "forecast_data",
            "demand",
            "predictions",
            "data",
            default=[],
        )

        if not isinstance(
            forecast_data,
            list,
        ):
            forecast_data = []

        fixed_forecast: list[
            dict[str, Any]
        ] = []

        # -------------------------------------------------
        # NORMALIZE FORECAST RECORDS
        # -------------------------------------------------

        for index, item in enumerate(
            forecast_data
        ):

            if not isinstance(item, dict):
                continue

            date = ReportService.first_value(
                item,
                "date",
                "Date",
                "month",
                "Month",
                "period",
                "Period",
                "ds",
                default=f"Period {index + 1}",
            )

            forecast_value = ReportService.first_value(
                item,
                "forecast",
                "Forecast",
                "demand",
                "Demand",
                "prediction",
                "Prediction",
                "predicted_demand",
                "Predicted Demand",
                "yhat",
                default=0,
            )

            forecast_value = ReportService.to_float(
                forecast_value
            )

            # -------------------------------------------------
            # ACTUAL
            # -------------------------------------------------

            actual = None

            actual_value = ReportService.first_value(
                item,
                "actual",
                "Actual",
                "actual_demand",
                "Actual Demand",
                default=None,
            )

            if actual_value is not None:

                actual = ReportService.to_float(
                    actual_value
                )

            # -------------------------------------------------
            # LOWER BOUND
            # -------------------------------------------------

            lower = None

            lower_value = ReportService.first_value(
                item,
                "lower",
                "Lower",
                "lower_bound",
                "Lower Bound",
                "yhat_lower",
                default=None,
            )

            if lower_value is not None:

                lower = ReportService.to_float(
                    lower_value
                )

            # -------------------------------------------------
            # UPPER BOUND
            # -------------------------------------------------

            upper = None

            upper_value = ReportService.first_value(
                item,
                "upper",
                "Upper",
                "upper_bound",
                "Upper Bound",
                "yhat_upper",
                default=None,
            )

            if upper_value is not None:

                upper = ReportService.to_float(
                    upper_value
                )

            # -------------------------------------------------
            # FORECAST TYPE
            # -------------------------------------------------

            forecast_type = ReportService.first_value(
                item,
                "forecast_type",
                "Forecast Type",
                "type",
                "Type",
                default=None,
            )

            if forecast_type is None:

                forecast_type = (
                    "historical"
                    if actual is not None
                    else "future"
                )

            forecast_type = str(
                forecast_type
            ).lower().strip()

            if forecast_type in {
                "history",
                "historical_data",
                "actual",
                "past",
            }:

                forecast_type = "historical"

            elif forecast_type in {
                "prediction",
                "predicted",
                "future_data",
                "forecasted",
                "forecast",
            }:

                forecast_type = "future"

            else:

                forecast_type = (
                    "historical"
                    if actual is not None
                    else "future"
                )

            # -------------------------------------------------
            # ERROR
            # -------------------------------------------------

            error = None
            error_percent = None

            if actual is not None:

                error = (
                    forecast_value - actual
                )

                if actual != 0:

                    error_percent = (
                        error / actual
                    ) * 100

            fixed_forecast.append(
                {
                    "date": str(date),

                    "forecast":
                        ReportService.safe_round(
                            forecast_value
                        ),

                    "demand":
                        ReportService.safe_round(
                            forecast_value
                        ),

                    "prediction":
                        ReportService.safe_round(
                            forecast_value
                        ),

                    "actual":
                        (
                            ReportService.safe_round(
                                actual
                            )
                            if actual is not None
                            else None
                        ),

                    "lower":
                        (
                            ReportService.safe_round(
                                lower
                            )
                            if lower is not None
                            else None
                        ),

                    "upper":
                        (
                            ReportService.safe_round(
                                upper
                            )
                            if upper is not None
                            else None
                        ),

                    "error":
                        (
                            ReportService.safe_round(
                                error
                            )
                            if error is not None
                            else None
                        ),

                    "error_percent":
                        (
                            ReportService.safe_round(
                                error_percent
                            )
                            if error_percent is not None
                            else None
                        ),

                    "forecast_type":
                        forecast_type,
                }
            )

        # -------------------------------------------------
        # HISTORICAL / FUTURE
        # -------------------------------------------------

        historical = [
            item
            for item in fixed_forecast
            if item.get(
                "forecast_type"
            ) == "historical"
        ]

        future = [
            item
            for item in fixed_forecast
            if item.get(
                "forecast_type"
            ) == "future"
        ]

        future_values = [
            ReportService.to_float(
                item.get(
                    "forecast",
                    0,
                )
            )
            for item in future
        ]

        historical_values = [
            ReportService.to_float(
                item.get(
                    "forecast",
                    0,
                )
            )
            for item in historical
        ]

        # -------------------------------------------------
        # AVERAGE FORECAST
        # -------------------------------------------------

        average_forecast = (
            sum(future_values)
            / len(future_values)
            if future_values
            else ReportService.to_float(
                data.get(
                    "average_forecast",
                    0,
                )
            )
        )

        # -------------------------------------------------
        # LATEST FORECAST
        # -------------------------------------------------

        if future:

            latest_forecast = future[-1].get(
                "forecast",
                0,
            )

        elif fixed_forecast:

            latest_forecast = fixed_forecast[-1].get(
                "forecast",
                0,
            )

        else:

            latest_forecast = ReportService.to_float(
                data.get(
                    "latest_forecast",
                    0,
                )
            )

        # -------------------------------------------------
        # MIN / MAX
        # -------------------------------------------------

        minimum_forecast = (
            min(future_values)
            if future_values
            else ReportService.to_float(
                data.get(
                    "minimum_forecast",
                    0,
                )
            )
        )

        maximum_forecast = (
            max(future_values)
            if future_values
            else ReportService.to_float(
                data.get(
                    "maximum_forecast",
                    0,
                )
            )
        )

        # -------------------------------------------------
        # GROWTH
        # -------------------------------------------------

        raw_growth = ReportService.first_value(
            data,
            "growth",
            "Growth",
            "growth_rate",
            "Growth Rate",
            default=0,
        )

        growth = ReportService.to_float(
            raw_growth
        )

        if (
            growth == 0
            and len(future_values) >= 2
        ):

            first_forecast = future_values[0]
            last_forecast = future_values[-1]

            if first_forecast != 0:

                growth = (
                    (
                        last_forecast
                        - first_forecast
                    )
                    / first_forecast
                ) * 100

        # -------------------------------------------------
        # FORECAST ACCURACY
        # -------------------------------------------------

        accuracy = None

        historical_errors = [
            ReportService.to_float(
                item.get(
                    "error_percent"
                )
            )
            for item in historical
            if item.get(
                "error_percent"
            ) is not None
        ]

        if historical_errors:

            mape = (
                sum(
                    abs(error)
                    for error in historical_errors
                )
                / len(historical_errors)
            )

            accuracy = max(
                0.0,
                min(
                    100.0,
                    100.0 - mape,
                ),
            )

        else:

            raw_accuracy = ReportService.first_value(
                data,
                "forecast_accuracy",
                "accuracy",
                "Accuracy",
                default=None,
            )

            if raw_accuracy is not None:

                accuracy = max(
                    0.0,
                    min(
                        100.0,
                        ReportService.to_float(
                            raw_accuracy
                        ),
                    ),
                )

        # -------------------------------------------------
        # AVAILABILITY
        # -------------------------------------------------

        available_value = data.get(
            "available"
        )

        if available_value is None:

            available = bool(
                fixed_forecast
            )

        elif isinstance(
            available_value,
            str,
        ):

            available = (
                available_value.lower()
                in {
                    "true",
                    "1",
                    "yes",
                    "available",
                }
            )

        else:

            available = bool(
                available_value
            )

        # -------------------------------------------------
        # MODEL
        # -------------------------------------------------

        model = ReportService.first_value(
            data,
            "model",
            "Model",
            "model_name",
            "Model Name",
            default="Facebook Prophet",
        )

        # -------------------------------------------------
        # FINAL REPORT
        # -------------------------------------------------

        result = {
            **data,

            "status":
                data.get(
                    "status",
                    "success",
                ),

            "available":
                available,

            "model":
                str(model),

            "forecast":
                fixed_forecast,

            "demand":
                fixed_forecast,

            "predictions":
                fixed_forecast,

            "historical":
                historical,

            "future":
                future,

            "records":
                len(fixed_forecast),

            "forecast_points":
                len(fixed_forecast),

            "historical_points":
                len(historical),

            "future_points":
                len(future),

            "average_forecast":
                ReportService.safe_round(
                    average_forecast
                ),

            "latest_forecast":
                ReportService.safe_round(
                    latest_forecast
                ),

            "minimum_forecast":
                ReportService.safe_round(
                    minimum_forecast
                ),

            "maximum_forecast":
                ReportService.safe_round(
                    maximum_forecast
                ),

            "growth":
                ReportService.safe_round(
                    growth
                ),

            "forecast_accuracy":
                (
                    ReportService.safe_round(
                        accuracy
                    )
                    if accuracy is not None
                    else None
                ),

            "historical_average":
                (
                    ReportService.safe_round(
                        sum(historical_values)
                        / len(historical_values)
                    )
                    if historical_values
                    else 0.0
                ),

            "future_average":
                (
                    ReportService.safe_round(
                        sum(future_values)
                        / len(future_values)
                    )
                    if future_values
                    else 0.0
                ),
        }

        return ReportService._json_safe(
            result
        )

    # =====================================================
    # BUSINESS KPI REPORT
    # =====================================================

    @staticmethod
    @redis_cache(expire=600)
    def business_kpi_report() -> dict[str, Any]:
        """
        Generate unified enterprise KPI report.

        Combines:
            - Sales
            - Inventory
            - Customers
        """

        data = ReportService.read_report(
            "business_kpi_report.json"
        )

        if not isinstance(data, dict):
            data = {}

        sales = ReportService.sales_report()

        inventory = ReportService.inventory_report()

        customer = ReportService.customer_report()

        # -------------------------------------------------
        # SALES
        # -------------------------------------------------

        revenue = ReportService.to_float(
            ReportService.first_value(
                data,
                "revenue",
                "Revenue",
                "total_sales",
                "Total Sales",
                default=sales.get(
                    "revenue",
                    0,
                ),
            )
        )

        profit = ReportService.to_float(
            ReportService.first_value(
                data,
                "profit",
                "Profit",
                "total_profit",
                "Total Profit",
                default=sales.get(
                    "profit",
                    0,
                ),
            )
        )

        profit_margin = ReportService.to_float(
            ReportService.first_value(
                data,
                "profit_margin",
                "Profit Margin",
                "margin",
                default=sales.get(
                    "profit_margin",
                    0,
                ),
            )
        )

        growth = ReportService.to_float(
            ReportService.first_value(
                data,
                "growth_rate",
                "growth",
                "Growth Rate",
                "Growth",
                default=sales.get(
                    "growth",
                    0,
                ),
            )
        )

        # -------------------------------------------------
        # INVENTORY
        # -------------------------------------------------

        inventory_units = ReportService.to_float(
            inventory.get(
                "inventory_units",
                0,
            )
        )

        inventory_demand = ReportService.to_float(
            ReportService.first_value(
                inventory,
                "Demand",
                "demand",
                "inventory_demand",
                default=0,
            )
        )

        products = ReportService.to_int(
            inventory.get(
                "products",
                0,
            )
        )

        inventory_surplus = ReportService.to_float(
            inventory.get(
                "inventory_surplus",
                0,
            )
        )

        inventory_coverage = ReportService.to_float(
            inventory.get(
                "inventory_coverage",
                0,
            )
        )

        stock_status = str(
            inventory.get(
                "stock_status",
                "Balanced",
            )
        )

        # -------------------------------------------------
        # CUSTOMERS
        # -------------------------------------------------

        customers = ReportService.to_int(
            customer.get(
                "customers",
                0,
            )
        )

        customer_segments = ReportService.to_int(
            customer.get(
                "Segments",
                customer.get(
                    "segments_count",
                    0,
                ),
            )
        )

        silhouette_score = ReportService.to_float(
            customer.get(
                "silhouette_score",
                0,
            )
        )

        # -------------------------------------------------
        # FINAL KPI
        # -------------------------------------------------

        result = {
            **data,

            "status":
                data.get(
                    "status",
                    "success",
                ),

            "revenue":
                round(
                    revenue,
                    2,
                ),

            "total_sales":
                round(
                    revenue,
                    2,
                ),

            "profit":
                round(
                    profit,
                    2,
                ),

            "profit_margin":
                round(
                    profit_margin,
                    2,
                ),

            "growth_rate":
                round(
                    growth,
                    2,
                ),

            "growth":
                round(
                    growth,
                    2,
                ),

            "inventory_units":
                round(
                    inventory_units,
                    2,
                ),

            "inventory":
                round(
                    inventory_units,
                    2,
                ),

            "products":
                products,

            "inventory_demand":
                round(
                    inventory_demand,
                    2,
                ),

            "inventory_surplus":
                round(
                    inventory_surplus,
                    2,
                ),

            "inventory_coverage":
                round(
                    inventory_coverage,
                    4,
                ),

            "stock_status":
                stock_status,

            "customers":
                customers,

            "customer_segments":
                customer_segments,

            "customer_silhouette":
                round(
                    silhouette_score,
                    4,
                ),
        }

        return ReportService._json_safe(
            result
        )

    # =====================================================
    # EXECUTIVE SUMMARY
    # =====================================================

    @staticmethod
    @redis_cache(expire=600)
    def executive_summary() -> dict[str, Any]:
        """
        Generate high-level executive business summary.
        """

        sales = ReportService.sales_report()

        inventory = ReportService.inventory_report()

        customer = ReportService.customer_report()

        forecast = ReportService.forecast_report()

        revenue = ReportService.to_float(
            sales.get(
                "revenue",
                0,
            )
        )

        profit = ReportService.to_float(
            sales.get(
                "profit",
                0,
            )
        )

        growth = ReportService.to_float(
            sales.get(
                "growth",
                0,
            )
        )

        stock_status = str(
            inventory.get(
                "stock_status",
                "Balanced",
            )
        )

        inventory_units = ReportService.to_float(
            inventory.get(
                "inventory_units",
                0,
            )
        )

        demand = ReportService.to_float(
            inventory.get(
                "demand",
                0,
            )
        )

        customers = ReportService.to_int(
            customer.get(
                "customers",
                0,
            )
        )

        forecast_accuracy = forecast.get(
            "forecast_accuracy"
        )

        # -------------------------------------------------
        # BUSINESS HEALTH
        # -------------------------------------------------

        risk_count = 0

        if stock_status == "Risk":
            risk_count += 1

        if growth < 0:
            risk_count += 1

        if (
            forecast_accuracy is not None
            and
            ReportService.to_float(
                forecast_accuracy
            ) < 70
        ):
            risk_count += 1

        if risk_count == 0:

            business_health = "Healthy"

        elif risk_count == 1:

            business_health = "Watch"

        else:

            business_health = "At Risk"

        # -------------------------------------------------
        # EXECUTIVE MESSAGE
        # -------------------------------------------------

        if business_health == "Healthy":

            message = (
                "Business performance is currently healthy "
                "with no major risk indicators detected."
            )

        elif business_health == "Watch":

            message = (
                "Business performance is stable, but "
                "management attention is recommended for "
                "one or more emerging indicators."
            )

        else:

            message = (
                "Business performance requires management "
                "attention because multiple risk indicators "
                "have been detected."
            )

        result = {
            "status": "success",

            "business_health":
                business_health,

            "executive_message":
                message,

            "revenue":
                round(
                    revenue,
                    2,
                ),

            "profit":
                round(
                    profit,
                    2,
                ),

            "growth":
                round(
                    growth,
                    2,
                ),

            "inventory_units":
                round(
                    inventory_units,
                    2,
                ),

            "inventory_demand":
                round(
                    demand,
                    2,
                ),

            "stock_status":
                stock_status,

            "customers":
                customers,

            "forecast_accuracy":
                (
                    ReportService.safe_round(
                        forecast_accuracy
                    )
                    if forecast_accuracy is not None
                    else None
                ),

            "risk_count":
                risk_count,

            "generated_at":
                ReportService.utc_now_iso(),
        }

        return ReportService._json_safe(
            result
        )

    # =====================================================
    # DASHBOARD ANALYTICS
    # =====================================================

    @staticmethod
    @redis_cache(expire=300)
    def dashboard_analytics() -> dict[str, Any]:
        """
        Return a single normalized payload for the
        enterprise dashboard.
        """

        sales = ReportService.sales_report()

        inventory = ReportService.inventory_report()

        customer = ReportService.customer_report()

        forecast = ReportService.forecast_report()

        kpi = ReportService.business_kpi_report()

        executive = ReportService.executive_summary()

        result = {
            "status": "success",

            "generated_at":
                ReportService.utc_now_iso(),

            "kpis": {

                "revenue":
                    kpi.get(
                        "revenue",
                        0,
                    ),

                "profit":
                    kpi.get(
                        "profit",
                        0,
                    ),

                "profit_margin":
                    kpi.get(
                        "profit_margin",
                        0,
                    ),

                "growth":
                    kpi.get(
                        "growth",
                        0,
                    ),

                "inventory_units":
                    kpi.get(
                        "inventory_units",
                        0,
                    ),

                "inventory_demand":
                    kpi.get(
                        "inventory_demand",
                        0,
                    ),

                "customers":
                    kpi.get(
                        "customers",
                        0,
                    ),

                "customer_segments":
                    kpi.get(
                        "customer_segments",
                        0,
                    ),
            },

            "sales":
                sales,

            "inventory":
                inventory,

            "customers":
                customer,

            "forecast":
                forecast,

            "executive":
                executive,
        }

        return ReportService._json_safe(
            result
        )

    # =====================================================
    # AI COPILOT CONTEXT
    # =====================================================

    @staticmethod
    @redis_cache(expire=300)
    def copilot_context() -> dict[str, Any]:
        """
        Build a compact analytics context for the
        AI Copilot / RAG / LLM layer.
        """

        sales = ReportService.sales_report()

        inventory = ReportService.inventory_report()

        customer = ReportService.customer_report()

        forecast = ReportService.forecast_report()

        executive = ReportService.executive_summary()

        context = {

            "business_health":
                executive.get(
                    "business_health",
                    "Unknown",
                ),

            "revenue":
                sales.get(
                    "revenue",
                    0,
                ),

            "profit":
                sales.get(
                    "profit",
                    0,
                ),

            "profit_margin":
                sales.get(
                    "profit_margin",
                    0,
                ),

            "sales_growth":
                sales.get(
                    "growth",
                    0,
                ),

            "best_category":
                sales.get(
                    "best_category",
                    "N/A",
                ),

            "best_region":
                sales.get(
                    "best_region",
                    "N/A",
                ),

            "inventory_units":
                inventory.get(
                    "inventory_units",
                    0,
                ),

            "inventory_demand":
                inventory.get(
                    "demand",
                    0,
                ),

            "inventory_surplus":
                inventory.get(
                    "inventory_surplus",
                    0,
                ),

            "inventory_coverage":
                inventory.get(
                    "inventory_coverage",
                    0,
                ),

            "stock_status":
                inventory.get(
                    "stock_status",
                    "Balanced",
                ),

            "customers":
                customer.get(
                    "customers",
                    0,
                ),

            "customer_segments":
                customer.get(
                    "segments_count",
                    0,
                ),

            "highest_spending_segment":
                customer.get(
                    "highest_spending_segment",
                    None,
                ),

            "high_income_low_spending":
                customer.get(
                    "high_income_low_spending",
                    [],
                ),

            "forecast_model":
                forecast.get(
                    "model",
                    "Unknown",
                ),

            "forecast_accuracy":
                forecast.get(
                    "forecast_accuracy",
                    None,
                ),

            "average_forecast":
                forecast.get(
                    "average_forecast",
                    0,
                ),

            "latest_forecast":
                forecast.get(
                    "latest_forecast",
                    0,
                ),

            "forecast_growth":
                forecast.get(
                    "growth",
                    0,
                ),

            "risk_count":
                executive.get(
                    "risk_count",
                    0,
                ),
        }

        return ReportService._json_safe(
            context
        )

    # =====================================================
    # ALL REPORTS
    # =====================================================

    @staticmethod
    @redis_cache(expire=300)
    def get_all_reports() -> dict[str, Any]:
        """
        Return all normalized enterprise reports.
        """

        result = {
            "status": "success",

            "generated_at":
                ReportService.utc_now_iso(),

            "sales":
                ReportService.sales_report(),

            "inventory":
                ReportService.inventory_report(),

            "customer":
                ReportService.customer_report(),

            "forecast":
                ReportService.forecast_report(),

            "kpi":
                ReportService.business_kpi_report(),

            "executive":
                ReportService.executive_summary(),

            "dashboard":
                ReportService.dashboard_analytics(),

            "copilot":
                ReportService.copilot_context(),
        }

        return ReportService._json_safe(
            result
        )


# =========================================================
# SERVICE INSTANCE
# =========================================================

report_service = ReportService()


# =========================================================
# PUBLIC EXPORTS
# =========================================================

__all__ = [
    "ReportService",
    "report_service",
]

