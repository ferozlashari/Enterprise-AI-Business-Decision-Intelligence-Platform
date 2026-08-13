"""
=========================================================
Enterprise AI Business Decision Intelligence Platform
Inventory Prediction Engine
Author : Feroz Ali
=========================================================
"""

import warnings
warnings.filterwarnings("ignore")

import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from datetime import datetime
from config.settings import settings

# =====================================================
# Machine Learning
# =====================================================

from sklearn.model_selection import (
    train_test_split,
    GridSearchCV,
    cross_val_score,
    KFold
)

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

from sklearn.preprocessing import (
    StandardScaler,
    OneHotEncoder
)

from sklearn.impute import SimpleImputer

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor
)

# =====================================================
# XGBoost
# =====================================================

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except Exception:
    XGBOOST_AVAILABLE = False


# =====================================================
# LightGBM
# =====================================================

try:
    from lightgbm import LGBMRegressor
    LIGHTGBM_AVAILABLE = True
except Exception:
    LIGHTGBM_AVAILABLE = False


# =====================================================
# SHAP
# =====================================================

try:
    import shap
    SHAP_AVAILABLE = True
except Exception:
    SHAP_AVAILABLE = False


# =====================================================
# Local Imports
# =====================================================

from config.logger import get_logger

from data.data_loader import DataLoader
from data.preprocessing import DataPreprocessor
from data.feature_engineering import FeatureEngineering

logger = get_logger("InventoryPrediction")


# =====================================================
# Inventory Prediction Class
# =====================================================

class InventoryPrediction:

    """
    Enterprise Inventory Prediction Engine

    Features
    --------
    ✔ Inventory Demand Prediction
    ✔ Safety Stock
    ✔ Reorder Point
    ✔ EOQ
    ✔ ABC Analysis
    ✔ Random Forest
    ✔ XGBoost
    ✔ LightGBM
    ✔ Grid Search
    ✔ Cross Validation
    ✔ SHAP Explainability
    ✔ Feature Importance
    ✔ Enterprise Reports
    ✔ Versioned Model Saving
    """

    def __init__(self):

        logger.info("Initializing Inventory Prediction Engine")

        self.loader = DataLoader()

        self.processor = DataPreprocessor()

        self.engineer = FeatureEngineering()

        self.models = {}

        self.best_model = None

        self.best_model_name = ""

        self.best_score = -999999

        self.preprocessor = None

        self.model_dir = Path(settings.MODEL_DIR)

        self.output_dir = Path(settings.OUTPUT_DIR)

        self.report_dir = Path(settings.REPORT_DIR)

        self.figure_dir = Path(settings.FIGURE_DIR)

        self.model_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.report_dir.mkdir(exist_ok=True)
        self.figure_dir.mkdir(exist_ok=True)

        # =====================================================
# Load Dataset
# =====================================================

    def load_dataset(self):

        logger.info("Loading Dataset")

        df = self.loader.load_superstore()

        df = self.processor.clean_dataframe(df)

        df = self.processor.convert_dates(
            df,
            ["Order Date", "Ship Date"]
        )

        df = self.engineer.full_pipeline(df)

        logger.info(f"Dataset Shape : {df.shape}")

        return df


# =====================================================
# Inventory Feature Engineering
# =====================================================

    def create_inventory_features(self, df):

        logger.info("Creating Inventory Features")

        if "Quantity" in df.columns:
            df["Inventory Demand"] = (

                df["Quantity"]

                .rolling(

                    window=7,

                    min_periods=1

                )

                .mean()

            )



        if "Sales" in df.columns and "Quantity" in df.columns:
            df["Unit Price"] = (
                df["Sales"] /
                df["Quantity"].replace(0, 1)
            )

        if "Profit" in df.columns and "Sales" in df.columns:
            df["Profit Margin"] = (
                df["Profit"] /
                df["Sales"].replace(0, 1)
            )

        if "Order Date" in df.columns:

            df["Year"] = df["Order Date"].dt.year
            df["Month"] = df["Order Date"].dt.month
            df["Quarter"] = df["Order Date"].dt.quarter
            df["Day"] = df["Order Date"].dt.day
            df["Weekday"] = df["Order Date"].dt.weekday

        logger.info("Inventory Features Created")

        return df


