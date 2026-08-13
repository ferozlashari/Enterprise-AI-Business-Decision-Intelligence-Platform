
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Prediction Service

Handles:

- Sales Prediction
- Inventory Prediction
- Demand Forecasting
- Customer Segmentation
- Feature Importance

Author : Feroz Ali
=========================================================
"""

from pathlib import Path
import json
import logging
import re

import pandas as pd


logger = logging.getLogger("PredictionService")


class PredictionService:

    # =====================================================
    # BASE DIRECTORIES
    # =====================================================

    BASE_DIR = (
        Path(__file__)
        .resolve()
        .parent
        .parent
        .parent
    )

    REPORT_DIR = BASE_DIR / "reports"

    OUTPUT_DIR = BASE_DIR / "outputs"

    # Possible locations for original datasets.
    DATA_DIRECTORIES = [

        BASE_DIR / "data",

        BASE_DIR / "datasets",

        BASE_DIR / "dataset",

        BASE_DIR / "input",

        BASE_DIR / "inputs",

        BASE_DIR / "resources",

        BASE_DIR / "reports",

        BASE_DIR / "outputs",

        BASE_DIR,

    ]

    # =====================================================
    # SAFE FLOAT
    # =====================================================

    @staticmethod
    def safe_float(
        value,
        default=0.0
    ):

        try:

            if value is None:
                return default

            if isinstance(value, str):

                value = (
                    value
                    .replace(",", "")
                    .replace("$", "")
                    .replace("%", "")
                    .strip()
                )

            if value == "":
                return default

            number = float(value)

            if pd.isna(number):
                return default

            return round(
                number,
                2
            )

        except (
            TypeError,
            ValueError
        ):

            return default

    # =====================================================
    # SAFE INTEGER
    # =====================================================

    @staticmethod
    def safe_int(
        value,
        default=0
    ):

        try:

            if value is None:
                return default

            number = float(value)

            if pd.isna(number):
                return default

            return int(number)

        except (
            TypeError,
            ValueError
        ):

            return default

    # =====================================================
    # NORMALIZE COLUMN NAME
    # =====================================================

    @staticmethod
    def normalize_column_name(
        column
    ):

        if column is None:
            return ""

        value = (
            str(column)
            .strip()
            .lower()
        )

        value = value.replace(
            "$",
            " dollar "
        )

        value = re.sub(
            r"[_\-\(\)\[\]\{\}/]+",
            " ",
            value
        )

        value = re.sub(
            r"[^a-z0-9]+",
            " ",
            value
        )

        return " ".join(
            value.split()
        )

    # =====================================================
    # FIND COLUMN
    # =====================================================

    @staticmethod
    def find_column(
        columns,
        exact_names=None,
        contains_names=None
    ):

        exact_names = (
            exact_names
            or []
        )

        contains_names = (
            contains_names
            or []
        )

        normalized_columns = {}

        for column in columns:

            normalized = (
                PredictionService
                .normalize_column_name(
                    column
                )
            )

            normalized_columns[
                normalized
            ] = column

        # -------------------------------------------------
        # EXACT MATCH
        # -------------------------------------------------

        for candidate in exact_names:

            normalized_candidate = (
                PredictionService
                .normalize_column_name(
                    candidate
                )
            )

            if (
                normalized_candidate
                in normalized_columns
            ):

                return normalized_columns[
                    normalized_candidate
                ]

        # -------------------------------------------------
        # CONTAINS MATCH
        # -------------------------------------------------

        for column in columns:

            normalized_column = (
                PredictionService
                .normalize_column_name(
                    column
                )
            )

            for candidate in contains_names:

                normalized_candidate = (
                    PredictionService
                    .normalize_column_name(
                        candidate
                    )
                )

                if (
                    normalized_candidate
                    and
                    normalized_candidate
                    in normalized_column
                ):

                    return column

        return None

    # =====================================================
    # JSON READER
    # =====================================================

    @staticmethod
    def read_json(
        file
    ):

        try:

            file = Path(file)

            if not file.exists():

                logger.warning(
                    "JSON file not found: %s",
                    file
                )

                return {}

            with open(
                file,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            if not isinstance(
                data,
                dict
            ):

                return {}

            # -------------------------------------------------
            # SUPPORT NESTED REPORT FORMAT
            # -------------------------------------------------

            if isinstance(
                data.get("report"),
                dict
            ):

                return data["report"]

            if isinstance(
                data.get("data"),
                dict
            ):

                return data["data"]

            if isinstance(
                data.get("result"),
                dict
            ):

                return data["result"]

            return data

        except (
            json.JSONDecodeError,
            OSError,
            TypeError,
            ValueError
        ) as error:

            logger.warning(
                "Unable to read JSON %s: %s",
                file,
                error
            )

            return {}

    # =====================================================
    # FIND FIRST EXISTING FILE
    # =====================================================

    @staticmethod
    def find_file(
        filenames,
        directories=None
    ):

        if directories is None:

            directories = [

                PredictionService.REPORT_DIR,

                PredictionService.OUTPUT_DIR

            ]

        for directory in directories:

            directory = Path(
                directory
            )

            for filename in filenames:

                file = (
                    directory
                    / filename
                )

                if file.exists():

                    return file

        return None

    # =====================================================
    # FIND ORIGINAL SALES DATASET
    #
    # Used as fallback when Prophet output does not contain
    # actual historical demand.
    # =====================================================

    @staticmethod
    def find_actual_sales_dataset():

        filenames = [

            "superstore.csv",

            "Superstore.csv",

            "superstore_sales.csv",

            "superstore_sales_dataset.csv",

            "sales.csv",

            "sales_data.csv",

            "sales_dataset.csv",

            "retail_sales.csv",

            "retail_sales_dataset.csv",

        ]

        file = PredictionService.find_file(
            filenames,
            PredictionService.DATA_DIRECTORIES
        )

        if file is not None:

            return file

        # -------------------------------------------------
        # Recursive fallback search
        # -------------------------------------------------

        for directory in (
            PredictionService.DATA_DIRECTORIES
        ):

            directory = Path(
                directory
            )

            if not directory.exists():
                continue

            try:

                for filename in filenames:

                    matches = list(
                        directory.rglob(
                            filename
                        )
                    )

                    if matches:

                        return matches[0]

            except Exception as error:

                logger.warning(
                    "Dataset search failed in %s: %s",
                    directory,
                    error
                )

        return None

    # =====================================================
    # LOAD ACTUAL MONTHLY SALES
    #
    # Expected original dataset:
    #
    # Order Date
    # Sales
    #
    # Returns:
    #
    # {
    #     "2014-01-01": 12345.67,
    #     "2014-02-01": 23456.78
    # }
    # =====================================================

    @staticmethod
    def get_actual_monthly_sales():

        file = (
            PredictionService
            .find_actual_sales_dataset()
        )

        if file is None:

            logger.warning(
                "Original sales dataset not found. "
                "Actual demand cannot be reconstructed."
            )

            return {}

        try:

            logger.info(
                "Actual sales source detected: %s",
                file
            )

            # -------------------------------------------------
            # Read CSV
            # -------------------------------------------------

            try:

                df = pd.read_csv(
                    file,
                    encoding="latin1"
                )

            except Exception:

                df = pd.read_csv(
                    file
                )

            if df.empty:

                logger.warning(
                    "Actual sales dataset is empty: %s",
                    file
                )

                return {}

            # -------------------------------------------------
            # Clean columns
            # -------------------------------------------------

            df.columns = [

                str(column).strip()

                for column in df.columns

            ]

            # -------------------------------------------------
            # Detect Order Date
            # -------------------------------------------------

            date_column = (
                PredictionService.find_column(

                    df.columns,

                    exact_names=[

                        "Order Date",

                        "order date",

                        "date",

                        "sales date"

                    ],

                    contains_names=[

                        "order date",

                        "sales date"

                    ]

                )
            )

            # -------------------------------------------------
            # Detect Sales
            # -------------------------------------------------

            sales_column = (
                PredictionService.find_column(

                    df.columns,

                    exact_names=[

                        "Sales",

                        "sales",

                        "revenue",

                        "amount"

                    ],

                    contains_names=[

                        "sales"

                    ]

                )
            )

            if date_column is None:

                logger.warning(
                    "Order Date column not found "
                    "in actual sales dataset."
                )

                return {}

            if sales_column is None:

                logger.warning(
                    "Sales column not found "
                    "in actual sales dataset."
                )

                return {}

            logger.info(
                "Actual sales date column: %s",
                date_column
            )

            logger.info(
                "Actual sales value column: %s",
                sales_column
            )

            # -------------------------------------------------
            # Convert date
            # -------------------------------------------------

            df[date_column] = pd.to_datetime(
                df[date_column],
                errors="coerce"
            )

            # -------------------------------------------------
            # Convert sales
            # -------------------------------------------------

            df[sales_column] = pd.to_numeric(
                df[sales_column],
                errors="coerce"
            )

            # -------------------------------------------------
            # Remove invalid rows
            # -------------------------------------------------

            df = df[
                df[date_column].notna()
                &
                df[sales_column].notna()
            ].copy()

            if df.empty:

                return {}

            # -------------------------------------------------
            # Convert to monthly period
            # -------------------------------------------------

            df["__forecast_month"] = (
                df[date_column]
                .dt.to_period("M")
                .dt.to_timestamp()
            )

            # -------------------------------------------------
            # Aggregate monthly actual sales
            # -------------------------------------------------

            monthly = (
                df.groupby(
                    "__forecast_month"
                )[sales_column]
                .sum()
                .reset_index()
            )

            actual_map = {}

            for _, row in monthly.iterrows():

                date_value = row[
                    "__forecast_month"
                ]

                sales_value = row[
                    sales_column
                ]

                if pd.isna(
                    date_value
                ):

                    continue

                if pd.isna(
                    sales_value
                ):

                    continue

                key = (
                    pd.Timestamp(
                        date_value
                    ).strftime(
                        "%Y-%m-%d"
                    )
                )

                actual_map[
                    key
                ] = PredictionService.safe_float(
                    sales_value
                )

            logger.info(
                "Actual monthly sales generated: %s records",
                len(actual_map)
            )

            return actual_map

        except Exception as error:

            logger.exception(
                "Unable to build actual monthly sales: %s",
                error
            )

            return {}

    # =====================================================
    # SALES PREDICTION
    # =====================================================

    @staticmethod
    def get_sales_prediction():

        file = PredictionService.find_file(

            [
                "sales_summary.json",
                "sales_prediction.json",
                "sales_report.json",
                "sales_summary_report.json"
            ],

            [
                PredictionService.REPORT_DIR,
                PredictionService.OUTPUT_DIR
            ]

        )

        if file is None:

            return {

                "status":
                    "success",

                "module":
                    "Sales Prediction",

                "available":
                    False,

                "message":
                    "Sales prediction report not available.",

                "records":
                    0,

                "total_sales":
                    0.0,

                "revenue":
                    0.0,

                "profit":
                    0.0,

                "prediction":
                    0.0,

                "predicted_sales":
                    0.0,

                "model":
                    "Unknown",

                "growth":
                    0.0,

                "average_sales":
                    0.0,

                "best_category":
                    "N/A",

                "sales_trend":
                    [],

                "category_sales":
                    [],

                "region_sales":
                    []

            }

        data = PredictionService.read_json(
            file
        )

        revenue = (

            data.get("total_sales")

            or data.get("Revenue")

            or data.get("revenue")

            or data.get("sales")

            or 0

        )

        profit = (

            data.get("profit")

            or data.get("Profit")

            or 0

        )

        prediction = (

            data.get("prediction")

            or data.get("predicted_sales")

            or data.get("Predicted Sales")

            or data.get("sales_prediction")

            or 0

        )

        model = (

            data.get("model")

            or data.get("Model")

            or data.get("best_model")

            or "Unknown"

        )

        growth = (

            data.get("growth")

            or data.get("Growth")

            or data.get("growth_rate")

            or 0

        )

        sales_trend = (

            data.get("sales_trend")

            or data.get("Sales Trend")

            or []

        )

        category_sales = (

            data.get("category_sales")

            or data.get("Category Sales")

            or []

        )

        region_sales = (

            data.get("region_sales")

            or data.get("Region Sales")

            or []

        )

        if not isinstance(
            sales_trend,
            list
        ):

            sales_trend = []

        if not isinstance(
            category_sales,
            list
        ):

            category_sales = []

        if not isinstance(
            region_sales,
            list
        ):

            region_sales = []

        revenue = PredictionService.safe_float(
            revenue
        )

        profit = PredictionService.safe_float(
            profit
        )

        prediction = PredictionService.safe_float(
            prediction
        )

        growth = PredictionService.safe_float(
            growth
        )

        record_count = (

            data.get("records")

            or data.get("record_count")

            or data.get("rows")

            or 9994

        )

        record_count = max(

            PredictionService.safe_int(
                record_count,
                9994
            ),

            1

        )

        average_sales = round(

            revenue
            /
            record_count,

            2

        )

        best_category = "N/A"

        valid_categories = [

            item

            for item in category_sales

            if isinstance(
                item,
                dict
            )

        ]

        if valid_categories:

            try:

                best = max(

                    valid_categories,

                    key=lambda item:

                    PredictionService.safe_float(

                        item.get(

                            "sales",

                            item.get(
                                "value",
                                0
                            )

                        )

                    )

                )

                best_category = (

                    best.get(
                        "category"
                    )

                    or

                    best.get(
                        "Category"
                    )

                    or

                    "N/A"

                )

            except Exception:

                best_category = "N/A"

        return {

            "status":
                "success",

            "module":
                "Sales Prediction",

            "available":
                True,

            "source":
                str(file),

            "records":
                record_count,

            "total_sales":
                revenue,

            "revenue":
                revenue,

            "profit":
                profit,

            "prediction":
                prediction,

            "predicted_sales":
                prediction,

            "model":
                model,

            "growth":
                growth,

            "average_sales":
                average_sales,

            "best_category":
                best_category,

            "sales_trend":
                sales_trend,

            "category_sales":
                category_sales,

            "region_sales":
                region_sales

        }

    # =====================================================
    # FEATURE IMPORTANCE
    # =====================================================

    @staticmethod
    def get_feature_importance():

        files = [

            PredictionService.REPORT_DIR
            / "feature_importance.csv",

            PredictionService.OUTPUT_DIR
            / "feature_importance.csv"

        ]

        for file in files:

            if not file.exists():
                continue

            try:

                df = pd.read_csv(
                    file
                )

                if df.empty:
                    return []

                df.columns = [

                    str(column)
                    .strip()
                    .lower()
                    .replace(
                        " ",
                        "_"
                    )

                    for column in df.columns

                ]

                feature_column = None

                importance_column = None

                for column in [

                    "feature",
                    "features",
                    "feature_name",
                    "name"

                ]:

                    if column in df.columns:

                        feature_column = column

                        break

                for column in [

                    "importance",
                    "feature_importance",
                    "importance_score",
                    "score"

                ]:

                    if column in df.columns:

                        importance_column = column

                        break

                if (
                    feature_column is None
                    or
                    importance_column is None
                ):

                    return []

                df[
                    importance_column
                ] = pd.to_numeric(

                    df[
                        importance_column
                    ],

                    errors="coerce"

                )

                df = df.dropna(

                    subset=[

                        importance_column

                    ]

                )

                df = df.sort_values(

                    importance_column,

                    ascending=False

                )

                result = []

                for _, row in (
                    df.head(20).iterrows()
                ):

                    result.append({

                        "feature":
                            str(
                                row[
                                    feature_column
                                ]
                            ),

                        "importance":
                            PredictionService.safe_float(

                                row[
                                    importance_column
                                ]

                            )

                    })

                return result

            except Exception as error:

                logger.warning(
                    "Feature importance error: %s",
                    error
                )

        return []

    # =====================================================
    # INVENTORY PREDICTION
    # =====================================================

    @staticmethod
    def get_inventory_prediction():

        file = PredictionService.find_file(

            [
                "inventory_predictions.csv",
                "inventory_prediction.csv",
                "inventory_summary.csv"
            ],

            [
                PredictionService.OUTPUT_DIR,
                PredictionService.REPORT_DIR
            ]

        )

        if file is None:

            return {

                "status":
                    "success",

                "module":
                    "Inventory Prediction",

                "available":
                    False,

                "records":
                    0,

                "inventory":
                    [],

                "total_inventory":
                    0.0,

                "total_demand":
                    0.0

            }

        try:

            df = pd.read_csv(
                file
            )

            if df.empty:

                return {

                    "status":
                        "success",

                    "module":
                        "Inventory Prediction",

                    "available":
                        True,

                    "records":
                        0,

                    "inventory":
                        [],

                    "total_inventory":
                        0.0,

                    "total_demand":
                        0.0

                }

            df.columns = [

                str(column).strip()

                for column in df.columns

            ]

            quantity_column = (
                PredictionService.find_column(

                    df.columns,

                    exact_names=[

                        "quantity",
                        "inventory",
                        "stock",
                        "predicted inventory"

                    ],

                    contains_names=[

                        "quantity",
                        "inventory",
                        "stock"

                    ]

                )
            )

            demand_column = (
                PredictionService.find_column(

                    df.columns,

                    exact_names=[

                        "demand",
                        "predicted demand"

                    ],

                    contains_names=[

                        "demand"

                    ]

                )
            )

            total_inventory = 0.0

            total_demand = 0.0

            if quantity_column:

                total_inventory = (
                    PredictionService.safe_float(

                        pd.to_numeric(

                            df[
                                quantity_column
                            ],

                            errors="coerce"

                        ).sum()

                    )
                )

            if demand_column:

                total_demand = (
                    PredictionService.safe_float(

                        pd.to_numeric(

                            df[
                                demand_column
                            ],

                            errors="coerce"

                        ).sum()

                    )
                )

            records = (
                df.head(20)
                .to_dict(
                    orient="records"
                )
            )

            return {

                "status":
                    "success",

                "module":
                    "Inventory Prediction",

                "available":
                    True,

                "source":
                    str(file),

                "records":
                    len(df),

                "inventory":
                    records,

                "total_inventory":
                    total_inventory,

                "total_demand":
                    total_demand

            }

        except Exception as error:

            logger.exception(
                "Inventory prediction error"
            )

            return {

                "status":
                    "error",

                "module":
                    "Inventory Prediction",

                "message":
                    str(error),

                "inventory":
                    [],

                "total_inventory":
                    0.0,

                "total_demand":
                    0.0

            }

    # =====================================================
    # CUSTOMER SEGMENTATION
    # =====================================================

    @staticmethod
    def get_customer_segments():

        file = PredictionService.find_file(

            [
                "customer_segments.csv",
                "customer_segment.csv",
                "customer_segmentation.csv"
            ],

            [
                PredictionService.OUTPUT_DIR,
                PredictionService.REPORT_DIR
            ]

        )

        if file is None:

            return {

                "status":
                    "success",

                "module":
                    "Customer Segmentation",

                "available":
                    False,

                "customers":
                    0,

                "segments":
                    {},

                "clusters":
                    {},

                "customer_segments":
                    [],

                "segment_count":
                    0,

                "largest_segment":
                    None,

                "highest_spending_segment":
                    None,

                "data":
                    []

            }

        try:

            df = pd.read_csv(
                file
            )

            if df.empty:

                return {

                    "status":
                        "success",

                    "module":
                        "Customer Segmentation",

                    "available":
                        True,

                    "customers":
                        0,

                    "segments":
                        {},

                    "clusters":
                        {},

                    "customer_segments":
                        [],

                    "segment_count":
                        0,

                    "largest_segment":
                        None,

                    "highest_spending_segment":
                        None,

                    "data":
                        []

                }

            df.columns = [

                str(column).strip()

                for column in df.columns

            ]

            cluster_column = (
                PredictionService.find_column(

                    df.columns,

                    exact_names=[

                        "cluster",
                        "cluster label",
                        "cluster id",
                        "segment",
                        "segment label"

                    ],

                    contains_names=[

                        "cluster",
                        "segment"

                    ]

                )
            )

            age_column = (
                PredictionService.find_column(

                    df.columns,

                    exact_names=[

                        "age",
                        "customer age",
                        "customer_age"

                    ],

                    contains_names=[

                        "customer age",
                        "age"

                    ]

                )
            )

            income_column = (
                PredictionService.find_column(

                    df.columns,

                    exact_names=[

                        "annual income",
                        "annual income k",
                        "annual income k$",
                        "annual income (k$)",
                        "income",
                        "income k",
                        "income k$",
                        "income (k$)"

                    ],

                    contains_names=[

                        "annual income",
                        "income"

                    ]

                )
            )

            spending_column = (
                PredictionService.find_column(

                    df.columns,

                    exact_names=[

                        "spending score",
                        "spending score 1 100",
                        "spending score (1 100)",
                        "spending_score",
                        "spending"

                    ],

                    contains_names=[

                        "spending score",
                        "spending"

                    ]

                )
            )

            if cluster_column is None:

                return {

                    "status":
                        "error",

                    "module":
                        "Customer Segmentation",

                    "available":
                        False,

                    "message":
                        "Cluster column not found.",

                    "customers":
                        0,

                    "segments":
                        {},

                    "clusters":
                        {},

                    "customer_segments":
                        [],

                    "data":
                        []

                }

            for column in [

                age_column,
                income_column,
                spending_column

            ]:

                if column:

                    df[column] = pd.to_numeric(

                        df[column],

                        errors="coerce"

                    )

            df[
                cluster_column
            ] = (

                df[
                    cluster_column
                ]
                .astype(str)
                .str.strip()

            )

            invalid_values = {

                "",
                "nan",
                "none",
                "null"

            }

            df = df[

                ~df[
                    cluster_column
                ]
                .str.lower()
                .isin(
                    invalid_values
                )

            ].copy()

            distribution = (

                df[
                    cluster_column
                ]
                .value_counts()
                .sort_index()

            )

            customer_segments = []

            for cluster_value, count in (
                distribution.items()
            ):

                cluster_df = df[

                    df[
                        cluster_column
                    ]
                    ==
                    cluster_value

                ]

                average_age = 0.0

                average_income = 0.0

                average_spending = 0.0

                if age_column:

                    average_age = (
                        cluster_df[
                            age_column
                        ].mean()
                    )

                if income_column:

                    average_income = (
                        cluster_df[
                            income_column
                        ].mean()
                    )

                if spending_column:

                    average_spending = (
                        cluster_df[
                            spending_column
                        ].mean()
                    )

                average_age = (

                    0.0

                    if pd.isna(
                        average_age
                    )

                    else average_age

                )

                average_income = (

                    0.0

                    if pd.isna(
                        average_income
                    )

                    else average_income

                )

                average_spending = (

                    0.0

                    if pd.isna(
                        average_spending
                    )

                    else average_spending

                )

                try:

                    cluster_number = int(

                        float(
                            cluster_value
                        )

                    )

                except (
                    ValueError,
                    TypeError
                ):

                    cluster_number = (
                        len(
                            customer_segments
                        )
                    )

                customer_segments.append({

                    "cluster":
                        cluster_number,

                    "segment":
                        f"Cluster {cluster_number}",

                    "name":
                        f"Cluster {cluster_number}",

                    "customers":
                        PredictionService.safe_int(
                            count
                        ),

                    "value":
                        PredictionService.safe_int(
                            count
                        ),

                    "average_age":
                        PredictionService.safe_float(
                            average_age
                        ),

                    "average_income":
                        PredictionService.safe_float(
                            average_income
                        ),

                    "average_spending_score":
                        PredictionService.safe_float(
                            average_spending
                        )

                })

            customer_segments.sort(

                key=lambda item:
                item["cluster"]

            )

            cluster_counts = {

                str(cluster):
                    PredictionService.safe_int(
                        count
                    )

                for cluster, count
                in distribution.items()

            }

            sample_data = (
                df.head(20)
                .to_dict(
                    orient="records"
                )
            )

            cleaned_sample_data = []

            for row in sample_data:

                cleaned_row = {}

                for key, value in row.items():

                    if pd.isna(value):

                        cleaned_row[
                            key
                        ] = None

                    elif hasattr(
                        value,
                        "item"
                    ):

                        try:

                            cleaned_row[
                                key
                            ] = value.item()

                        except Exception:

                            cleaned_row[
                                key
                            ] = str(value)

                    else:

                        cleaned_row[
                            key
                        ] = value

                cleaned_sample_data.append(
                    cleaned_row
                )

            largest_segment = (

                max(

                    customer_segments,

                    key=lambda item:
                    item["customers"]

                )

                if customer_segments

                else None

            )

            highest_spending = (

                max(

                    customer_segments,

                    key=lambda item:
                    item[
                        "average_spending_score"
                    ]

                )

                if customer_segments

                else None

            )

            return {

                "status":
                    "success",

                "module":
                    "Customer Segmentation",

                "available":
                    True,

                "source":
                    str(file),

                "customers":
                    len(df),

                "segments":
                    cluster_counts,

                "clusters":
                    cluster_counts,

                "customer_segments":
                    customer_segments,

                "segment_count":
                    len(
                        customer_segments
                    ),

                "largest_segment":
                    largest_segment,

                "highest_spending_segment":
                    highest_spending,

                "data":
                    cleaned_sample_data

            }

        except Exception as error:

            logger.exception(
                "Customer segmentation error"
            )

            return {

                "status":
                    "error",

                "module":
                    "Customer Segmentation",

                "available":
                    False,

                "message":
                    str(error),

                "customers":
                    0,

                "segments":
                    {},

                "clusters":
                    {},

                "customer_segments":
                    [],

                "segment_count":
                    0,

                "largest_segment":
                    None,

                "highest_spending_segment":
                    None,

                "data":
                    []

            }

    # =====================================================
    # FORECAST SUMMARY FALLBACK
    # =====================================================

    @staticmethod
    def get_forecast_summary():

        file = (
            PredictionService.REPORT_DIR
            / "forecast_summary.json"
        )

        if not file.exists():

            return None

        try:

            data = (
                PredictionService
                .read_json(file)
            )

            forecast = data.get(
                "forecast",
                []
            )

            if not isinstance(
                forecast,
                list
            ):

                return None

            cleaned_forecast = []

            for item in forecast:

                if not isinstance(
                    item,
                    dict
                ):

                    continue

                date_value = (

                    item.get("date")

                    or item.get("ds")

                    or ""

                )

                actual = (

                    item.get("actual")

                    if item.get("actual")
                    is not None

                    else item.get(
                        "actual_demand"
                    )

                )

                forecast_value = (

                    item.get("forecast")

                    if item.get("forecast")
                    is not None

                    else item.get(
                        "yhat",
                        0
                    )

                )

                lower = (

                    item.get("lower")

                    if item.get("lower")
                    is not None

                    else item.get(
                        "yhat_lower"
                    )

                )

                upper = (

                    item.get("upper")

                    if item.get("upper")
                    is not None

                    else item.get(
                        "yhat_upper"
                    )

                )

                cleaned_forecast.append({

                    "date":
                        str(date_value),

                    "forecast":
                        (
                            None
                            if forecast_value is None
                            else PredictionService.safe_float(
                                forecast_value
                            )
                        ),

                    "actual":
                        (
                            None
                            if actual is None
                            else PredictionService.safe_float(
                                actual
                            )
                        ),

                    "actual_demand":
                        (
                            None
                            if actual is None
                            else PredictionService.safe_float(
                                actual
                            )
                        ),

                    "lower":
                        (
                            None
                            if lower is None
                            else PredictionService.safe_float(
                                lower
                            )
                        ),

                    "upper":
                        (
                            None
                            if upper is None
                            else PredictionService.safe_float(
                                upper
                            )
                        ),

                    "yhat_lower":
                        (
                            None
                            if lower is None
                            else PredictionService.safe_float(
                                lower
                            )
                        ),

                    "yhat_upper":
                        (
                            None
                            if upper is None
                            else PredictionService.safe_float(
                                upper
                            )
                        )

                })

            return {

                "model":
                    data.get(
                        "model",
                        "Facebook Prophet"
                    ),

                "forecast":
                    cleaned_forecast

            }

        except Exception as error:

            logger.warning(
                "Forecast summary error: %s",
                error
            )

            return None

    # =====================================================
    # DEMAND FORECAST
    # =====================================================

    @staticmethod
    def get_forecast():

        file = PredictionService.find_file(

            [

                "sales_forecast.csv",

                "forecast.csv",

                "demand_forecast.csv",

                "demand_forecasting.csv"

            ],

            [

                PredictionService.OUTPUT_DIR,

                PredictionService.REPORT_DIR

            ]

        )

        # =================================================
        # CSV NOT FOUND
        # =================================================

        if file is None:

            summary = (
                PredictionService
                .get_forecast_summary()
            )

            if summary is None:

                return {

                    "status":
                        "success",

                    "module":
                        "Demand Forecasting",

                    "available":
                        False,

                    "model":
                        "Unknown",

                    "forecast":
                        [],

                    "records":
                        0,

                    "historical_records":
                        0,

                    "future_records":
                        0,

                    "forecast_points":
                        0,

                    "average_forecast":
                        0.0,

                    "latest_forecast":
                        0.0,

                    "minimum_forecast":
                        0.0,

                    "maximum_forecast":
                        0.0,

                    "growth":
                        0.0

                }

            forecast = summary.get(
                "forecast",
                []
            )

            values = [

                PredictionService.safe_float(
                    item.get("forecast")
                )

                for item in forecast

                if item.get(
                    "forecast"
                ) is not None

            ]

            if values:

                average_forecast = round(

                    sum(values)
                    /
                    len(values),

                    2

                )

                latest_forecast = values[-1]

                minimum_forecast = min(
                    values
                )

                maximum_forecast = max(
                    values
                )

            else:

                average_forecast = 0.0

                latest_forecast = 0.0

                minimum_forecast = 0.0

                maximum_forecast = 0.0

            growth = 0.0

            if len(values) >= 2:

                first_value = values[0]

                last_value = values[-1]

                if first_value != 0:

                    growth = round(

                        (

                            (
                                last_value
                                -
                                first_value
                            )

                            /

                            abs(
                                first_value
                            )

                        )
                        * 100,

                        2

                    )

            historical_records = sum(

                1

                for item in forecast

                if item.get(
                    "actual"
                ) is not None

            )

            future_records = (

                len(forecast)
                -
                historical_records

            )

            return {

                "status":
                    "success",

                "module":
                    "Demand Forecasting",

                "available":
                    True,

                "source":
                    str(
                        PredictionService.REPORT_DIR
                        / "forecast_summary.json"
                    ),

                "model":
                    summary.get(
                        "model",
                        "Facebook Prophet"
                    ),

                "records":
                    len(forecast),

                "historical_records":
                    historical_records,

                "future_records":
                    future_records,

                "forecast_points":
                    len(forecast),

                "forecast":
                    forecast,

                "average_forecast":
                    average_forecast,

                "latest_forecast":
                    latest_forecast,

                "minimum_forecast":
                    minimum_forecast,

                "maximum_forecast":
                    maximum_forecast,

                "growth":
                    growth

            }

        # =================================================
        # READ CSV
        # =================================================

        try:

            logger.info(
                "Reading forecast file: %s",
                file
            )

            df = pd.read_csv(
                file
            )

            logger.info(
                "Forecast columns: %s",
                list(df.columns)
            )

            if df.empty:

                return {

                    "status":
                        "success",

                    "module":
                        "Demand Forecasting",

                    "available":
                        True,

                    "source":
                        str(file),

                    "model":
                        "Facebook Prophet",

                    "forecast":
                        [],

                    "records":
                        0,

                    "historical_records":
                        0,

                    "future_records":
                        0,

                    "forecast_points":
                        0,

                    "average_forecast":
                        0.0,

                    "latest_forecast":
                        0.0,

                    "minimum_forecast":
                        0.0,

                    "maximum_forecast":
                        0.0,

                    "growth":
                        0.0

                }

            # =================================================
            # CLEAN COLUMN NAMES
            # =================================================

            df.columns = [

                str(column).strip()

                for column in df.columns

            ]

            # =================================================
            # DETECT DATE
            # =================================================

            date_column = (
                PredictionService.find_column(

                    df.columns,

                    exact_names=[

                        "ds",
                        "date",
                        "datetime",
                        "timestamp"

                    ],

                    contains_names=[

                        "date",
                        "datetime",
                        "timestamp"

                    ]

                )
            )

            # =================================================
            # DETECT FORECAST
            # =================================================

            prediction_column = (
                PredictionService.find_column(

                    df.columns,

                    exact_names=[

                        "yhat",
                        "forecast",
                        "prediction",
                        "predicted demand",
                        "predicted sales"

                    ],

                    contains_names=[

                        "yhat",
                        "forecast",
                        "prediction",
                        "predicted demand",
                        "predicted sales"

                    ]

                )
            )

            # =================================================
            # DETECT LOWER
            # =================================================

            lower_column = (
                PredictionService.find_column(

                    df.columns,

                    exact_names=[

                        "yhat lower",
                        "yhat_lower",
                        "lower",
                        "lower bound",
                        "lower_bound",
                        "forecast lower",
                        "prediction lower"

                    ],

                    contains_names=[

                        "yhat lower",
                        "lower bound",
                        "forecast lower",
                        "prediction lower",
                        "lower"

                    ]

                )
            )

            # =================================================
            # DETECT UPPER
            # =================================================

            upper_column = (
                PredictionService.find_column(

                    df.columns,

                    exact_names=[

                        "yhat upper",
                        "yhat_upper",
                        "upper",
                        "upper bound",
                        "upper_bound",
                        "forecast upper",
                        "prediction upper"

                    ],

                    contains_names=[

                        "yhat upper",
                        "upper bound",
                        "forecast upper",
                        "prediction upper",
                        "upper"

                    ]

                )
            )

            # =================================================
            # DETECT ACTUAL
            # =================================================

            actual_column = (
                PredictionService.find_column(

                    df.columns,

                    exact_names=[

                        "y",
                        "actual",
                        "actual sales",
                        "actual demand",
                        "actual value",
                        "actual_demand",
                        "actual_sales"

                    ],

                    contains_names=[

                        "actual sales",
                        "actual demand",
                        "actual value",
                        "actual"

                    ]

                )
            )

            logger.info(
                "Detected forecast columns:"
            )

            logger.info(
                "Date: %s",
                date_column
            )

            logger.info(
                "Forecast: %s",
                prediction_column
            )

            logger.info(
                "Actual: %s",
                actual_column
            )

            logger.info(
                "Lower: %s",
                lower_column
            )

            logger.info(
                "Upper: %s",
                upper_column
            )

            if date_column is None:

                raise ValueError(
                    "Forecast date column could not be detected."
                )

            if prediction_column is None:

                raise ValueError(
                    "Forecast column could not be detected."
                )

            # =================================================
            # NORMALIZE DATE
            # =================================================

            df[date_column] = pd.to_datetime(

                df[date_column],

                errors="coerce"

            )

            # =================================================
            # NORMALIZE NUMERIC COLUMNS
            # =================================================

            numeric_columns = [

                prediction_column,

                actual_column,

                lower_column,

                upper_column

            ]

            for column in numeric_columns:

                if column:

                    df[column] = pd.to_numeric(

                        df[column],

                        errors="coerce"

                    )

            # =================================================
            # REMOVE INVALID DATES
            # =================================================

            df = df[

                df[date_column].notna()

            ].copy()

            # =================================================
            # SORT
            # =================================================

            df = df.sort_values(

                date_column

            ).reset_index(

                drop=True

            )

            # =================================================
            # FALLBACK ACTUAL DEMAND
            #
            # If Prophet CSV has no actual values, load
            # actual monthly sales from the original dataset.
            # =================================================

            actual_map = {}

            actual_values_exist = False

            if actual_column:

                actual_values_exist = (

                    df[
                        actual_column
                    ]
                    .notna()
                    .any()

                )

            if not actual_values_exist:

                logger.info(

                    "Forecast file does not contain "
                    "historical actual values. "
                    "Attempting to reconstruct actual demand."

                )

                actual_map = (

                    PredictionService
                    .get_actual_monthly_sales()

                )

                if actual_map:

                    logger.info(

                        "Actual demand fallback loaded: %s months",

                        len(actual_map)

                    )

            # =================================================
            # BUILD COMPLETE FORECAST DATA
            # =================================================

            forecast = []

            for _, row in df.iterrows():

                date_value = row.get(
                    date_column
                )

                if pd.isna(
                    date_value
                ):

                    continue

                timestamp = pd.Timestamp(
                    date_value
                )

                formatted_date = (
                    timestamp.strftime(
                        "%Y-%m-%d"
                    )
                )

                # ---------------------------------------------
                # FORECAST
                # ---------------------------------------------

                raw_forecast = row.get(
                    prediction_column
                )

                forecast_value = (

                    None

                    if pd.isna(
                        raw_forecast
                    )

                    else PredictionService.safe_float(
                        raw_forecast
                    )

                )

                # ---------------------------------------------
                # ACTUAL
                # ---------------------------------------------

                actual_value = None

                if actual_column:

                    raw_actual = row.get(
                        actual_column
                    )

                    if not pd.isna(
                        raw_actual
                    ):

                        actual_value = (
                            PredictionService.safe_float(
                                raw_actual
                            )
                        )

                # ---------------------------------------------
                # FALLBACK ACTUAL
                # ---------------------------------------------

                if actual_value is None:

                    actual_value = (
                        actual_map.get(
                            formatted_date
                        )
                    )

                # ---------------------------------------------
                # LOWER
                # ---------------------------------------------

                lower_value = None

                if lower_column:

                    raw_lower = row.get(
                        lower_column
                    )

                    if not pd.isna(
                        raw_lower
                    ):

                        lower_value = (
                            PredictionService.safe_float(
                                raw_lower
                            )
                        )

                # ---------------------------------------------
                # UPPER
                # ---------------------------------------------

                upper_value = None

                if upper_column:

                    raw_upper = row.get(
                        upper_column
                    )

                    if not pd.isna(
                        raw_upper
                    ):

                        upper_value = (
                            PredictionService.safe_float(
                                raw_upper
                            )
                        )

                # ---------------------------------------------
                # FINAL API FORMAT
                # ---------------------------------------------

                forecast.append({

                    "date":
                        formatted_date,

                    "forecast":
                        forecast_value,

                    "actual":
                        actual_value,

                    "actual_demand":
                        actual_value,

                    "lower":
                        lower_value,

                    "upper":
                        upper_value,

                    "yhat":
                        forecast_value,

                    "yhat_lower":
                        lower_value,

                    "yhat_upper":
                        upper_value

                })

            # =================================================
            # LIMIT
            # =================================================

            forecast = forecast[:100]

            # =================================================
            # FORECAST VALUES
            # =================================================

            forecast_values = [

                item["forecast"]

                for item in forecast

                if item.get(
                    "forecast"
                ) is not None

            ]

            # =================================================
            # SUMMARY
            # =================================================

            if forecast_values:

                average_forecast = round(

                    sum(
                        forecast_values
                    )
                    /
                    len(
                        forecast_values
                    ),

                    2

                )

                latest_forecast = (
                    forecast_values[-1]
                )

                minimum_forecast = min(
                    forecast_values
                )

                maximum_forecast = max(
                    forecast_values
                )

            else:

                average_forecast = 0.0

                latest_forecast = 0.0

                minimum_forecast = 0.0

                maximum_forecast = 0.0

            # =================================================
            # GROWTH
            # =================================================

            growth = 0.0

            if len(
                forecast_values
            ) >= 2:

                first_value = (
                    forecast_values[0]
                )

                last_value = (
                    forecast_values[-1]
                )

                if first_value != 0:

                    growth = round(

                        (

                            (
                                last_value
                                -
                                first_value
                            )

                            /

                            abs(
                                first_value
                            )

                        )
                        * 100,

                        2

                    )

            # =================================================
            # HISTORICAL / FUTURE COUNTS
            # =================================================

            historical_records = sum(

                1

                for item in forecast

                if (

                    item.get(
                        "actual"
                    ) is not None

                )

            )

            future_records = (

                len(forecast)
                -
                historical_records

            )

            # =================================================
            # RESPONSE
            # =================================================

            response = {

                "status":
                    "success",

                "module":
                    "Demand Forecasting",

                "available":
                    True,

                "source":
                    str(file),

                "model":
                    "Facebook Prophet",

                "records":
                    len(df),

                "historical_records":
                    historical_records,

                "future_records":
                    future_records,

                "forecast_points":
                    len(forecast),

                "forecast":
                    forecast,

                "average_forecast":
                    average_forecast,

                "latest_forecast":
                    latest_forecast,

                "minimum_forecast":
                    minimum_forecast,

                "maximum_forecast":
                    maximum_forecast,

                "growth":
                    growth

            }

            logger.info(
                "Forecast completed successfully."
            )

            logger.info(
                "Total records: %s",
                len(df)
            )

            logger.info(
                "Historical records: %s",
                historical_records
            )

            logger.info(
                "Future records: %s",
                future_records
            )

            logger.info(
                "Frontend forecast points: %s",
                len(forecast)
            )

            logger.info(
                "Actual fallback records: %s",
                len(actual_map)
            )

            return response

        except Exception as error:

            logger.exception(
                "Forecast error"
            )

            return {

                "status":
                    "error",

                "module":
                    "Demand Forecasting",

                "available":
                    False,

                "message":
                    str(error),

                "model":
                    "Facebook Prophet",

                "forecast":
                    [],

                "records":
                    0,

                "historical_records":
                    0,

                "future_records":
                    0,

                "forecast_points":
                    0,

                "average_forecast":
                    0.0,

                "latest_forecast":
                    0.0,

                "minimum_forecast":
                    0.0,

                "maximum_forecast":
                    0.0,

                "growth":
                    0.0

            }

    # =====================================================
    # ALL PREDICTIONS
    # =====================================================

    @staticmethod
    def get_all_predictions():

        return {

            "status":
                "success",

            "sales":
                PredictionService
                .get_sales_prediction(),

            "inventory":
                PredictionService
                .get_inventory_prediction(),

            "forecast":
                PredictionService
                .get_forecast(),

            "customer":
                PredictionService
                .get_customer_segments()

        }

    # =====================================================
    # SALES REPORT
    # =====================================================

    @staticmethod
    def get_sales_report():

        return (
            PredictionService
            .get_sales_prediction()
        )

    # =====================================================
    # HEALTH
    # =====================================================

    @staticmethod
    def health():

        return {

            "service":
                "PredictionService",

            "status":
                "healthy",

            "directories": {

                "reports":
                    str(
                        PredictionService
                        .REPORT_DIR
                    ),

                "outputs":
                    str(
                        PredictionService
                        .OUTPUT_DIR
                    )

            },

            "files": {

                "sales":
                    (
                        PredictionService.find_file(

                            [
                                "sales_summary.json",
                                "sales_prediction.json",
                                "sales_report.json"
                            ],

                            [
                                PredictionService.REPORT_DIR,
                                PredictionService.OUTPUT_DIR
                            ]

                        )

                        is not None

                    ),

                "inventory":
                    (
                        PredictionService.find_file(

                            [
                                "inventory_predictions.csv",
                                "inventory_prediction.csv"
                            ],

                            [
                                PredictionService.OUTPUT_DIR,
                                PredictionService.REPORT_DIR
                            ]

                        )

                        is not None

                    ),

                "forecast":
                    (
                        PredictionService.find_file(

                            [
                                "sales_forecast.csv",
                                "forecast.csv",
                                "demand_forecast.csv",
                                "demand_forecasting.csv"
                            ],

                            [
                                PredictionService.OUTPUT_DIR,
                                PredictionService.REPORT_DIR
                            ]

                        )

                        is not None

                        or

                        (
                            PredictionService.REPORT_DIR
                            / "forecast_summary.json"
                        ).exists()

                    ),

                "actual_sales_dataset":
                    (
                        PredictionService
                        .find_actual_sales_dataset()
                        is not None
                    ),

                "customer":
                    (
                        PredictionService.find_file(

                            [
                                "customer_segments.csv",
                                "customer_segment.csv",
                                "customer_segmentation.csv"
                            ],

                            [
                                PredictionService.OUTPUT_DIR,
                                PredictionService.REPORT_DIR
                            ]

                        )

                        is not None

                    )

            }

        }

