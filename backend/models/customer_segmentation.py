
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Customer Segmentation Engine

Responsibilities:
- Load customer data
- Clean and preprocess customer data
- Scale customer features
- Determine clustering behavior
- Train K-Means segmentation model
- Calculate silhouette score
- Generate customer segments
- Save trained model
- Save scaler
- Save clustered dataset
- Generate segmentation reports
- Generate dashboard summary
- Generate visualization
- Provide run_pipeline() for AIService

Author : Feroz Ali
=========================================================
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import joblib
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


# =========================================================
# LOGGER
# =========================================================

logger = logging.getLogger("CustomerSegmentation")


# =========================================================
# PROJECT DIRECTORIES
# =========================================================

# Expected project structure:
#
# Enterprise_AI/
# ├── backend/
# │   └── models/
# │       └── customer_segmentation.py
# ├── datasets/
# ├── saved_models/
# ├── outputs/
# └── reports/
#
# parents[2] -> Enterprise_AI

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_DIR = BASE_DIR / "datasets"
MODEL_DIR = BASE_DIR / "saved_models"
OUTPUT_DIR = BASE_DIR / "outputs"
REPORT_DIR = BASE_DIR / "reports"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# CUSTOMER SEGMENTATION
# =========================================================

class CustomerSegmentation:

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        data_path: Optional[str] = None,
        n_clusters: int = 5,
    ) -> None:

        self.data_path = Path(
            data_path
            if data_path
            else DATASET_DIR / "customers.csv"
        )

        self.n_clusters = max(
            2,
            int(n_clusters),
        )

        self.model: Optional[KMeans] = None

        self.scaler = StandardScaler()

        # Default features for Mall Customers dataset
        self.features = [
            "Age",
            "Annual Income (k$)",
            "Spending Score (1-100)",
        ]

        self.silhouette_score: float = 0.0

        self.summary: Optional[dict[str, Any]] = None

        self.elbow_result: dict[str, Any] = {}

        self.clustered_data: Optional[pd.DataFrame] = None

    # =====================================================
    # LOAD DATA
    # =====================================================

    def load_data(
        self,
        data_path: Optional[str] = None,
    ) -> pd.DataFrame:

        if data_path:
            self.data_path = Path(data_path)

        # Convert relative dataset paths to project-relative paths
        if not self.data_path.is_absolute():
            self.data_path = BASE_DIR / self.data_path

        if not self.data_path.exists():
            raise FileNotFoundError(
                "Customer dataset not found: "
                f"{self.data_path}"
            )

        logger.info(
            "Loading customer dataset: %s",
            self.data_path,
        )

        try:
            df = pd.read_csv(
                self.data_path,
                encoding="latin1",
            )
        except UnicodeDecodeError:
            logger.warning(
                "latin1 decoding failed. Retrying with UTF-8."
            )

            df = pd.read_csv(
                self.data_path,
                encoding="utf-8",
            )

        if df.empty:
            raise ValueError(
                "Customer dataset is empty."
            )

        logger.info(
            "Customer dataset loaded successfully. "
            "Rows=%s Columns=%s",
            len(df),
            len(df.columns),
        )

        print("=" * 60)
        print("CUSTOMER DATASET LOADED")
        print("=" * 60)
        print(f"Dataset : {self.data_path}")
        print(f"Rows    : {len(df)}")
        print(f"Columns : {len(df.columns)}")
        print()
        print(df.head())
        print("=" * 60)

        return df

    # =====================================================
    # PREPROCESS
    # =====================================================

    def preprocess(
        self,
        df: pd.DataFrame,
    ) -> tuple[pd.DataFrame, Any]:

        if df is None:
            raise ValueError(
                "Customer dataframe cannot be None."
            )

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "Customer data must be a pandas DataFrame."
            )

        df = df.copy()

        logger.info(
            "Starting customer preprocessing."
        )

        # -------------------------------------------------
        # Validate required columns
        # -------------------------------------------------

        missing_features = [
            feature
            for feature in self.features
            if feature not in df.columns
        ]

        if missing_features:
            raise ValueError(
                "Customer dataset is missing required "
                f"columns: {missing_features}. "
                f"Available columns: {list(df.columns)}"
            )

        # -------------------------------------------------
        # Remove duplicate rows
        # -------------------------------------------------

        before_duplicates = len(df)

        df = df.drop_duplicates()

        removed_duplicates = (
            before_duplicates - len(df)
        )

        if removed_duplicates:
            logger.info(
                "Removed %s duplicate rows.",
                removed_duplicates,
            )

        # -------------------------------------------------
        # Convert required features to numeric
        # -------------------------------------------------

        for feature in self.features:

            df[feature] = pd.to_numeric(
                df[feature],
                errors="coerce",
            )

        # -------------------------------------------------
        # Handle missing values
        # -------------------------------------------------

        for feature in self.features:

            if df[feature].isna().any():

                median_value = df[feature].median()

                if pd.isna(median_value):
                    raise ValueError(
                        f"Unable to calculate median for "
                        f"feature: {feature}"
                    )

                df[feature] = df[feature].fillna(
                    median_value
                )

        # -------------------------------------------------
        # Remove infinite values
        # -------------------------------------------------

        df[self.features] = df[
            self.features
        ].replace(
            [float("inf"), float("-inf")],
            pd.NA,
        )

        # -------------------------------------------------
        # Remove remaining invalid feature rows
        # -------------------------------------------------

        df = df.dropna(
            subset=self.features
        )

        if df.empty:
            raise ValueError(
                "No valid customer records remain "
                "after preprocessing."
            )

        if len(df) < 2:
            raise ValueError(
                "At least 2 valid customers are required "
                "for segmentation."
            )

        # -------------------------------------------------
        # Feature matrix
        # -------------------------------------------------

        X = df[
            self.features
        ].astype(float)

        # -------------------------------------------------
        # Scaling
        # -------------------------------------------------

        X_scaled = self.scaler.fit_transform(X)

        logger.info(
            "Customer preprocessing completed. "
            "Valid customers=%s",
            len(df),
        )

        print(
            "\nCustomer preprocessing completed."
        )

        print(
            f"Valid Customers: {len(df)}"
        )

        print(
            f"Features: {self.features}"
        )

        return df, X_scaled

    # =====================================================
    # ELBOW METHOD
    # =====================================================

    def elbow_method(
        self,
        X: Any,
    ) -> dict[str, Any]:

        if X is None:
            raise ValueError(
                "Feature matrix cannot be None."
            )

        sample_count = len(X)

        if sample_count < 3:

            logger.warning(
                "Not enough samples for elbow analysis."
            )

            self.elbow_result = {
                "k_values": [],
                "inertia": [],
                "visualization_path": None,
            }

            return self.elbow_result

        # Never allow k >= number of samples
        max_k = min(
            10,
            sample_count - 1,
        )

        if max_k < 2:

            self.elbow_result = {
                "k_values": [],
                "inertia": [],
                "visualization_path": None,
            }

            return self.elbow_result

        k_values = list(
            range(
                2,
                max_k + 1,
            )
        )

        inertia: list[float] = []

        for k in k_values:

            model = KMeans(
                n_clusters=k,
                random_state=42,
                n_init=10,
            )

            model.fit(X)

            inertia.append(
                float(
                    model.inertia_
                )
            )

        # -------------------------------------------------
        # Plot elbow curve
        # -------------------------------------------------

        plt.figure(
            figsize=(8, 5)
        )

        plt.plot(
            k_values,
            inertia,
            marker="o",
        )

        plt.xlabel(
            "Number of Clusters"
        )

        plt.ylabel(
            "Inertia"
        )

        plt.title(
            "Customer Segmentation Elbow Method"
        )

        plt.grid(
            True,
            alpha=0.3,
        )

        plt.tight_layout()

        elbow_path = (
            OUTPUT_DIR /
            "elbow_method.png"
        )

        plt.savefig(
            elbow_path,
            bbox_inches="tight",
            dpi=150,
        )

        plt.close()

        self.elbow_result = {
            "k_values": k_values,
            "inertia": inertia,
            "visualization_path": str(
                elbow_path
            ),
        }

        logger.info(
            "Elbow graph saved: %s",
            elbow_path,
        )

        return self.elbow_result

    # =====================================================
    # TRAIN MODEL
    # =====================================================

    def train(
        self,
        X: Any,
    ) -> Any:

        if X is None:
            raise ValueError(
                "Feature matrix cannot be None."
            )

        sample_count = len(X)

        if sample_count < self.n_clusters:
            raise ValueError(
                f"Customer records ({sample_count}) "
                f"must be greater than or equal to "
                f"number of clusters ({self.n_clusters})."
            )

        logger.info(
            "Training K-Means with %s clusters.",
            self.n_clusters,
        )

        self.model = KMeans(
            n_clusters=self.n_clusters,
            random_state=42,
            n_init=10,
        )

        labels = self.model.fit_predict(X)

        # -------------------------------------------------
        # Silhouette score
        # -------------------------------------------------

        unique_labels = len(
            set(labels)
        )

        if (
            unique_labels > 1
            and unique_labels < sample_count
        ):

            self.silhouette_score = float(
                silhouette_score(
                    X,
                    labels,
                )
            )

        else:

            self.silhouette_score = 0.0

        print(
            "\nSilhouette Score:",
            round(
                self.silhouette_score,
                4,
            ),
        )

        # -------------------------------------------------
        # Training report
        # -------------------------------------------------

        report = {
            "status": "success",
            "model": "K-Means Customer Segmentation",
            "algorithm": "KMeans",
            "clusters": self.n_clusters,
            "features": self.features,
            "customers": int(sample_count),
            "silhouette_score": round(
                self.silhouette_score,
                6,
            ),
            "random_state": 42,
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        report_path = (
            REPORT_DIR /
            "customer_segmentation_report.json"
        )

        self._write_json(
            report_path,
            report,
        )

        logger.info(
            "Customer segmentation report saved: %s",
            report_path,
        )

        return labels

    # =====================================================
    # SAVE MODEL
    # =====================================================

    def save_model(self) -> dict[str, str]:

        if self.model is None:
            raise RuntimeError(
                "Customer segmentation model "
                "has not been trained."
            )

        model_path = (
            MODEL_DIR /
            "customer_segmentation.pkl"
        )

        scaler_path = (
            MODEL_DIR /
            "customer_scaler.pkl"
        )

        metadata_path = (
            MODEL_DIR /
            "customer_segmentation_metadata.json"
        )

        joblib.dump(
            self.model,
            model_path,
        )

        joblib.dump(
            self.scaler,
            scaler_path,
        )

        metadata = {
            "model": "KMeans",
            "algorithm": "KMeans",
            "clusters": self.n_clusters,
            "features": self.features,
            "silhouette_score": float(
                self.silhouette_score
            ),
            "model_path": str(
                model_path
            ),
            "scaler_path": str(
                scaler_path
            ),
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        self._write_json(
            metadata_path,
            metadata,
        )

        print(
            "\nCustomer Segmentation Model Saved"
        )

        logger.info(
            "Customer segmentation model saved."
        )

        return {
            "model": str(
                model_path
            ),
            "scaler": str(
                scaler_path
            ),
            "metadata": str(
                metadata_path
            ),
        }

    # =====================================================
    # SAVE CLUSTERED DATASET
    # =====================================================

    def save_dataset(
        self,
        df: pd.DataFrame,
    ) -> str:

        if df is None:
            raise ValueError(
                "Customer dataframe cannot be None."
            )

        if "Cluster" not in df.columns:
            raise ValueError(
                "Cluster column is missing."
            )

        output_path = (
            OUTPUT_DIR /
            "customer_segments.csv"
        )

        df.to_csv(
            output_path,
            index=False,
        )

        logger.info(
            "Clustered customer dataset saved: %s",
            output_path,
        )

        print(
            "Clustered Dataset Saved:",
            output_path,
        )

        return str(
            output_path
        )

    # =====================================================
    # CUSTOMER SUMMARY
    # =====================================================

    def generate_summary(
        self,
        df: pd.DataFrame,
    ) -> dict[str, Any]:

        if df is None:
            raise ValueError(
                "Customer dataframe cannot be None."
            )

        if "Cluster" not in df.columns:
            raise ValueError(
                "Cluster column is missing."
            )

        distribution = (
            df["Cluster"]
            .value_counts()
            .sort_index()
            .to_dict()
        )

        distribution = {
            str(key): int(value)
            for key, value
            in distribution.items()
        }

        segments = self.get_segments(df)

        summary = {
            "status": "success",
            "customers": int(
                len(df)
            ),
            "clusters": int(
                self.n_clusters
            ),
            "segments": segments,
            "customer_segments": segments,
            "segment_count": int(
                df["Cluster"].nunique()
            ),
            "customer_segments_count": int(
                df["Cluster"].nunique()
            ),
            "segment_distribution": distribution,
            "silhouette_score": round(
                float(
                    self.silhouette_score
                ),
                6,
            ),
            "model": "KMeans",
            "model_status": "healthy",
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        summary_path = (
            REPORT_DIR /
            "customer_summary.json"
        )

        self._write_json(
            summary_path,
            summary,
        )

        self.summary = summary

        logger.info(
            "Customer summary saved: %s",
            summary_path,
        )

        return summary

    # =====================================================
    # VISUALIZATION
    # =====================================================

    def visualize(
        self,
        df: pd.DataFrame,
    ) -> str:

        if df is None:
            raise ValueError(
                "Customer dataframe cannot be None."
            )

        if "Cluster" not in df.columns:
            raise ValueError(
                "Cluster column is missing."
            )

        required_columns = [
            "Annual Income (k$)",
            "Spending Score (1-100)",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                "Required visualization columns "
                f"missing: {missing_columns}"
            )

        plt.figure(
            figsize=(9, 6)
        )

        plt.scatter(
            df["Annual Income (k$)"],
            df["Spending Score (1-100)"],
            c=df["Cluster"],
            cmap="viridis",
            alpha=0.75,
            edgecolors="black",
            linewidths=0.3,
        )

        plt.xlabel(
            "Annual Income (k$)"
        )

        plt.ylabel(
            "Spending Score (1-100)"
        )

        plt.title(
            "Customer Segmentation"
        )

        plt.grid(
            True,
            alpha=0.2,
        )

        plt.tight_layout()

        output_path = (
            OUTPUT_DIR /
            "customer_clusters.png"
        )

        plt.savefig(
            output_path,
            bbox_inches="tight",
            dpi=150,
        )

        plt.close()

        logger.info(
            "Customer cluster visualization saved: %s",
            output_path,
        )

        print(
            "Customer Cluster Graph Saved:",
            output_path,
        )

        return str(
            output_path
        )

    # =====================================================
    # GET SEGMENT DATA
    # =====================================================

    def get_segments(
        self,
        df: pd.DataFrame,
    ) -> list[dict[str, Any]]:

        if df is None:
            return []

        if "Cluster" not in df.columns:
            return []

        required_columns = [
            "Age",
            "Annual Income (k$)",
            "Spending Score (1-100)",
        ]

        if any(
            column not in df.columns
            for column in required_columns
        ):
            return []

        segments: list[dict[str, Any]] = []

        grouped = df.groupby(
            "Cluster",
            sort=True,
        )

        for cluster_id, group in grouped:

            try:
                cluster_number = int(
                    cluster_id
                )
            except (
                TypeError,
                ValueError,
            ):
                cluster_number = str(
                    cluster_id
                )

            segment = {
                "cluster": cluster_number,

                "segment": (
                    f"Cluster {cluster_number}"
                ),

                "customers": int(
                    len(group)
                ),

                "average_age": round(
                    float(
                        group["Age"].mean()
                    ),
                    2,
                ),

                "average_income": round(
                    float(
                        group[
                            "Annual Income (k$)"
                        ].mean()
                    ),
                    2,
                ),

                "average_spending_score": round(
                    float(
                        group[
                            "Spending Score (1-100)"
                        ].mean()
                    ),
                    2,
                ),
            }

            segments.append(
                segment
            )

        return segments

    # =====================================================
    # DASHBOARD SUMMARY
    # =====================================================

    def get_dashboard_summary(
        self,
        df: Optional[pd.DataFrame] = None,
    ) -> dict[str, Any]:

        if df is None:
            df = self.clustered_data

        if df is None:
            return {
                "status": "success",
                "customers": 0,
                "customer_segments": [],
                "customer_segments_count": 0,
                "customer_silhouette": 0.0,
                "model_status": "unknown",
                "model": "KMeans",
                "clusters": int(
                    self.n_clusters
                ),
            }

        segments = self.get_segments(df)

        return {
            "status": "success",

            "customers": int(
                len(df)
            ),

            "customer_segments": segments,

            "customer_segments_count": int(
                len(segments)
            ),

            "customer_silhouette": round(
                float(
                    self.silhouette_score
                ),
                6,
            ),

            "model_status": (
                "healthy"
                if self.model is not None
                else "unknown"
            ),

            "model": "KMeans",

            "clusters": int(
                self.n_clusters
            ),
        }

    # =====================================================
    # RUN PIPELINE
    # =====================================================

    def run_pipeline(
        self,
        data_path: Optional[str] = None,
        save: bool = True,
    ) -> dict[str, Any]:

        """
        Complete customer segmentation pipeline.

        Required by AIService.

        Returns a stable dictionary compatible with:
        - AIService
        - ReportService
        - DashboardService
        - Decision Engine
        - FastAPI
        """

        try:

            print(
                "\n" +
                "=" * 60
            )

            print(
                "CUSTOMER SEGMENTATION PIPELINE"
            )

            print(
                "=" * 60
            )

            # -------------------------------------------------
            # LOAD
            # -------------------------------------------------

            df = self.load_data(
                data_path=data_path
            )

            # -------------------------------------------------
            # PREPROCESS
            # -------------------------------------------------

            df, X = self.preprocess(df)

            # -------------------------------------------------
            # VALIDATE CLUSTER COUNT
            # -------------------------------------------------

            if self.n_clusters > len(df):

                self.n_clusters = len(df)

                logger.warning(
                    "Requested cluster count was larger "
                    "than customer count. "
                    "Adjusted clusters to %s.",
                    self.n_clusters,
                )

            if self.n_clusters < 2:
                raise ValueError(
                    "At least 2 clusters are required."
                )

            # -------------------------------------------------
            # ELBOW
            # -------------------------------------------------

            elbow = self.elbow_method(X)

            # -------------------------------------------------
            # TRAIN
            # -------------------------------------------------

            labels = self.train(X)

            # -------------------------------------------------
            # ATTACH CLUSTERS
            # -------------------------------------------------

            df = df.copy()

            df["Cluster"] = labels

            self.clustered_data = df

            # -------------------------------------------------
            # SEGMENTS
            # -------------------------------------------------

            segments = self.get_segments(df)

            # -------------------------------------------------
            # SAVE
            # -------------------------------------------------

            model_paths: dict[str, str] = {}

            dataset_path: Optional[str] = None

            visualization_path: Optional[str] = None

            summary: Optional[dict[str, Any]] = None

            if save:

                model_paths = self.save_model()

                dataset_path = self.save_dataset(
                    df
                )

                summary = self.generate_summary(
                    df
                )

                visualization_path = self.visualize(
                    df
                )

            else:

                distribution = (
                    df["Cluster"]
                    .value_counts()
                    .sort_index()
                    .to_dict()
                )

                summary = {
                    "status": "success",

                    "customers": int(
                        len(df)
                    ),

                    "clusters": int(
                        self.n_clusters
                    ),

                    "segments": segments,

                    "customer_segments": segments,

                    "segment_count": int(
                        df["Cluster"].nunique()
                    ),

                    "customer_segments_count": int(
                        df["Cluster"].nunique()
                    ),

                    "segment_distribution": {
                        str(key): int(value)
                        for key, value
                        in distribution.items()
                    },

                    "silhouette_score": round(
                        float(
                            self.silhouette_score
                        ),
                        6,
                    ),

                    "model": "KMeans",

                    "model_status": "healthy",
                }

                self.summary = summary

            # -------------------------------------------------
            # DASHBOARD DATA
            # -------------------------------------------------

            dashboard = self.get_dashboard_summary(
                df
            )

            # -------------------------------------------------
            # FINAL RESULT
            # -------------------------------------------------

            result = {

                "status": "success",

                "model": "KMeans",

                "algorithm": "KMeans",

                "clusters": int(
                    self.n_clusters
                ),

                "customers": int(
                    len(df)
                ),

                "silhouette_score": round(
                    float(
                        self.silhouette_score
                    ),
                    6,
                ),

                "segments": segments,

                "customer_segments": segments,

                "customer_segments_count": int(
                    len(segments)
                ),

                "summary": summary,

                "dashboard": dashboard,

                "elbow": elbow,

                "model_paths": model_paths,

                "dataset_path": dataset_path,

                "visualization_path": (
                    visualization_path
                ),

                "report_path": str(
                    REPORT_DIR /
                    "customer_segmentation_report.json"
                ),

                "summary_path": str(
                    REPORT_DIR /
                    "customer_summary.json"
                ),

                "generated_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            }

            print(
                "\n" +
                "=" * 60
            )

            print(
                "CUSTOMER SEGMENTATION COMPLETED"
            )

            print(
                "=" * 60
            )

            logger.info(
                "Customer segmentation completed successfully."
            )

            return result

        except Exception as error:

            logger.exception(
                "Customer segmentation pipeline failed."
            )

            print(
                "\nCustomer Segmentation Pipeline Failed:"
            )

            print(error)

            return {

                "status": "error",

                "model": "KMeans",

                "algorithm": "KMeans",

                "clusters": int(
                    self.n_clusters
                ),

                "customers": 0,

                "silhouette_score": 0.0,

                "segments": [],

                "customer_segments": [],

                "customer_segments_count": 0,

                "summary": {},

                "dashboard": {
                    "status": "error",
                    "customers": 0,
                    "customer_segments": [],
                    "customer_segments_count": 0,
                    "customer_silhouette": 0.0,
                    "model_status": "error",
                    "model": "KMeans",
                    "clusters": int(
                        self.n_clusters
                    ),
                },

                "elbow": {},

                "model_paths": {},

                "dataset_path": None,

                "visualization_path": None,

                "report_path": str(
                    REPORT_DIR /
                    "customer_segmentation_report.json"
                ),

                "summary_path": str(
                    REPORT_DIR /
                    "customer_summary.json"
                ),

                "message": str(error),

                "generated_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            }

    # =====================================================
    # JSON HELPER
    # =====================================================

    @staticmethod
    def _write_json(
        path: Path,
        data: dict[str, Any],
    ) -> None:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                default=str,
            )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )

    segmentation = CustomerSegmentation()

    result = segmentation.run_pipeline()

    print(
        "\n" +
        "=" * 60
    )

    print(
        "FINAL CUSTOMER SEGMENTATION RESULT"
    )

    print(
        "=" * 60
    )

    print(
        json.dumps(
            result,
            indent=4,
            default=str,
        )
    )