# =====================================================
# Prepare Dataset
# =====================================================

    def prepare_dataset(self):

        logger.info("Preparing Dataset")

        df = self.load_dataset()

        df = self.create_inventory_features(df)

        target = "Inventory Demand"

        remove_columns = [
            "Inventory Demand",
            "Quantity", 
            "Order ID",
            "Customer Name",
            "Product Name"
        ]

        remove_columns = [
            c for c in remove_columns
            if c in df.columns
        ]

        X = df.drop(columns=remove_columns)

        datetime_columns = X.select_dtypes(
            include=["datetime64[ns]"]
        ).columns.tolist()

        X = X.drop(
            columns=datetime_columns,
            errors="ignore"
        )

        y = df[target]

        categorical = X.select_dtypes(
            include=["object"]
        ).columns.tolist()

        numerical = X.select_dtypes(
            include=[np.number]
        ).columns.tolist()

        numeric_pipeline = Pipeline(

            steps=[

                (
                    "imputer",
                    SimpleImputer(strategy="median")
                ),

                (
                    "scaler",
                    StandardScaler()
                )

            ]

        )

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

        self.preprocessor = ColumnTransformer(

            transformers=[

                (
                    "num",
                    numeric_pipeline,
                    numerical
                ),

                (
                    "cat",
                    categorical_pipeline,
                    categorical
                )

            ]

        )

        X_train, X_test, y_train, y_test = train_test_split(

            X,
            y,

            test_size=0.20,

            shuffle=False

        )

        logger.info("Dataset Ready")

        return (

            X_train,

            X_test,

            y_train,

            y_test

        )

    # =====================================================
# Train Random Forest
# =====================================================

    def train_random_forest(self):

        logger.info("Training Random Forest")

        X_train, X_test, y_train, y_test = self.prepare_dataset()

        model = RandomForestRegressor(
            n_estimators=300,
            max_depth=20,
            random_state=42,
            n_jobs=-1
        )

        pipeline = Pipeline([
            ("preprocessor", self.preprocessor),
            ("model", model)
        ])

        pipeline.fit(X_train, y_train)

        prediction = pipeline.predict(X_test)

        score = r2_score(y_test, prediction)

        self.models["Random Forest"] = {
            "model": pipeline,
            "score": score
        }

        print(f"Random Forest R² : {score:.4f}")

        return pipeline


# =====================================================
# Train XGBoost
# =====================================================

    def train_xgboost(self):

        if not XGBOOST_AVAILABLE:
            print("XGBoost Not Installed")
            return

        logger.info("Training XGBoost")

        X_train, X_test, y_train, y_test = self.prepare_dataset()

        model = XGBRegressor(
            random_state=42,
            n_estimators=400,
            learning_rate=0.05,
            max_depth=8,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror"
        )

        pipeline = Pipeline([
            ("preprocessor", self.preprocessor),
            ("model", model)
        ])

        pipeline.fit(X_train, y_train)

        prediction = pipeline.predict(X_test)

        score = r2_score(y_test, prediction)

        self.models["XGBoost"] = {
            "model": pipeline,
            "score": score
        }

        print(f"XGBoost R² : {score:.4f}")

        return pipeline


# =====================================================
# Train LightGBM
# =====================================================

    def train_lightgbm(self):

        if not LIGHTGBM_AVAILABLE:
            print("LightGBM Not Installed")
            return

        logger.info("Training LightGBM")

        X_train, X_test, y_train, y_test = self.prepare_dataset()

        model = LGBMRegressor(
            random_state=42,
            n_estimators=400,
            learning_rate=0.05,
            max_depth=10
        )

        pipeline = Pipeline([
            ("preprocessor", self.preprocessor),
            ("model", model)
        ])

        pipeline.fit(X_train, y_train)

        prediction = pipeline.predict(X_test)

        score = r2_score(y_test, prediction)

        self.models["LightGBM"] = {
            "model": pipeline,
            "score": score
        }

        print(f"LightGBM R² : {score:.4f}")

        return pipeline

    # =====================================================
