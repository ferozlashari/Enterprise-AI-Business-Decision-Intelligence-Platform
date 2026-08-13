
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Demand Forecasting Engine

Model:
    - Facebook Prophet
    - Time Series Forecasting

Author : Feroz Ali
=========================================================
"""

import warnings

warnings.filterwarnings("ignore")

import json
import joblib

from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from prophet import Prophet

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)

from config.settings import settings
from config.logger import get_logger

from data.data_loader import DataLoader
from data.preprocessing import DataPreprocessor


logger = get_logger("DemandForecast")


class DemandForecasting:

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        self.loader = DataLoader()

        self.processor = DataPreprocessor()

        self.model = None

        self.model_dir = Path(
            settings.MODEL_DIR
        )

        self.figure_dir = Path(
            settings.FIGURE_DIR
        )

        self.report_dir = Path(
            settings.REPORT_DIR
        )

        self.output_dir = Path(
            settings.OUTPUT_DIR
        )

        self.model_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.figure_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.report_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    # =====================================================
    # LOAD DATA
    # =====================================================

    def load_data(self):

        logger.info(
            "Loading Dataset"
        )

        df = self.loader.load_superstore()

        df = self.processor.clean_dataframe(
            df
        )

        df = self.processor.convert_dates(
            df,
            [
                "Order Date"
            ]
        )

        required_columns = [
            "Order Date",
            "Sales",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:

            raise ValueError(
                "Missing required forecast columns: "
                + ", ".join(
                    missing_columns
                )
            )

        # -------------------------------------------------
        # CLEAN DATE
        # -------------------------------------------------

        df["Order Date"] = pd.to_datetime(
            df["Order Date"],
            errors="coerce"
        )

        # -------------------------------------------------
        # CLEAN SALES
        # -------------------------------------------------

        df["Sales"] = pd.to_numeric(
            df["Sales"],
            errors="coerce"
        )

        df = df.dropna(
            subset=[
                "Order Date",
                "Sales",
            ]
        )

        if df.empty:

            raise ValueError(
                "No valid sales records available "
                "for demand forecasting."
            )

        df = df.sort_values(
            "Order Date"
        ).reset_index(
            drop=True
        )

        logger.info(
            "Forecast source rows: %s",
            len(df)
        )

        logger.info(
            "Historical source start: %s",
            df["Order Date"].min()
        )

        logger.info(
            "Historical source end: %s",
            df["Order Date"].max()
        )

        return df

    # =====================================================
    # PREPARE PROPHET DATASET
    # =====================================================

    def prepare_data(self):

        logger.info(
            "Preparing Forecast Dataset"
        )

        df = self.load_data()

        # -------------------------------------------------
        # MONTHLY SALES DEMAND
        # -------------------------------------------------

        demand = (
            df.groupby(
                pd.Grouper(
                    key="Order Date",
                    freq="MS"
                )
            )["Sales"]
            .sum()
            .reset_index()
        )

        demand.columns = [
            "ds",
            "y"
        ]

        demand["ds"] = pd.to_datetime(
            demand["ds"],
            errors="coerce"
        )

        demand["y"] = pd.to_numeric(
            demand["y"],
            errors="coerce"
        )

        demand = demand.dropna(
            subset=[
                "ds",
                "y"
            ]
        )

        demand = demand.sort_values(
            "ds"
        ).reset_index(
            drop=True
        )

        if demand.empty:

            raise ValueError(
                "No monthly demand data available "
                "for Prophet."
            )

        logger.info(
            "Forecast Data Shape: %s",
            demand.shape
        )

        logger.info(
            "Forecast Start Date: %s",
            demand["ds"].min()
        )

        logger.info(
            "Forecast End Date: %s",
            demand["ds"].max()
        )

        return demand

    # =====================================================
    # TRAIN MODEL
    # =====================================================

    def train_model(self):

        logger.info(
            "Training Prophet Model"
        )

        data = self.prepare_data()

        self.model = Prophet(

            yearly_seasonality=True,

            weekly_seasonality=False,

            daily_seasonality=False,

            seasonality_mode="multiplicative",

        )

        self.model.fit(
            data
        )

        logger.info(
            "Prophet Training Completed"
        )

        logger.info(
            "Prophet Last Historical Date: %s",
            data["ds"].max()
        )

        return self.model

    # =====================================================
    # FUTURE FORECAST
    # =====================================================

    def forecast(
        self,
        periods=12
    ):

        if self.model is None:

            self.train_model()

        # -------------------------------------------------
        # GET LAST HISTORICAL DATE
        # -------------------------------------------------

        historical_data = (
            self.prepare_data()
        )

        last_historical_date = (
            pd.Timestamp(
                historical_data["ds"].max()
            )
        )

        logger.info(
            "Last Historical Month: %s",
            last_historical_date.strftime(
                "%Y-%m-%d"
            )
        )

        # -------------------------------------------------
        # CREATE COMPLETE PROPHET DATAFRAME
        #
        # This contains:
        #
        # historical dates
        # +
        # future dates
        # -------------------------------------------------

        future = self.model.make_future_dataframe(

            periods=int(periods),

            freq="MS",

            include_history=True

        )

        future["ds"] = pd.to_datetime(
            future["ds"],
            errors="coerce"
        )

        future = future.dropna(
            subset=[
                "ds"
            ]
        )

        future = future.sort_values(
            "ds"
        ).reset_index(
            drop=True
        )

        # -------------------------------------------------
        # SAFETY CHECK
        #
        # Make sure future dataframe actually extends
        # beyond the historical data.
        # -------------------------------------------------

        expected_last_future_date = (
            last_historical_date
            + pd.DateOffset(
                months=int(periods)
            )
        )

        actual_last_future_date = (
            future["ds"].max()
        )

        logger.info(
            "Expected Last Future Date: %s",
            expected_last_future_date.strftime(
                "%Y-%m-%d"
            )
        )

        logger.info(
            "Actual Prophet Last Date: %s",
            actual_last_future_date.strftime(
                "%Y-%m-%d"
            )
        )

        if (
            actual_last_future_date
            <=
            last_historical_date
        ):

            raise RuntimeError(
                "Prophet did not generate future dates. "
                "Last historical date: "
                f"{last_historical_date.strftime('%Y-%m-%d')}, "
                "last generated date: "
                f"{actual_last_future_date.strftime('%Y-%m-%d')}"
            )

        # -------------------------------------------------
        # PREDICT
        # -------------------------------------------------

        prediction = self.model.predict(
            future
        )

        prediction["ds"] = pd.to_datetime(
            prediction["ds"],
            errors="coerce"
        )

        prediction = prediction.dropna(
            subset=[
                "ds"
            ]
        )

        prediction = prediction.sort_values(
            "ds"
        ).reset_index(
            drop=True
        )

        # -------------------------------------------------
        # NON-NEGATIVE FORECAST
        # -------------------------------------------------

        prediction["yhat"] = (
            prediction["yhat"]
            .clip(
                lower=0
            )
        )

        if "yhat_lower" in prediction.columns:

            prediction["yhat_lower"] = (
                prediction["yhat_lower"]
                .clip(
                    lower=0
                )
            )

        if "yhat_upper" in prediction.columns:

            prediction["yhat_upper"] = (
                prediction["yhat_upper"]
                .clip(
                    lower=0
                )
            )

        # -------------------------------------------------
        # ADD FORECAST TYPE
        # -------------------------------------------------

        prediction["forecast_type"] = np.where(

            prediction["ds"]
            <=
            last_historical_date,

            "historical",

            "future"

        )

        # -------------------------------------------------
        # EXTRACT ONLY FUTURE ROWS FOR VALIDATION
        # -------------------------------------------------

        future_prediction = (
            prediction[
                prediction["ds"]
                >
                last_historical_date
            ]
            .copy()
        )

        # -------------------------------------------------
        # HARD SAFETY CHECK
        # -------------------------------------------------

        if future_prediction.empty:

            raise RuntimeError(
                "No future forecast points were generated."
            )

        if len(future_prediction) != int(periods):

            logger.warning(
                "Expected %s future points but generated %s.",
                periods,
                len(future_prediction)
            )

        logger.info(
            "Future Forecast Start: %s",
            future_prediction["ds"].min()
        )

        logger.info(
            "Future Forecast End: %s",
            future_prediction["ds"].max()
        )

        logger.info(
            "Future Forecast Points: %s",
            len(future_prediction)
        )

        # -------------------------------------------------
        # SAVE COMPLETE FORECAST
        # -------------------------------------------------

        file = (
            self.output_dir
            / "sales_forecast.csv"
        )

        prediction.to_csv(
            file,
            index=False
        )

        logger.info(
            "Complete Forecast Saved: %s",
            file
        )

        # -------------------------------------------------
        # SAVE FUTURE-ONLY FORECAST
        # -------------------------------------------------

        future_file = (
            self.output_dir
            / "sales_future_forecast.csv"
        )

        future_prediction.to_csv(
            future_file,
            index=False
        )

        logger.info(
            "Future Forecast Saved: %s",
            future_file
        )

        return prediction

    # =====================================================
    # EVALUATION
    # =====================================================

    def evaluate(self):

        data = self.prepare_data()

        if self.model is None:

            self.train_model()

        prediction = self.model.predict(
            data
        )

        prediction["yhat"] = (
            prediction["yhat"]
            .clip(
                lower=0
            )
        )

        mae = mean_absolute_error(
            data["y"],
            prediction["yhat"]
        )

        rmse = np.sqrt(
            mean_squared_error(
                data["y"],
                prediction["yhat"]
            )
        )

        metrics = {

            "MAE":
                float(
                    mae
                ),

            "RMSE":
                float(
                    rmse
                ),

        }

        logger.info(
            "Forecast Metrics: %s",
            metrics
        )

        return metrics

    # =====================================================
    # FORECAST PLOT
    # =====================================================

    def plot_forecast(
        self,
        forecast
    ):

        if self.model is None:
            return

        self.model.plot(
            forecast
        )

        plt.title(
            "Sales Demand Forecast"
        )

        plt.tight_layout()

        file = (
            self.figure_dir
            / "forecast.png"
        )

        plt.savefig(
            file,
            dpi=300
        )

        plt.close()

        logger.info(
            "Forecast plot saved: %s",
            file
        )

    # =====================================================
    # COMPONENTS PLOT
    # =====================================================

    def plot_components(
        self,
        forecast
    ):

        if self.model is None:
            return

        self.model.plot_components(
            forecast
        )

        plt.tight_layout()

        file = (
            self.figure_dir
            / "forecast_components.png"
        )

        plt.savefig(
            file,
            dpi=300
        )

        plt.close()

        logger.info(
            "Forecast components plot saved: %s",
            file
        )

    # =====================================================
    # SAVE MODEL
    # =====================================================

    def save_model(self):

        if self.model is None:

            raise ValueError(
                "Cannot save Prophet model "
                "because model is not trained."
            )

        path = (
            self.model_dir
            / "prophet_model.pkl"
        )

        joblib.dump(
            self.model,
            path
        )

        logger.info(
            "Forecast Model Saved: %s",
            path
        )

    # =====================================================
    # GENERATE REPORT
    # =====================================================

    def generate_report(
        self,
        metrics
    ):

        report = {

            "model":
                "Facebook Prophet",

            "metrics":
                metrics,

            "forecast_period":
                12,

        }

        file = (
            self.report_dir
            / "forecast_report.json"
        )

        with open(
            file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                report,
                f,
                indent=4
            )

        logger.info(
            "Forecast report saved: %s",
            file
        )

        return report

    # =====================================================
    # GENERATE DASHBOARD FORECAST SUMMARY
    # =====================================================

    def generate_dashboard_report(
        self,
        forecast
    ):

        try:

            if forecast is None:
                return {}

            if forecast.empty:
                return {}

            # -------------------------------------------------
            # REQUIRED COLUMNS
            # -------------------------------------------------

            required_columns = [
                "ds",
                "yhat",
            ]

            missing = [
                column
                for column in required_columns
                if column not in forecast.columns
            ]

            if missing:

                raise ValueError(
                    "Forecast is missing required columns: "
                    + ", ".join(
                        missing
                    )
                )

            # -------------------------------------------------
            # COPY
            # -------------------------------------------------

            forecast = forecast.copy()

            forecast["ds"] = pd.to_datetime(
                forecast["ds"],
                errors="coerce"
            )

            forecast = forecast.dropna(
                subset=[
                    "ds"
                ]
            )

            forecast = forecast.sort_values(
                "ds"
            ).reset_index(
                drop=True
            )

            # -------------------------------------------------
            # HISTORICAL DATA
            # -------------------------------------------------

            historical_data = (
                self.prepare_data()
            )

            historical_data["ds"] = pd.to_datetime(
                historical_data["ds"],
                errors="coerce"
            )

            historical_data["y"] = pd.to_numeric(
                historical_data["y"],
                errors="coerce"
            )

            historical_data = historical_data.dropna(
                subset=[
                    "ds",
                    "y"
                ]
            )

            historical_data = historical_data.sort_values(
                "ds"
            ).reset_index(
                drop=True
            )

            # -------------------------------------------------
            # LAST HISTORICAL DATE
            # -------------------------------------------------

            last_historical_date = pd.Timestamp(
                historical_data["ds"].max()
            )

            logger.info(
                "Dashboard Historical End Date: %s",
                last_historical_date.strftime(
                    "%Y-%m-%d"
                )
            )

            # -------------------------------------------------
            # ACTUAL MAP
            # -------------------------------------------------

            actual_map = {

                pd.Timestamp(
                    row["ds"]
                ).strftime(
                    "%Y-%m-%d"
                ):

                float(
                    max(
                        0,
                        round(
                            float(
                                row["y"]
                            ),
                            2
                        )
                    )
                )

                for _, row
                in historical_data.iterrows()

            }

            # -------------------------------------------------
            # BUILD DASHBOARD DATA
            # -------------------------------------------------

            forecast_data = []

            for _, row in forecast.iterrows():

                date_value = pd.Timestamp(
                    row["ds"]
                )

                date_key = (
                    date_value.strftime(
                        "%Y-%m-%d"
                    )
                )

                # ---------------------------------------------
                # FORECAST
                # ---------------------------------------------

                forecast_value = row.get(
                    "yhat"
                )

                if pd.isna(
                    forecast_value
                ):

                    forecast_value = 0.0

                forecast_value = max(
                    0,
                    round(
                        float(
                            forecast_value
                        ),
                        2
                    )
                )

                # ---------------------------------------------
                # ACTUAL
                # ---------------------------------------------

                actual_value = (
                    actual_map.get(
                        date_key
                    )
                )

                # ---------------------------------------------
                # LOWER
                # ---------------------------------------------

                lower_value = None

                if (
                    "yhat_lower"
                    in forecast.columns
                ):

                    raw_lower = row.get(
                        "yhat_lower"
                    )

                    if not pd.isna(
                        raw_lower
                    ):

                        lower_value = max(
                            0,
                            round(
                                float(
                                    raw_lower
                                ),
                                2
                            )
                        )

                # ---------------------------------------------
                # UPPER
                # ---------------------------------------------

                upper_value = None

                if (
                    "yhat_upper"
                    in forecast.columns
                ):

                    raw_upper = row.get(
                        "yhat_upper"
                    )

                    if not pd.isna(
                        raw_upper
                    ):

                        upper_value = max(
                            0,
                            round(
                                float(
                                    raw_upper
                                ),
                                2
                            )
                        )

                # ---------------------------------------------
                # FORECAST TYPE
                # ---------------------------------------------

                forecast_type = (

                    "future"

                    if date_value
                    >
                    last_historical_date

                    else

                    "historical"

                )

                # ---------------------------------------------
                # FRONTEND DATA
                # ---------------------------------------------

                forecast_data.append({

                    "date":
                        date_key,

                    "forecast":
                        forecast_value,

                    "actual":
                        actual_value,

                    "lower":
                        lower_value,

                    "upper":
                        upper_value,

                    "forecast_type":
                        forecast_type,

                })

            # -------------------------------------------------
            # FUTURE POINTS
            #
            # IMPORTANT:
            # Do NOT identify future points merely by
            # actual == None.
            #
            # Use the historical cutoff date.
            # -------------------------------------------------

            future_points = [

                item

                for item in forecast_data

                if item.get(
                    "forecast_type"
                ) == "future"

            ]

            historical_points = [

                item

                for item in forecast_data

                if item.get(
                    "forecast_type"
                ) == "historical"

            ]

            # -------------------------------------------------
            # FUTURE FORECAST VALUES ONLY
            # -------------------------------------------------

            future_forecast_values = [

                item["forecast"]

                for item in future_points

                if item.get(
                    "forecast"
                ) is not None

            ]

            # -------------------------------------------------
            # ALL FORECAST VALUES
            # -------------------------------------------------

            forecast_values = [

                item["forecast"]

                for item in forecast_data

                if item.get(
                    "forecast"
                ) is not None

            ]

            actual_values = [

                item["actual"]

                for item in forecast_data

                if item.get(
                    "actual"
                ) is not None

            ]

            # -------------------------------------------------
            # AVERAGE FUTURE FORECAST
            #
            # This is more meaningful for the dashboard.
            # -------------------------------------------------

            if future_forecast_values:

                average_forecast = round(

                    sum(
                        future_forecast_values
                    )
                    /
                    len(
                        future_forecast_values
                    ),

                    2

                )

            elif forecast_values:

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

            else:

                average_forecast = 0.0

            # -------------------------------------------------
            # LATEST FUTURE FORECAST
            # -------------------------------------------------

            latest_forecast = 0.0

            if future_points:

                latest_forecast = (
                    future_points[-1]
                    .get(
                        "forecast",
                        0.0
                    )
                )

            elif forecast_data:

                latest_forecast = (
                    forecast_data[-1]
                    .get(
                        "forecast",
                        0.0
                    )
                )

            # -------------------------------------------------
            # MINIMUM FUTURE FORECAST
            # -------------------------------------------------

            minimum_forecast = (

                min(
                    future_forecast_values
                )

                if future_forecast_values

                else 0.0

            )

            # -------------------------------------------------
            # MAXIMUM FUTURE FORECAST
            # -------------------------------------------------

            maximum_forecast = (

                max(
                    future_forecast_values
                )

                if future_forecast_values

                else 0.0

            )

            # -------------------------------------------------
            # FUTURE GROWTH
            # -------------------------------------------------

            growth = 0.0

            if len(
                future_forecast_values
            ) >= 2:

                first_value = (
                    future_forecast_values[0]
                )

                last_value = (
                    future_forecast_values[-1]
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
                        *
                        100,

                        2

                    )

            # -------------------------------------------------
            # REPORT
            # -------------------------------------------------

            report = {

                "status":
                    "success",

                "available":
                    True,

                "model":
                    "Facebook Prophet",

                "historical_end_date":
                    last_historical_date.strftime(
                        "%Y-%m-%d"
                    ),

                "forecast_start_date":
                    (
                        future_points[0]["date"]
                        if future_points
                        else None
                    ),

                "forecast_end_date":
                    (
                        future_points[-1]["date"]
                        if future_points
                        else None
                    ),

                "forecast":
                    forecast_data,

                "records":
                    len(
                        forecast_data
                    ),

                "forecast_points":
                    len(
                        future_points
                    ),

                "historical_points":
                    len(
                        historical_points
                    ),

                "future_points":
                    len(
                        future_points
                    ),

                "average_forecast":
                    average_forecast,

                "latest_forecast":
                    latest_forecast,

                "minimum_forecast":
                    minimum_forecast,

                "maximum_forecast":
                    maximum_forecast,

                "growth":
                    growth,

            }

            # -------------------------------------------------
            # SAVE DASHBOARD REPORT
            # -------------------------------------------------

            file = (
                self.report_dir
                / "forecast_summary.json"
            )

            with open(
                file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    report,
                    f,
                    indent=4
                )

            logger.info(
                "Dashboard Forecast Summary Generated"
            )

            logger.info(
                "Historical points: %s",
                len(
                    historical_points
                )
            )

            logger.info(
                "Future points: %s",
                len(
                    future_points
                )
            )

            logger.info(
                "Future Forecast Start: %s",
                report[
                    "forecast_start_date"
                ]
            )

            logger.info(
                "Future Forecast End: %s",
                report[
                    "forecast_end_date"
                ]
            )

            logger.info(
                "Total dashboard points: %s",
                len(
                    forecast_data
                )
            )

            return report

        except Exception as error:

            logger.exception(
                "Forecast Dashboard Report Failed"
            )

            return {

                "status":
                    "error",

                "available":
                    False,

                "model":
                    "Facebook Prophet",

                "forecast":
                    [],

                "records":
                    0,

                "forecast_points":
                    0,

                "historical_points":
                    0,

                "future_points":
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
                    0.0,

                "message":
                    str(
                        error
                    )

            }

    # =====================================================
    # COMPLETE AI PIPELINE
    # =====================================================

    def run_pipeline(self):

        logger.info(
            "Demand Forecast Pipeline Started"
        )

        # -------------------------------------------------
        # TRAIN
        # -------------------------------------------------

        self.train_model()

        # -------------------------------------------------
        # FORECAST
        # -------------------------------------------------

        forecast = self.forecast(
            periods=12
        )

        # -------------------------------------------------
        # EVALUATE
        # -------------------------------------------------

        metrics = self.evaluate()

        # -------------------------------------------------
        # PLOTS
        # -------------------------------------------------

        self.plot_forecast(
            forecast
        )

        self.plot_components(
            forecast
        )

        # -------------------------------------------------
        # SAVE MODEL
        # -------------------------------------------------

        self.save_model()

        # -------------------------------------------------
        # REPORT
        # -------------------------------------------------

        report = self.generate_report(
            metrics
        )

        # -------------------------------------------------
        # DASHBOARD REPORT
        # -------------------------------------------------

        dashboard_report = (
            self.generate_dashboard_report(
                forecast
            )
        )

        logger.info(
            "Demand Forecast Completed"
        )

        return {

            "model":
                "Facebook Prophet",

            "status":
                "completed",

            "metrics":
                metrics,

            "forecast_file":
                str(
                    self.output_dir
                    / "sales_forecast.csv"
                ),

            "future_forecast_file":
                str(
                    self.output_dir
                    / "sales_future_forecast.csv"
                ),

            "report":
                report,

            "dashboard_forecast":
                dashboard_report

        }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    model = DemandForecasting()

    result = model.run_pipeline()

    print(
        json.dumps(
            result,
            indent=4
        )
    )

