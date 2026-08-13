
"""
Enterprise AI Business Decision Intelligence Platform

Sales Prediction Engine

Author : Feroz Ali
"""

import warnings

warnings.filterwarnings("ignore")

import json
import logging
import joblib
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from pathlib import Path
from datetime import datetime

# ==========================================================
# Machine Learning
# ==========================================================

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from sklearn.ensemble import RandomForestRegressor


# ==========================================================
# Optional Models
# ==========================================================

try:

    from xgboost import XGBRegressor

    XGBOOST_AVAILABLE = True

except Exception:

    XGBOOST_AVAILABLE = False


try:

    from lightgbm import LGBMRegressor

    LIGHTGBM_AVAILABLE = True

except Exception:

    LIGHTGBM_AVAILABLE = False


# ==========================================================
# SHAP
# ==========================================================

try:

    import shap

    SHAP_AVAILABLE = True

except Exception:

    SHAP_AVAILABLE = False


# ==========================================================
# Project Imports
# ==========================================================

from config.settings import settings

from config.logger import get_logger

from data.data_loader import DataLoader

from data.preprocessing import DataPreprocessor

from data.feature_engineering import FeatureEngineering


logger = get_logger("SalesPrediction")


# ==========================================================
# Sales Prediction Class
# ==========================================================