# Grid Search
# =====================================================

    def grid_search_random_forest(self):

        logger.info("Running Grid Search")

        X_train, X_test, y_train, y_test = self.prepare_dataset()

        pipeline = Pipeline([
            ("preprocessor", self.preprocessor),
            ("model", RandomForestRegressor(random_state=42))
        ])

        params = {

            "model__n_estimators": [100, 200],

            "model__max_depth": [10, 20],

            "model__min_samples_split": [2, 5]

        }

        search = GridSearchCV(

            pipeline,

            params,

            cv=3,

            scoring="r2",

            n_jobs=-1

        )

        search.fit(X_train, y_train)

        print("\nBest Parameters")

        print(search.best_params_)

        print("Best Score")

        print(search.best_score_)


        return search.best_estimator_

        


# =====================================================
# Cross Validation
# =====================================================

    def cross_validation(self):

        logger.info("Running Cross Validation")

        X_train, X_test, y_train, y_test = self.prepare_dataset()

        pipeline = Pipeline([
            ("preprocessor", self.preprocessor),
            ("model", RandomForestRegressor(random_state=42))
        ])

        cv = KFold(

            n_splits=5,

            shuffle=True,

            random_state=42

        )

        scores = cross_val_score(

            pipeline,

            X_train,

            y_train,

            cv=cv,

            scoring="r2"

        )

        print("\nCross Validation Scores")

        print(scores)

        print("\nAverage Score")

        print(scores.mean())


# =====================================================
# Evaluate Model
# =====================================================

    def evaluate_model(self, model):

        X_train, X_test, y_train, y_test = self.prepare_dataset()

        prediction = model.predict(X_test)

        mae = mean_absolute_error(y_test, prediction)

        mse = mean_squared_error(y_test, prediction)

        rmse = np.sqrt(mse)

        r2 = r2_score(y_test, prediction)

        report = {

            "MAE": float(mae),

            "RMSE": float(rmse),

            "R2": float(r2),

            "Generated": str(datetime.now())

        }

        with open(

            self.report_dir / "inventory_metrics.json",

            "w"

        ) as f:

            json.dump(report, f, indent=4)

        print("\n=====================")

        print("Inventory Evaluation")

        print("=====================")

        print(f"MAE  : {mae:.2f}")

        print(f"RMSE : {rmse:.2f}")

        print(f"R²   : {r2:.4f}")

        return report


# =====================================================
# Compare Models
# =====================================================

    def compare_models(self):

        if len(self.models) == 0:

            raise Exception("No trained models.")

        comparison = []

        for name, info in self.models.items():

            comparison.append({

                "Model": name,

                "R2 Score": info["score"]

            })

        comparison_df = pd.DataFrame(comparison)

        comparison_df = comparison_df.sort_values(

            "R2 Score",

            ascending=False

        )

        comparison_df.to_csv(

            self.report_dir /

            "inventory_model_comparison.csv",

            index=False

        )

        print("\n========================")

        print("MODEL COMPARISON")

        print("========================")

        print(comparison_df)

        self.best_model_name = comparison_df.iloc[0]["Model"]

        self.best_model = self.models[

            self.best_model_name

        ]["model"]

        self.best_score = self.models[

            self.best_model_name

        ]["score"]

        print("\nBest Model :", self.best_model_name)

        print("Best Score :", round(self.best_score, 4))



        # =====================================================
# Save Best Model
# =====================================================

    def save_best_model(self):

        if self.best_model is None:
            raise Exception("No Best Model Selected")

        filename = self.model_dir / "best_inventory_model.pkl"

        joblib.dump(
            self.best_model,
            filename
        )

        logger.info("Best Inventory Model Saved")

        print("Best Inventory Model Saved")


# =====================================================
# Load Best Model
# =====================================================
    def load_best_model(self):

        filename = self.model_dir / "best_inventory_model.pkl"


        if not filename.exists():

            raise FileNotFoundError(
                "Inventory model not trained yet"
            )


        self.best_model = joblib.load(
            filename
        )


        logger.info(
            "Inventory Model Loaded"
        )


        return self.best_model


    



# =====================================================
# Predict Inventory
# =====================================================

    def predict_inventory(self):

        if self.best_model is None:

           self.load_best_model()

        logger.info("Predicting Inventory")

        df = self.load_dataset()

        df = self.create_inventory_features(df)

        remove_columns = [
            "Inventory Demand",
            "Quantity", 
            "Order ID",
            "Customer Name",
            "Product Name"
        ]

        remove_columns = [
            c for c in remove_columns
            if c in df.columns
        ]

        X = df.drop(columns=remove_columns)

        datetime_columns = X.select_dtypes(
            include=["datetime64[ns]"]
        ).columns.tolist()

        X = X.drop(
            columns=datetime_columns,
            errors="ignore"
        )

        prediction = self.best_model.predict(X)

        df["Predicted Inventory"] = prediction

        output = self.output_dir / "inventory_predictions.csv"

        df.to_csv(
            output,
            index=False
        )

        logger.info("Inventory Prediction Saved")

        print("Inventory Prediction Saved")

        return df


# =====================================================
# Safety Stock
# =====================================================

    def calculate_safety_stock(self, df):

        logger.info("Calculating Safety Stock")

        std = df["Inventory Demand"].std()

        safety_stock = 1.65 * std

        print(f"Safety Stock : {round(safety_stock,2)}")

        return safety_stock


# =====================================================
# Reorder Point
# =====================================================

    def calculate_reorder_point(
        self,
        avg_daily_demand,
        lead_time,
        safety_stock
    ):

        reorder = (
            avg_daily_demand * lead_time
        ) + safety_stock

        print(f"Reorder Point : {round(reorder,2)}")

        return reorder


# =====================================================
# EOQ
# =====================================================

    def economic_order_quantity(
        self,
        annual_demand,
        ordering_cost,
        holding_cost
    ):

        eoq = np.sqrt(
            (
                2 * annual_demand * ordering_cost
            ) / holding_cost
        )

        print(f"Economic Order Quantity : {round(eoq,2)}")

        return eoq