class SalesPrediction:

    """
    Enterprise Sales Prediction Engine.

    Responsibilities:

    - Load enterprise sales data
    - Clean and engineer features
    - Train ML models
    - Compare models
    - Evaluate best model
    - Save best model
    - Generate predictions
    - Generate feature importance
    - Generate SHAP explanation
    - Generate business summary
    """

    # ======================================================
    # INITIALIZATION
    # ======================================================

    def __init__(self):

        logger.info(
            "Initializing Sales Prediction Engine"
        )

        # --------------------------------------------------
        # Data components
        # --------------------------------------------------

        self.loader = DataLoader()

        self.processor = DataPreprocessor()

        self.engineer = FeatureEngineering()

        # --------------------------------------------------
        # Model state
        # --------------------------------------------------

        self.models = {}

        self.best_model = None

        self.best_model_name = ""

        self.best_score = -999999.0

        self.preprocessor = None

        # --------------------------------------------------
        # Dataset state
        # --------------------------------------------------

        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

        self.feature_columns = []

        # --------------------------------------------------
        # Enterprise paths
        # --------------------------------------------------

        self.model_dir = Path(
            settings.MODEL_DIR
        )

        self.output_dir = Path(
            settings.OUTPUT_DIR
        )

        self.report_dir = Path(
            settings.REPORT_DIR
        )

        self.figure_dir = Path(
            "figures"
        )

        # --------------------------------------------------
        # Create directories
        # --------------------------------------------------

        self.model_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.report_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.figure_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        logger.info(
            "Sales Prediction Engine Ready"
        )

    # ======================================================
    # LOAD DATASET
    # ======================================================

    def load_dataset(self):

        logger.info(
            "Loading Sales Dataset"
        )

        df = self.loader.load_superstore()

        if df is None:

            raise ValueError(
                "Sales dataset could not be loaded."
            )

        if df.empty:

            raise ValueError(
                "Sales dataset is empty."
            )

        # --------------------------------------------------
        # Cleaning
        # --------------------------------------------------

        df = self.processor.clean_dataframe(
            df
        )

        # --------------------------------------------------
        # Dates
        # --------------------------------------------------

        date_columns = []

        for column in [
            "Order Date",
            "Ship Date",
        ]:

            if column in df.columns:

                date_columns.append(
                    column
                )

        if date_columns:

            df = self.processor.convert_dates(
                df,
                date_columns
            )

        # --------------------------------------------------
        # Feature engineering
        # --------------------------------------------------

        df = self.engineer.full_pipeline(
            df
        )

        logger.info(
            "Sales Dataset Shape: %s",
            df.shape
        )

        return df

    # ======================================================
    # PREPARE DATASET
    # ======================================================

    def prepare_dataset(
        self,
        force=False
    ):

        """
        Prepare training/testing data only once.

        This prevents recreating a different train/test
        split every time a model is trained.
        """

        if (
            not force
            and self.X_train is not None
            and self.X_test is not None
        ):

            return (
                self.X_train,
                self.X_test,
                self.y_train,
                self.y_test
            )

        logger.info(
            "Preparing Sales Dataset"
        )

        df = self.load_dataset()

        target = "Sales"

        if target not in df.columns:

            raise ValueError(
                "Sales target column is missing."
            )

        # --------------------------------------------------
        # Remove target and leakage columns
        # --------------------------------------------------

        remove_columns = [

            "Sales",

            # Leakage
            "Profit",
            "Product Sales",
            "Customer Sales",
            "Average Price",
            "Profit Margin",

            # Identifiers / text
            "Order ID",
            "Customer Name",
            "Product Name",

        ]

        remove_columns = [

            column

            for column in remove_columns

            if column in df.columns

        ]

        X = df.drop(
            columns=remove_columns,
            errors="ignore"
        )

        y = pd.to_numeric(
            df[target],
            errors="coerce"
        )

        # --------------------------------------------------
        # Remove invalid targets
        # --------------------------------------------------

        valid_rows = y.notna()

        X = X.loc[
            valid_rows
        ].reset_index(
            drop=True
        )

        y = y.loc[
            valid_rows
        ].reset_index(
            drop=True
        )

        # --------------------------------------------------
        # Remove datetime columns
        # --------------------------------------------------

        datetime_columns = X.select_dtypes(
            include=[
                "datetime64[ns]",
                "datetime64[ns, UTC]"
            ]
        ).columns.tolist()

        X = X.drop(
            columns=datetime_columns,
            errors="ignore"
        )

        # --------------------------------------------------
        # Store feature names
        # --------------------------------------------------

        self.feature_columns = (
            X.columns.tolist()
        )

        # --------------------------------------------------
        # Identify columns
        # --------------------------------------------------

        categorical_columns = (
            X.select_dtypes(
                include=["object", "category"]
            )
            .columns
            .tolist()
        )

        numerical_columns = (
            X.select_dtypes(
                include=[np.number]
            )
            .columns
            .tolist()
        )

        logger.info(
            "Numerical Features: %s",
            len(numerical_columns)
        )

        logger.info(
            "Categorical Features: %s",
            len(categorical_columns)
        )

        # --------------------------------------------------
        # Numeric pipeline
        # --------------------------------------------------

        numeric_pipeline = Pipeline(
            steps=[

                (
                    "imputer",

                    SimpleImputer(
                        strategy="median"
                    )

                ),

                (
                    "scaler",

                    StandardScaler()
                )

            ]
        )

        # --------------------------------------------------
        # Categorical pipeline
        # --------------------------------------------------

        categorical_pipeline = Pipeline(
            steps=[

                (
                    "imputer",

                    SimpleImputer(
                        strategy="most_frequent"
                    )

                ),

                (
                    "encoder",

                    OneHotEncoder(
                        handle_unknown="ignore"
                    )

                )

            ]
        )

        # --------------------------------------------------
        # Column transformer
        # --------------------------------------------------

        self.preprocessor = ColumnTransformer(
            transformers=[

                (
                    "numeric",

                    numeric_pipeline,

                    numerical_columns
                ),

                (
                    "categorical",

                    categorical_pipeline,

                    categorical_columns
                )

            ],

            remainder="drop"
        )

        # --------------------------------------------------
        # Train/Test split
        # --------------------------------------------------

        (
            self.X_train,
            self.X_test,
            self.y_train,
            self.y_test
        ) = train_test_split(

            X,

            y,

            test_size=0.20,

            random_state=42

        )

        logger.info(
            "Training Rows: %s",
            len(self.X_train)
        )

        logger.info(
            "Testing Rows: %s",
            len(self.X_test)
        )

        return (
            self.X_train,
            self.X_test,
            self.y_train,
            self.y_test
        )

    # ======================================================
    # RANDOM FOREST
    # ======================================================

    def train_random_forest(self):

        logger.info(
            "Training Random Forest"
        )

        (
            X_train,
            X_test,
            y_train,
            y_test
        ) = self.prepare_dataset()

        model = RandomForestRegressor(

            n_estimators=300,

            max_depth=20,

            random_state=42,

            n_jobs=-1

        )

        pipeline = Pipeline(
            steps=[

                (
                    "preprocessor",

                    self.preprocessor
                ),

                (
                    "model",

                    model
                )

            ]
        )

        pipeline.fit(
            X_train,
            y_train
        )

        prediction = pipeline.predict(
            X_test
        )

        score = r2_score(
            y_test,
            prediction
        )

        self.models["Random Forest"] = {

            "model":
                pipeline,

            "score":
                float(score)

        }

        logger.info(
            "Random Forest R2: %.4f",
            score
        )

        return pipeline

    # ======================================================
    # XGBOOST
    # ======================================================

    def train_xgboost(self):

        if not XGBOOST_AVAILABLE:

            logger.warning(
                "XGBoost is not installed."
            )

            return None

        logger.info(
            "Training XGBoost"
        )

        (
            X_train,
            X_test,
            y_train,
            y_test
        ) = self.prepare_dataset()

        model = XGBRegressor(

            n_estimators=400,

            learning_rate=0.05,

            max_depth=8,

            subsample=0.8,

            colsample_bytree=0.8,

            random_state=42,

            objective="reg:squarederror",

            n_jobs=-1

        )

        pipeline = Pipeline(
            steps=[

                (
                    "preprocessor",

                    self.preprocessor
                ),

                (
                    "model",

                    model
                )

            ]
        )

        pipeline.fit(
            X_train,
            y_train
        )

        prediction = pipeline.predict(
            X_test
        )

        score = r2_score(
            y_test,
            prediction
        )

        self.models["XGBoost"] = {

            "model":
                pipeline,

            "score":
                float(score)

        }

        logger.info(
            "XGBoost R2: %.4f",
            score
        )

        return pipeline

    # ======================================================
    # LIGHTGBM
    # ======================================================

    def train_lightgbm(self):

        if not LIGHTGBM_AVAILABLE:

            logger.warning(
                "LightGBM is not installed."
            )

            return None

        logger.info(
            "Training LightGBM"
        )

        (
            X_train,
            X_test,
            y_train,
            y_test
        ) = self.prepare_dataset()

        model = LGBMRegressor(

            n_estimators=400,

            learning_rate=0.05,

            max_depth=10,

            random_state=42,

            verbosity=-1

        )

        pipeline = Pipeline(
            steps=[

                (
                    "preprocessor",

                    self.preprocessor
                ),

                (
                    "model",

                    model
                )

            ]
        )

        pipeline.fit(
            X_train,
            y_train
        )

        prediction = pipeline.predict(
            X_test
        )

        score = r2_score(
            y_test,
            prediction
        )

        self.models["LightGBM"] = {

            "model":
                pipeline,

            "score":
                float(score)

        }

        logger.info(
            "LightGBM R2: %.4f",
            score
        )

        return pipeline

    # ======================================================
    # MODEL COMPARISON
    # ======================================================

    def compare_models(self):

        if not self.models:

            raise RuntimeError(
                "No models were successfully trained."
            )

        results = []

        for name, info in self.models.items():

            results.append({

                "Model":
                    name,

                "R2 Score":
                    float(
                        info["score"]
                    )

            })

        comparison = pd.DataFrame(
            results
        )

        comparison = comparison.sort_values(
            by="R2 Score",
            ascending=False
        )

        comparison.to_csv(

            self.report_dir
            / "model_comparison.csv",

            index=False

        )

        best_name = (
            comparison.iloc[0]["Model"]
        )

        self.best_model_name = (
            str(best_name)
        )

        self.best_model = (
            self.models[
                self.best_model_name
            ]["model"]
        )

        self.best_score = float(
            self.models[
                self.best_model_name
            ]["score"]
        )

        logger.info(
            "Best Sales Model: %s",
            self.best_model_name
        )

        logger.info(
            "Best R2 Score: %.4f",
            self.best_score
        )

        return self.best_model

    # ======================================================
    # EVALUATE MODEL
    # ======================================================

    def evaluate_model(
        self,
        model=None
    ):

        if model is None:

            model = self.best_model

        if model is None:

            raise RuntimeError(
                "No model available for evaluation."
            )

        (
            X_train,
            X_test,
            y_train,
            y_test
        ) = self.prepare_dataset()

        prediction = model.predict(
            X_test
        )

        mae = mean_absolute_error(
            y_test,
            prediction
        )

        mse = mean_squared_error(
            y_test,
            prediction
        )

        rmse = np.sqrt(
            mse
        )

        r2 = r2_score(
            y_test,
            prediction
        )

        report = {

            "MAE":
                float(mae),

            "MSE":
                float(mse),

            "RMSE":
                float(rmse),

            "R2":
                float(r2),

            "Model":
                self.best_model_name,

            "Generated":
                datetime.now().isoformat()

        }

        with open(

            self.report_dir
            / "metrics.json",

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(
                report,
                file,
                indent=4
            )

        return report

    # ======================================================
    # SAVE BEST MODEL
    # ======================================================

    def save_best_model(self):

        if self.best_model is None:

            raise RuntimeError(
                "No best model available."
            )

        path = (
            self.model_dir
            / "best_sales_model.pkl"
        )

        joblib.dump(
            self.best_model,
            path
        )

        logger.info(
            "Best sales model saved: %s",
            path
        )

        return str(path)

    # ======================================================
    # LOAD BEST MODEL
    # ======================================================

    def load_best_model(self):

        path = (
            self.model_dir
            / "best_sales_model.pkl"
        )

        if not path.exists():

            raise FileNotFoundError(
                f"Sales model not found: {path}"
            )

        self.best_model = joblib.load(
            path
        )

        # --------------------------------------------------
        # Restore model name if possible
        # --------------------------------------------------

        if not self.best_model_name:

            self.best_model_name = (
                "Saved Sales Model"
            )

        logger.info(
            "Best sales model loaded."
        )

        return self.best_model

    # ======================================================
    # BATCH PREDICTION
    # ======================================================

    def predict_dataset(self):

        if self.best_model is None:

            self.load_best_model()

        df = self.load_dataset()

        X = df.drop(

            columns=[

                "Sales",

                "Profit",

                "Profit Margin",

                "Product Sales",

                "Customer Sales",

                "Average Price",

                "Order ID",

                "Customer Name",

                "Product Name"

            ],

            errors="ignore"

        )

        datetime_columns = (
            X.select_dtypes(
                include=[
                    "datetime64[ns]",
                    "datetime64[ns, UTC]"
                ]
            )
            .columns
            .tolist()
        )

        X = X.drop(
            columns=datetime_columns,
            errors="ignore"
        )

        prediction = (
            self.best_model.predict(X)
        )

        prediction = np.maximum(
            prediction,
            0
        )

        df["Predicted Sales"] = (
            prediction
        )

        output = (
            self.output_dir
            / "sales_predictions.csv"
        )

        df.to_csv(
            output,
            index=False
        )

        logger.info(
            "Sales predictions saved: %s",
            output
        )

        return df

    # ======================================================
    # SINGLE PREDICTION
    # ======================================================

    def predict_single(
        self,
        dataframe
    ):

        if self.best_model is None:

            self.load_best_model()

        if not isinstance(
            dataframe,
            pd.DataFrame
        ):

            dataframe = pd.DataFrame(
                dataframe
            )

        prediction = (
            self.best_model.predict(
                dataframe
            )
        )

        value = float(
            prediction[0]
        )

        return {

            "status":
                "success",

            "prediction":
                value,

            "predicted_sales":
                value,

            "model":
                self.best_model_name
                or "Saved Sales Model"

        }

    # ======================================================
    # FEATURE IMPORTANCE
    # ======================================================

    def feature_importance(self):

        if self.best_model is None:

            raise RuntimeError(
                "Train or load the sales model first."
            )

        try:

            model = (
                self.best_model
                .named_steps["model"]
            )

            if not hasattr(
                model,
                "feature_importances_"
            ):

                return {

                    "status":
                        "unavailable",

                    "message":
                        "Feature importance is not available."

                }

            preprocessor = (
                self.best_model
                .named_steps["preprocessor"]
            )

            features = (
                preprocessor
                .get_feature_names_out()
            )

            importance = (
                model.feature_importances_
            )

            df = pd.DataFrame({

                "feature":
                    features,

                "importance":
                    importance

            })

            df = df.sort_values(

                "importance",

                ascending=False

            )

            path = (
                self.report_dir
                / "feature_importance.csv"
            )

            df.head(20).to_csv(

                path,

                index=False

            )

            return {

                "status":
                    "success",

                "features":
                    df.head(20).to_dict(
                        orient="records"
                    )

            }

        except Exception as error:

            logger.exception(
                "Feature importance failed."
            )

            return {

                "status":
                    "error",

                "message":
                    str(error)

            }

    # ======================================================
    # SHAP EXPLAINABILITY
    # ======================================================

    def shap_explainability(self):

        if not SHAP_AVAILABLE:

            return {

                "status":
                    "unavailable",

                "message":
                    "SHAP is not installed."

            }

        if self.best_model is None:

            return {

                "status":
                    "error",

                "message":
                    "No trained model available."

            }

        try:

            df = self.load_dataset()

            X = df.drop(

                columns=[

                    "Sales",

                    "Profit",

                    "Profit Margin",

                    "Product Sales",

                    "Customer Sales",

                    "Average Price",

                    "Order ID",

                    "Customer Name",

                    "Product Name"

                ],

                errors="ignore"

            )

            X = X.select_dtypes(
                exclude=[
                    "datetime64[ns]",
                    "datetime64[ns, UTC]"
                ]
            )

            preprocessor = (
                self.best_model
                .named_steps["preprocessor"]
            )

            model = (
                self.best_model
                .named_steps["model"]
            )

            transformed = (
                preprocessor.transform(
                    X
                )
            )

            if hasattr(
                transformed,
                "toarray"
            ):

                transformed = (
                    transformed.toarray()
                )

            sample = transformed[
                :100
            ]

            explainer = (
                shap.TreeExplainer(
                    model
                )
            )

            values = (
                explainer.shap_values(
                    sample
                )
            )

            feature_names = (
                preprocessor
                .get_feature_names_out()
            )

            shap.summary_plot(

                values,

                features=sample,

                feature_names=feature_names,

                show=False

            )

            path = (
                self.figure_dir
                / "shap_summary.png"
            )

            plt.savefig(

                path,

                bbox_inches="tight"

            )

            plt.close()

            return {

                "status":
                    "success",

                "message":
                    "SHAP explanation generated.",

                "file":
                    str(path)

            }

        except Exception as error:

            logger.exception(
                "SHAP explainability failed."
            )

            return {

                "status":
                    "error",

                "message":
                    str(error)

            }

    # ======================================================
    # GENERATE BUSINESS REPORT
    # ======================================================

    def generate_report(self):

        summary = {

            "status":
                "success",

            "module":
                "Sales Prediction",

            "revenue":
                0.0,

            "total_sales":
                0.0,

            "profit":
                0.0,

            "prediction":
                0.0,

            "predicted_sales":
                0.0,

            "average_sales":
                0.0,

            "model":
                self.best_model_name
                or "N/A",

            "r2_score":
                float(
                    self.best_score
                )
                if self.best_model is not None
                else 0.0,

            "growth":
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

        prediction_file = (
            self.output_dir
            / "sales_predictions.csv"
        )

        try:

            if not prediction_file.exists():

                logger.warning(
                    "Sales prediction file does not exist."
                )

            else:

                df = pd.read_csv(
                    prediction_file
                )

                # --------------------------------------------------
                # Revenue
                # --------------------------------------------------

                total_sales = 0.0

                if "Sales" in df.columns:

                    total_sales = float(
                        pd.to_numeric(
                            df["Sales"],
                            errors="coerce"
                        )
                        .fillna(0)
                        .sum()
                    )

                # --------------------------------------------------
                # Predicted sales
                # --------------------------------------------------

                predicted_sales = 0.0

                if (
                    "Predicted Sales"
                    in df.columns
                ):

                    predicted_sales = float(
                        pd.to_numeric(
                            df["Predicted Sales"],
                            errors="coerce"
                        )
                        .fillna(0)
                        .sum()
                    )

                # --------------------------------------------------
                # Profit
                # --------------------------------------------------

                profit = 0.0

                if "Profit" in df.columns:

                    profit = float(
                        pd.to_numeric(
                            df["Profit"],
                            errors="coerce"
                        )
                        .fillna(0)
                        .sum()
                    )

                else:

                    profit = round(
                        total_sales * 0.25,
                        2
                    )

                # --------------------------------------------------
                # Average sales
                # --------------------------------------------------

                average_sales = (

                    total_sales / len(df)

                    if len(df) > 0

                    else 0.0

                )

                # --------------------------------------------------
                # Sales trend
                # --------------------------------------------------

                sales_trend = []

                if (
                    "Order Date" in df.columns
                    and "Sales" in df.columns
                ):

                    dates = pd.to_datetime(

                        df["Order Date"],

                        errors="coerce"

                    )

                    trend_df = pd.DataFrame({

                        "date":
                            dates,

                        "sales":
                            pd.to_numeric(
                                df["Sales"],
                                errors="coerce"
                            ).fillna(0)

                    })

                    trend_df = (
                        trend_df
                        .dropna(
                            subset=["date"]
                        )
                    )

                    if not trend_df.empty:

                        trend = (

                            trend_df

                            .groupby(
                                trend_df[
                                    "date"
                                ].dt.to_period("M")
                            )["sales"]

                            .sum()

                            .reset_index()

                            .sort_values(
                                "date"
                            )

                        )

                        sales_trend = [

                            {

                                "month":
                                    str(
                                        row["date"]
                                    ),

                                "sales":
                                    float(
                                        row["sales"]
                                    )

                            }

                            for _, row
                            in trend.iterrows()

                        ]

                # --------------------------------------------------
                # Category sales
                # --------------------------------------------------

                category_sales = []

                if (
                    "Category" in df.columns
                    and "Sales" in df.columns
                ):

                    category = (

                        df.groupby(
                            "Category"
                        )["Sales"]

                        .sum()

                        .reset_index()

                        .rename(
                            columns={

                                "Category":
                                    "category",

                                "Sales":
                                    "sales"

                            }
                        )

                    )

                    category_sales = [

                        {

                            "category":
                                str(
                                    row["category"]
                                ),

                            "sales":
                                float(
                                    row["sales"]
                                )

                        }

                        for _, row
                        in category.iterrows()

                    ]

                # --------------------------------------------------
                # Region sales
                # --------------------------------------------------

                region_sales = []

                if (
                    "Region" in df.columns
                    and "Sales" in df.columns
                ):

                    region = (

                        df.groupby(
                            "Region"
                        )["Sales"]

                        .sum()

                        .reset_index()

                        .rename(
                            columns={

                                "Region":
                                    "region",

                                "Sales":
                                    "sales"

                            }
                        )

                    )

                    region_sales = [

                        {

                            "region":
                                str(
                                    row["region"]
                                ),

                            "sales":
                                float(
                                    row["sales"]
                                )

                        }

                        for _, row
                        in region.iterrows()

                    ]

                # --------------------------------------------------
                # Best category
                # --------------------------------------------------

                best_category = (

                    max(

                        category_sales,

                        key=lambda item:
                            item["sales"]

                    )["category"]

                    if category_sales

                    else "N/A"

                )

                # --------------------------------------------------
                # Growth
                # --------------------------------------------------

                growth = 0.0

                if len(sales_trend) >= 2:

                    previous = float(
                        sales_trend[-2]["sales"]
                    )

                    current = float(
                        sales_trend[-1]["sales"]
                    )

                    if previous != 0:

                        growth = (

                            (
                                current
                                - previous
                            )
                            / previous
                        ) * 100

                # --------------------------------------------------
                # Final summary
                # --------------------------------------------------

                summary.update({

                    "revenue":
                        total_sales,

                    "total_sales":
                        total_sales,

                    "profit":
                        profit,

                    "prediction":
                        predicted_sales,

                    "predicted_sales":
                        predicted_sales,

                    "average_sales":
                        round(
                            average_sales,
                            2
                        ),

                    "growth":
                        round(
                            growth,
                            2
                        ),

                    "best_category":
                        best_category,

                    "sales_trend":
                        sales_trend,

                    "category_sales":
                        category_sales,

                    "region_sales":
                        region_sales

                })

        except Exception as error:

            logger.exception(
                "Sales Summary Generation Failed"
            )

            summary["status"] = "error"

            summary["message"] = (
                str(error)
            )

        # --------------------------------------------------
        # Save JSON
        # --------------------------------------------------

        summary_file = (
            self.report_dir
            / "sales_summary.json"
        )

        with open(

            summary_file,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                summary,

                file,

                indent=4

            )

        logger.info(
            "Sales Summary Generated: %s",
            summary_file
        )

        return summary

    # ======================================================
    # VERSIONED MODEL
    # ======================================================

    def save_versioned_model(self):

        if self.best_model is None:

            raise RuntimeError(
                "No best model available."
            )

        version = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        file = (

            self.model_dir
            / f"sales_model_{version}.pkl"

        )

        joblib.dump(

            self.best_model,

            file

        )

        logger.info(
            "Versioned sales model saved: %s",
            file
        )

        return str(file)

    # ======================================================
    # COMPLETE PIPELINE
    # ======================================================

    def run_pipeline(self):

        """
        Run complete enterprise sales pipeline.

        IMPORTANT:
        This method returns a dictionary.

        This fixes the previous problem where
        AIService received None from run_pipeline().
        """

        start_time = datetime.now()

        logger.info(
            "Starting Sales Prediction Pipeline"
        )

        try:

            # --------------------------------------------------
            # Reset model state for fresh training
            # --------------------------------------------------

            self.models = {}

            self.best_model = None

            self.best_model_name = ""

            self.best_score = -999999.0

            self.X_train = None
            self.X_test = None
            self.y_train = None
            self.y_test = None

            # --------------------------------------------------
            # Train models
            # --------------------------------------------------

            self.train_random_forest()

            if XGBOOST_AVAILABLE:

                self.train_xgboost()

            if LIGHTGBM_AVAILABLE:

                self.train_lightgbm()

            # --------------------------------------------------
            # Compare
            # --------------------------------------------------

            self.compare_models()

            # --------------------------------------------------
            # Evaluate
            # --------------------------------------------------

            metrics = self.evaluate_model(
                self.best_model
            )

            # --------------------------------------------------
            # Save
            # --------------------------------------------------

            model_path = (
                self.save_best_model()
            )

            versioned_model = (
                self.save_versioned_model()
            )

            # --------------------------------------------------
            # Predictions
            # --------------------------------------------------

            prediction_df = (
                self.predict_dataset()
            )

            # --------------------------------------------------
            # Feature importance
            # --------------------------------------------------

            importance = (
                self.feature_importance()
            )

            # --------------------------------------------------
            # SHAP
            # --------------------------------------------------

            shap_result = (
                self.shap_explainability()
            )

            # --------------------------------------------------
            # Business report
            # --------------------------------------------------

            summary = (
                self.generate_report()
            )

            # --------------------------------------------------
            # Execution time
            # --------------------------------------------------

            execution_time = round(

                (
                    datetime.now()
                    - start_time
                ).total_seconds(),

                3

            )

            # --------------------------------------------------
            # FINAL RESULT
            # --------------------------------------------------

            result = {

                "status":
                    "success",

                "module":
                    "Sales Prediction",

                "model":
                    self.best_model_name,

                "best_model":
                    self.best_model_name,

                "r2_score":
                    float(
                        self.best_score
                    ),

                "metrics":
                    metrics,

                "summary":
                    summary,

                "revenue":
                    summary.get(
                        "revenue",
                        0
                    ),

                "total_sales":
                    summary.get(
                        "total_sales",
                        0
                    ),

                "profit":
                    summary.get(
                        "profit",
                        0
                    ),

                "prediction":
                    summary.get(
                        "prediction",
                        0
                    ),

                "predicted_sales":
                    summary.get(
                        "predicted_sales",
                        0
                    ),

                "growth":
                    summary.get(
                        "growth",
                        0
                    ),

                "sales_trend":
                    summary.get(
                        "sales_trend",
                        []
                    ),

                "category_sales":
                    summary.get(
                        "category_sales",
                        []
                    ),

                "region_sales":
                    summary.get(
                        "region_sales",
                        []
                    ),

                "best_category":
                    summary.get(
                        "best_category",
                        "N/A"
                    ),

                "feature_importance":
                    importance,

                "shap":
                    shap_result,

                "records":
                    int(
                        len(prediction_df)
                    ),

                "model_path":
                    model_path,

                "versioned_model":
                    versioned_model,

                "execution_time":
                    execution_time

            }

            logger.info(
                "Sales Prediction Pipeline Completed "
                "Successfully in %ss",
                execution_time
            )

            return result

        except Exception as error:

            execution_time = round(

                (
                    datetime.now()
                    - start_time
                ).total_seconds(),

                3

            )

            logger.exception(
                "Sales Prediction Pipeline Failed"
            )

            return {

                "status":
                    "error",

                "module":
                    "Sales Prediction",

                "message":
                    str(error),

                "execution_time":
                    execution_time

            }


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    model = SalesPrediction()

    result = model.run_pipeline()

    print(
        "\n======================================"
    )

    print(
        "ENTERPRISE SALES PREDICTION RESULT"
    )

    print(
        "======================================"
    )

    print(
        json.dumps(
            result,
            indent=4,
            default=str
        )
    )