# =====================================================
# ABC Analysis
# =====================================================

    def abc_analysis(self):

        logger.info("Running ABC Analysis")

        df = self.load_dataset()

        abc = (
            df.groupby("Product Name")["Sales"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        abc["Cumulative"] = (
            abc["Sales"].cumsum() /
            abc["Sales"].sum()
        )

        abc["Class"] = np.where(
            abc["Cumulative"] <= 0.80,
            "A",
            np.where(
                abc["Cumulative"] <= 0.95,
                "B",
                "C"
            )
        )

        abc.to_csv(
            self.report_dir / "abc_analysis.csv",
            index=False
        )

        logger.info("ABC Analysis Saved")

        print("ABC Analysis Completed")

        return abc


    # =====================================================
# Feature Importance
# =====================================================

    def plot_feature_importance(self):

        logger.info("Generating Feature Importance")

        try:

            estimator = self.best_model.named_steps["model"]

            if not hasattr(estimator, "feature_importances_"):
                print("Feature Importance Not Supported")
                return

            feature_names = self.best_model.named_steps[
                "preprocessor"
            ].get_feature_names_out()

            importance = estimator.feature_importances_

            importance_df = pd.DataFrame({

                "Feature": feature_names,

                "Importance": importance

            })

            importance_df = importance_df.sort_values(

                "Importance",

                ascending=False

            ).head(20)

            plt.figure(figsize=(12,8))

            plt.barh(

                importance_df["Feature"],

                importance_df["Importance"]

            )

            plt.gca().invert_yaxis()

            plt.tight_layout()

            plt.savefig(

                self.figure_dir /
                "inventory_feature_importance.png",

                dpi=300

            )

            plt.close()

            importance_df.to_csv(

                self.report_dir /
                "inventory_feature_importance.csv",

                index=False

            )

            print("Inventory Feature Importance Saved")

        except Exception as e:

            logger.error(str(e))


# =====================================================
# SHAP Explainability
# =====================================================

    def shap_explainability(self):

        if not SHAP_AVAILABLE:

            print("SHAP Not Installed")

            return

        try:

            df = self.predict_inventory()

            remove_columns = [

                "Inventory Demand",

                "Predicted Inventory",

                "Quantity", 

                "Order ID",

                "Customer Name",

                "Product Name"

            ]

            remove_columns = [

                c for c in remove_columns

                if c in df.columns

            ]

            X = df.drop(columns=remove_columns)

            datetime_columns = X.select_dtypes(

                include=["datetime64[ns]"]

            ).columns.tolist()

            X = X.drop(

                columns=datetime_columns,

                errors="ignore"

            )

            transformed = self.best_model.named_steps[
                "preprocessor"
            ].transform(X)

            if hasattr(transformed, "toarray"):

                transformed = transformed.toarray()

            transformed = np.asarray(
                transformed
            ).astype(np.float64)

            estimator = self.best_model.named_steps[
                "model"
            ]

            explainer = shap.TreeExplainer(
                estimator
            )

            shap_values = explainer.shap_values(
                transformed[:100]
            )

            plt.figure(figsize=(12,8))

            shap.summary_plot(

                shap_values,

                transformed[:100],

                show=False

            )

            plt.savefig(

                self.figure_dir /
                "inventory_shap_summary.png",

                dpi=300,

                bbox_inches="tight"

            )

            plt.close()

            print("Inventory SHAP Saved")

        except Exception as e:

            logger.warning(f"SHAP skipped: {e}")


# =====================================================
# Enterprise Report
# =====================================================

    def generate_report(self):

        report = {

            "Project": "Enterprise AI Inventory Prediction",

            "Best Model": self.best_model_name,

            "Best Score": float(self.best_score),

            "Generated": str(datetime.now()),

            "Models": list(self.models.keys())

        }

        with open(

            self.report_dir /
            "inventory_report.json",

            "w"

        ) as f:

            json.dump(

                report,

                f,

                indent=4

            )

        print("Inventory Report Saved")

    # =====================================================
# Inventory Summary
# =====================================================

    def generate_summary(self):

        logger.info(
            "Generating Inventory Summary"
        )


        file = (
            self.output_dir /
            "inventory_predictions.csv"
        )


        if not file.exists():

            logger.warning(
                "inventory_predictions.csv missing"
            )

            return



        df = pd.read_csv(
            file
        )


        summary = {


        "Inventory":

        float(
            df["Predicted Inventory"].sum()
        ),


        "Demand":

        float(
            df["Inventory Demand"].sum()
        ),


        "Products":

        int(
            len(df)
        ),


        "inventory_data":

        [

            {

            "product":
            "Inventory",

            "quantity":
            float(
                df["Predicted Inventory"].sum()
            ),

            "demand":
            float(
                df["Inventory Demand"].sum()
            )

            }

        ]


        }



        with open(

            self.report_dir /
            "inventory_summary.json",

            "w"

        ) as f:


            json.dump(

                summary,

                f,

                indent=4

            )



        logger.info(
            "Inventory Summary Generated"
        )


        print(
            "Inventory Summary Saved"
        )


        return summary    


# =====================================================
# Versioned Model
# =====================================================

    def save_versioned_model(self):

        version = datetime.now().strftime(

            "%Y%m%d_%H%M%S"

        )

        filename = self.model_dir / f"inventory_model_{version}.pkl"

        joblib.dump(

            self.best_model,

            filename

        )

        print("Version Saved :", filename.name)


# =====================================================
# Complete Pipeline
# =====================================================

    def run_pipeline(self):

        print("\n========== Inventory Prediction ==========\n")

        self.train_random_forest()

        if XGBOOST_AVAILABLE:

            self.train_xgboost()

        if LIGHTGBM_AVAILABLE:

            self.train_lightgbm()

        self.compare_models()

        self.evaluate_model(self.best_model)

        self.save_best_model()

        self.save_versioned_model()

        inventory = self.predict_inventory()


        safety_stock = self.calculate_safety_stock(
            inventory
        )


        self.calculate_reorder_point(

            avg_daily_demand=
                inventory["Inventory Demand"].mean(),

            lead_time=7,

            safety_stock=safety_stock

        )

        self.economic_order_quantity(

            annual_demand=inventory["Inventory Demand"].sum(),

            ordering_cost=100,

            holding_cost=5

        )

        self.abc_analysis()

        self.plot_feature_importance()

        self.shap_explainability()

        self.generate_summary()

        self.generate_report()

        print("\nInventory Prediction Completed Successfully")


# =====================================================
# Main
# =====================================================

if __name__ == "__main__":

    predictor = InventoryPrediction()

    predictor.run_pipeline()