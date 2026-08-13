"""
=========================================================
Enterprise AI Business Decision Intelligence Platform
AI Service Layer

Author : Feroz Ali

Responsibilities
----------------
1. Load enterprise AI models lazily.
2. Provide a singleton AI service.
3. Run Sales Prediction.
4. Run Inventory Prediction.
5. Run Customer Segmentation.
6. Run Demand Forecasting.
7. Cache successful model results.
8. Normalize model responses.
9. Run all enterprise AI models.
10. Build unified Decision Engine input.
11. Execute Enterprise Decision Intelligence.
12. Provide service health information.
=========================================================
"""

import logging
import threading
import time

from typing import Any, Dict, Optional

from backend.models.sales_prediction import (
    SalesPrediction,
)

from backend.models.inventory_prediction import (
    InventoryPrediction,
)

from backend.models.customer_segmentation import (
    CustomerSegmentation,
)

from backend.models.demand_forecasting import (
    DemandForecasting,
)

from backend.services.decision_service import (
    DecisionService,
)


logger = logging.getLogger(
    "AIService"
)


class AIService:

    # =====================================================
    # SINGLETON STATE
    # =====================================================

    _instance = None

    _lock = threading.RLock()

    _sales_model = None

    _inventory_model = None

    _customer_model = None

    _forecast_model = None

    _cache: Dict[str, Dict[str, Any]] = {}

    _initialized = False

    # =====================================================
    # SINGLETON
    # =====================================================

    def __new__(
        cls,
    ):

        if cls._instance is None:

            with cls._lock:

                if cls._instance is None:

                    cls._instance = super(
                        AIService,
                        cls,
                    ).__new__(
                        cls
                    )

        return cls._instance

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
    ):

        if getattr(
            self,
            "_initialized",
            False,
        ):

            return

        logger.info(
            "Enterprise AI Service Ready"
        )

        self._initialized = True

    # =====================================================
    # SALES MODEL
    # =====================================================

    def get_sales_model(
        self,
    ):

        if AIService._sales_model is None:

            with AIService._lock:

                if AIService._sales_model is None:

                    logger.info(
                        "Loading Sales Prediction Model"
                    )

                    AIService._sales_model = (
                        SalesPrediction()
                    )

        return AIService._sales_model

    # =====================================================
    # INVENTORY MODEL
    # =====================================================

    def get_inventory_model(
        self,
    ):

        if AIService._inventory_model is None:

            with AIService._lock:

                if AIService._inventory_model is None:

                    logger.info(
                        "Loading Inventory Prediction Model"
                    )

                    AIService._inventory_model = (
                        InventoryPrediction()
                    )

        return AIService._inventory_model

    # =====================================================
    # CUSTOMER MODEL
    # =====================================================

    def get_customer_model(
        self,
    ):

        if AIService._customer_model is None:

            with AIService._lock:

                if AIService._customer_model is None:

                    logger.info(
                        "Loading Customer Segmentation Model"
                    )

                    AIService._customer_model = (
                        CustomerSegmentation()
                    )

        return AIService._customer_model

    # =====================================================
    # FORECAST MODEL
    # =====================================================

    def get_forecast_model(
        self,
    ):

        if AIService._forecast_model is None:

            with AIService._lock:

                if AIService._forecast_model is None:

                    logger.info(
                        "Loading Demand Forecasting Model"
                    )

                    AIService._forecast_model = (
                        DemandForecasting()
                    )

        return AIService._forecast_model

    # =====================================================
    # CACHE KEY
    # =====================================================

    def _build_cache_key(
        self,
        model,
        question="",
    ):

        model_key = str(
            model or ""
        ).strip().lower()

        question_key = str(
            question or ""
        ).strip().lower()

        return (
            f"{model_key}:"
            f"{question_key}"
        )

    # =====================================================
    # NORMALIZE RESULT
    # =====================================================

    def _normalize_result(
        self,
        result,
        model,
        execution_time,
    ):

        # -------------------------------------------------
        # None result
        # -------------------------------------------------

        if result is None:

            logger.warning(
                "Model '%s' returned None.",
                model,
            )

            return {

                "status":
                    "error",

                "model":
                    model,

                "message":
                    (
                        f"{model} completed "
                        "without returning any "
                        "business analysis data."
                    ),

                "result":
                    {},

                "execution_time":
                    execution_time,
            }

        # -------------------------------------------------
        # Dictionary result
        # -------------------------------------------------

        if isinstance(
            result,
            dict,
        ):

            normalized = dict(
                result
            )

        else:

            normalized = {

                "status":
                    "success",

                "result":
                    result,
            }

        # -------------------------------------------------
        # Ensure status
        # -------------------------------------------------

        normalized.setdefault(
            "status",
            "success",
        )

        # -------------------------------------------------
        # Ensure model
        # -------------------------------------------------

        normalized.setdefault(
            "model",
            model,
        )

        # -------------------------------------------------
        # Ensure execution time
        # -------------------------------------------------

        normalized.setdefault(
            "execution_time",
            execution_time,
        )

        return normalized

    # =====================================================
    # RUN MODEL PIPELINE
    # =====================================================

    def _run_model_pipeline(
        self,
        model_name,
        model_instance,
        question="",
    ):

        """
        Safely execute an enterprise AI model.

        Supports:

            run_pipeline()

        and:

            run_pipeline(question=...)
        """

        try:

            # -------------------------------------------------
            # Prefer question-aware pipeline
            # -------------------------------------------------

            try:

                return model_instance.run_pipeline(
                    question=question
                )

            except TypeError as error:

                error_message = str(
                    error
                ).lower()

                # -------------------------------------------------
                # Backward compatibility
                # -------------------------------------------------

                if (
                    "unexpected keyword argument"
                    in error_message
                    or
                    "positional argument"
                    in error_message
                    or
                    "keyword argument"
                    in error_message
                ):

                    logger.info(
                        "%s.run_pipeline() "
                        "does not support question. "
                        "Using legacy pipeline.",
                        model_name,
                    )

                    return model_instance.run_pipeline()

                raise

        except Exception:

            logger.exception(
                "%s pipeline execution failed",
                model_name,
            )

            raise

    # =====================================================
    # BUSINESS ANALYSIS ROUTER
    # =====================================================

    def run_business_analysis(
        self,
        model: str,
        question: str = "",
    ):

        if not model:

            return {

                "status":
                    "error",

                "message":
                    "Model name is required.",

                "result":
                    {},
            }

        model = str(
            model
        ).strip().lower()

        question = str(
            question or ""
        ).strip()

        # -------------------------------------------------
        # Cache
        # -------------------------------------------------

        cache_key = self._build_cache_key(
            model,
            question,
        )

        with AIService._lock:

            cached = AIService._cache.get(
                cache_key
            )

        if cached is not None:

            logger.info(
                "AI Service Cache HIT: %s",
                cache_key,
            )

            cached_result = dict(
                cached
            )

            cached_result[
                "cached"
            ] = True

            return cached_result

        # -------------------------------------------------
        # Routes
        # -------------------------------------------------

        routes = {

            # SALES
            "sales_prediction":
                self.sales_analysis,

            "sales":
                self.sales_analysis,

            # INVENTORY
            "inventory_prediction":
                self.inventory_analysis,

            "inventory":
                self.inventory_analysis,

            # CUSTOMER
            "customer_segmentation":
                self.customer_analysis,

            "customer":
                self.customer_analysis,

            # FORECAST
            "demand_forecasting":
                self.forecast_analysis,

            "forecast":
                self.forecast_analysis,
        }

        if model not in routes:

            logger.warning(
                "Unknown AI model requested: %s",
                model,
            )

            return {

                "status":
                    "error",

                "model":
                    model,

                "message":
                    f"Unknown model: {model}",

                "available_models":
                    [
                        "sales_prediction",
                        "inventory_prediction",
                        "customer_segmentation",
                        "demand_forecasting",
                    ],

                "result":
                    {},
            }

        start_time = time.time()

        try:

            # -------------------------------------------------
            # Execute selected model
            # -------------------------------------------------

            result = routes[
                model
            ](
                question=question
            )

            execution_time = round(
                time.time()
                - start_time,
                3,
            )

            # -------------------------------------------------
            # Normalize result
            # -------------------------------------------------

            result = self._normalize_result(
                result,
                model,
                execution_time,
            )

            # -------------------------------------------------
            # Store question
            # -------------------------------------------------

            result.setdefault(
                "question",
                question,
            )

            # -------------------------------------------------
            # Cache only successful results
            # -------------------------------------------------

            if (
                result.get(
                    "status"
                )
                == "success"
            ):

                with AIService._lock:

                    AIService._cache[
                        cache_key
                    ] = dict(
                        result
                    )

            return result

        except Exception as error:

            execution_time = round(
                time.time()
                - start_time,
                3,
            )

            logger.exception(
                "AI analysis failed for %s",
                model,
            )

            return {

                "status":
                    "error",

                "model":
                    model,

                "question":
                    question,

                "message":
                    str(error),

                "result":
                    {},

                "execution_time":
                    execution_time,
            }

    # =====================================================
    # SALES ANALYSIS
    # =====================================================

    def sales_analysis(
        self,
        question: str = "",
    ):

        logger.info(
            "Running Sales Analysis | question=%s",
            question,
        )

        start_time = time.time()

        try:

            model = (
                self.get_sales_model()
            )

            result = self._run_model_pipeline(
                "sales_prediction",
                model,
                question,
            )

            execution_time = round(
                time.time()
                - start_time,
                3,
            )

            if result is None:

                logger.error(
                    "SalesPrediction returned None."
                )

                return {

                    "module":
                        "Sales Prediction",

                    "status":
                        "error",

                    "message":
                        (
                            "SalesPrediction.run_pipeline() "
                            "returned no result."
                        ),

                    "result":
                        {},

                    "question":
                        question,

                    "execution_time":
                        execution_time,
                }

            return {

                "module":
                    "Sales Prediction",

                "status":
                    "success",

                "result":
                    result,

                "question":
                    question,

                "execution_time":
                    execution_time,
            }

        except Exception as error:

            logger.exception(
                "Sales analysis failed"
            )

            return {

                "module":
                    "Sales Prediction",

                "status":
                    "error",

                "message":
                    str(error),

                "result":
                    {},

                "question":
                    question,

                "execution_time":
                    round(
                        time.time()
                        - start_time,
                        3,
                    ),
            }

    # =====================================================
    # INVENTORY ANALYSIS
    # =====================================================

    def inventory_analysis(
        self,
        question: str = "",
    ):

        logger.info(
            "Running Inventory Analysis | question=%s",
            question,
        )

        start_time = time.time()

        try:

            model = (
                self.get_inventory_model()
            )

            result = self._run_model_pipeline(
                "inventory_prediction",
                model,
                question,
            )

            execution_time = round(
                time.time()
                - start_time,
                3,
            )

            if result is None:

                logger.error(
                    "InventoryPrediction returned None."
                )

                return {

                    "module":
                        "Inventory Prediction",

                    "status":
                        "error",

                    "message":
                        (
                            "InventoryPrediction.run_pipeline() "
                            "returned no result."
                        ),

                    "result":
                        {},

                    "question":
                        question,

                    "execution_time":
                        execution_time,
                }

            return {

                "module":
                    "Inventory Prediction",

                "status":
                    "success",

                "result":
                    result,

                "question":
                    question,

                "execution_time":
                    execution_time,
            }

        except Exception as error:

            logger.exception(
                "Inventory analysis failed"
            )

            return {

                "module":
                    "Inventory Prediction",

                "status":
                    "error",

                "message":
                    str(error),

                "result":
                    {},

                "question":
                    question,

                "execution_time":
                    round(
                        time.time()
                        - start_time,
                        3,
                    ),
            }

    # =====================================================
    # CUSTOMER ANALYSIS
    # =====================================================

    def customer_analysis(
        self,
        question: str = "",
    ):

        logger.info(
            "Running Customer Analysis | question=%s",
            question,
        )

        start_time = time.time()

        try:

            model = (
                self.get_customer_model()
            )

            result = self._run_model_pipeline(
                "customer_segmentation",
                model,
                question,
            )

            execution_time = round(
                time.time()
                - start_time,
                3,
            )

            if result is None:

                logger.error(
                    "CustomerSegmentation returned None."
                )

                return {

                    "module":
                        "Customer Segmentation",

                    "status":
                        "error",

                    "message":
                        (
                            "CustomerSegmentation.run_pipeline() "
                            "returned no result."
                        ),

                    "result":
                        {},

                    "question":
                        question,

                    "execution_time":
                        execution_time,
                }

            return {

                "module":
                    "Customer Segmentation",

                "status":
                    "success",

                "result":
                    result,

                "question":
                    question,

                "execution_time":
                    execution_time,
            }

        except Exception as error:

            logger.exception(
                "Customer analysis failed"
            )

            return {

                "module":
                    "Customer Segmentation",

                "status":
                    "error",

                "message":
                    str(error),

                "result":
                    {},

                "question":
                    question,

                "execution_time":
                    round(
                        time.time()
                        - start_time,
                        3,
                    ),
            }

    # =====================================================
    # FORECAST ANALYSIS
    # =====================================================

    def forecast_analysis(
        self,
        question: str = "",
    ):

        logger.info(
            "Running Demand Forecasting | question=%s",
            question,
        )

        start_time = time.time()

        try:

            model = (
                self.get_forecast_model()
            )

            result = self._run_model_pipeline(
                "demand_forecasting",
                model,
                question,
            )

            execution_time = round(
                time.time()
                - start_time,
                3,
            )

            if result is None:

                logger.error(
                    "DemandForecasting returned None."
                )

                return {

                    "module":
                        "Demand Forecasting",

                    "status":
                        "error",

                    "message":
                        (
                            "DemandForecasting.run_pipeline() "
                            "returned no result."
                        ),

                    "result":
                        {},

                    "question":
                        question,

                    "execution_time":
                        execution_time,
                }

            return {

                "module":
                    "Demand Forecasting",

                "status":
                    "success",

                "result":
                    result,

                "question":
                    question,

                "execution_time":
                    execution_time,
            }

        except Exception as error:

            logger.exception(
                "Forecast analysis failed"
            )

            return {

                "module":
                    "Demand Forecasting",

                "status":
                    "error",

                "message":
                    str(error),

                "result":
                    {},

                "question":
                    question,

                "execution_time":
                    round(
                        time.time()
                        - start_time,
                        3,
                    ),
            }

    # =====================================================
    # RUN ALL MODELS
    # =====================================================

    def run_all_models(
        self,
        question: str = "",
    ):

        logger.info(
            "Running all enterprise AI models"
        )

        return {

            "sales":
                self.run_business_analysis(
                    "sales_prediction",
                    question,
                ),

            "inventory":
                self.run_business_analysis(
                    "inventory_prediction",
                    question,
                ),

            "forecast":
                self.run_business_analysis(
                    "demand_forecasting",
                    question,
                ),

            "customer":
                self.run_business_analysis(
                    "customer_segmentation",
                    question,
                ),
        }

    # =====================================================
    # SAFE FLOAT
    # =====================================================

    @staticmethod
    def _safe_float(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:

            if value is None:
                return default

            if isinstance(
                value,
                bool,
            ):
                return float(value)

            if isinstance(
                value,
                str,
            ):

                value = (
                    value
                    .replace(",", "")
                    .replace("$", "")
                    .replace("%", "")
                    .strip()
                )

            result = float(
                value
            )

            if result != result:
                return default

            if result in (
                float("inf"),
                float("-inf"),
            ):
                return default

            return result

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):

            return default

    # =====================================================
    # SAFE INTEGER
    # =====================================================

    @staticmethod
    def _safe_int(
        value: Any,
        default: int = 0,
    ) -> int:

        try:

            if value is None:
                return default

            if isinstance(
                value,
                bool,
            ):
                return int(value)

            if isinstance(
                value,
                str,
            ):

                value = (
                    value
                    .replace(",", "")
                    .strip()
                )

            return max(
                0,
                int(
                    float(value)
                ),
            )

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):

            return default

    # =====================================================
    # FIND VALUE IN NESTED RESULT
    # =====================================================

    @staticmethod
    def _find_value(
        data: Any,
        keys: list[str],
        default: Any = None,
    ) -> Any:

        if data is None:
            return default

        if isinstance(
            data,
            dict,
        ):

            # -------------------------------------------------
            # Direct lookup first
            # -------------------------------------------------

            for key in keys:

                if key in data:

                    value = data[key]

                    if (
                        value is not None
                        and value != ""
                    ):

                        return value

            # -------------------------------------------------
            # Nested lookup
            # -------------------------------------------------

            for value in data.values():

                if isinstance(
                    value,
                    dict,
                ):

                    found = (
                        AIService._find_value(
                            value,
                            keys,
                            None,
                        )
                    )

                    if found is not None:

                        return found

                elif isinstance(
                    value,
                    list,
                ):

                    for item in value:

                        if isinstance(
                            item,
                            dict,
                        ):

                            found = (
                                AIService._find_value(
                                    item,
                                    keys,
                                    None,
                                )
                            )

                            if found is not None:

                                return found

        return default

    # =====================================================
    # EXTRACT SALES METRICS
    # =====================================================

    def _extract_sales_metrics(
        self,
        result: Dict[str, Any],
    ) -> Dict[str, float]:

        value = self._find_value(
            result,
            [
                "predicted_sales",
                "predictedSales",
                "prediction",
                "prediction_value",
                "predicted_value",
                "sales_prediction",
                "forecast_sales",
                "predicted_revenue",
                "sales",
            ],
            0.0,
        )

        return {

            "predicted_sales":
                max(
                    0.0,
                    self._safe_float(
                        value
                    ),
                ),
        }

    # =====================================================
    # EXTRACT INVENTORY METRICS
    # =====================================================

    def _extract_inventory_metrics(
        self,
        result: Dict[str, Any],
    ) -> Dict[str, float]:

        current_stock = self._find_value(
            result,
            [
                "inventory",
                "current_stock",
                "currentStock",
                "inventory_count",
                "inventory_units",
                "stock",
                "stock_level",
                "available_stock",
                "quantity",
                "current_inventory",
            ],
            0.0,
        )

        return {

            "inventory":
                max(
                    0.0,
                    self._safe_float(
                        current_stock
                    ),
                ),
        }

    # =====================================================
    # EXTRACT FORECAST METRICS
    # =====================================================

    def _extract_forecast_metrics(
        self,
        result: Dict[str, Any],
    ) -> Dict[str, float]:

        growth = self._find_value(
            result,
            [
                "forecast_growth",
                "forecastGrowth",
                "growth",
                "growth_rate",
                "growthRate",
                "forecast_change",
                "percentage_change",
                "change_percent",
                "growth_percentage",
            ],
            0.0,
        )

        growth = self._safe_float(
            growth
        )

        return {

            "forecast_growth":
                max(
                    -100.0,
                    min(
                        100.0,
                        growth,
                    ),
                ),
        }

    # =====================================================
    # EXTRACT CUSTOMER METRICS
    # =====================================================

    def _extract_customer_metrics(
        self,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:

        churn = self._find_value(
            result,
            [
                "customer_churn",
                "customerChurn",
                "churn",
                "churn_rate",
                "churnRate",
                "predicted_churn",
                "churn_percentage",
                "churn_percent",
            ],
            0.0,
        )

        customers = self._find_value(
            result,
            [
                "customers",
                "customer_count",
                "customerCount",
                "total_customers",
                "totalCustomers",
                "number_of_customers",
                "customer_total",
            ],
            0,
        )

        churn_value = self._safe_float(
            churn
        )

        return {

            "customer_churn":
                max(
                    0.0,
                    min(
                        100.0,
                        churn_value,
                    ),
                ),

            "customers":
                self._safe_int(
                    customers
                ),
        }

    # =====================================================
    # EXTRACT FINANCIAL METRICS
    # =====================================================

    def _extract_financial_metrics(
        self,
        results: Dict[str, Any],
    ) -> Dict[str, float]:

        revenue = self._find_value(
            results,
            [
                "revenue",
                "total_revenue",
                "totalRevenue",
                "sales_revenue",
                "predicted_revenue",
                "net_revenue",
            ],
            0.0,
        )

        profit = self._find_value(
            results,
            [
                "profit",
                "total_profit",
                "totalProfit",
                "net_profit",
                "netProfit",
                "gross_profit",
            ],
            0.0,
        )

        return {

            "revenue":
                max(
                    0.0,
                    self._safe_float(
                        revenue
                    ),
                ),

            "profit":
                self._safe_float(
                    profit
                ),
        }

    # =====================================================
    # BUILD DECISION INPUT
    # =====================================================

    def build_decision_input(
        self,
        results: Dict[str, Any],
    ) -> Dict[str, Any]:

        if not isinstance(
            results,
            dict,
        ):

            results = {}

        # -------------------------------------------------
        # Get model results
        # -------------------------------------------------

        sales_result = results.get(
            "sales",
            {},
        )

        inventory_result = results.get(
            "inventory",
            {},
        )

        forecast_result = results.get(
            "forecast",
            {},
        )

        customer_result = results.get(
            "customer",
            {},
        )

        # -------------------------------------------------
        # Unwrap service response
        # -------------------------------------------------

        sales_data = (
            sales_result.get(
                "result",
                sales_result,
            )
            if isinstance(
                sales_result,
                dict,
            )
            else {}
        )

        inventory_data = (
            inventory_result.get(
                "result",
                inventory_result,
            )
            if isinstance(
                inventory_result,
                dict,
            )
            else {}
        )

        forecast_data = (
            forecast_result.get(
                "result",
                forecast_result,
            )
            if isinstance(
                forecast_result,
                dict,
            )
            else {}
        )

        customer_data = (
            customer_result.get(
                "result",
                customer_result,
            )
            if isinstance(
                customer_result,
                dict,
            )
            else {}
        )

        # -------------------------------------------------
        # Extract metrics
        # -------------------------------------------------

        sales_metrics = (
            self._extract_sales_metrics(
                sales_data
            )
        )

        inventory_metrics = (
            self._extract_inventory_metrics(
                inventory_data
            )
        )

        forecast_metrics = (
            self._extract_forecast_metrics(
                forecast_data
            )
        )

        customer_metrics = (
            self._extract_customer_metrics(
                customer_data
            )
        )

        # -------------------------------------------------
        # Financial metrics
        # -------------------------------------------------
        #
        # Search the complete model response because
        # revenue/profit can be returned by different
        # enterprise models.
        #

        financial_metrics = (
            self._extract_financial_metrics(
                results
            )
        )

        # -------------------------------------------------
        # Unified Decision Engine Input
        # -------------------------------------------------

        decision_input = {

            "predicted_sales":
                sales_metrics.get(
                    "predicted_sales",
                    0.0,
                ),

            "inventory":
                inventory_metrics.get(
                    "inventory",
                    0.0,
                ),

            "forecast_growth":
                forecast_metrics.get(
                    "forecast_growth",
                    0.0,
                ),

            "customer_churn":
                customer_metrics.get(
                    "customer_churn",
                    0.0,
                ),

            "revenue":
                financial_metrics.get(
                    "revenue",
                    0.0,
                ),

            "profit":
                financial_metrics.get(
                    "profit",
                    0.0,
                ),

            "customers":
                customer_metrics.get(
                    "customers",
                    0,
                ),
        }

        logger.info(
            "Decision input constructed: %s",
            decision_input,
        )

        return decision_input

    # =====================================================
    # RUN ENTERPRISE DECISION ENGINE
    # =====================================================

    def run_decision_engine(
        self,
        db,
        question: str = "",
    ) -> Dict[str, Any]:

        logger.info(
            "Running Enterprise Decision Engine."
        )

        start_time = time.time()

        try:

            if db is None:

                return {

                    "status":
                        "error",

                    "module":
                        "Enterprise Decision Intelligence",

                    "message":
                        "Database session is required.",

                    "decision":
                        {},

                    "execution_time":
                        round(
                            time.time()
                            - start_time,
                            3,
                        ),
                }

            # -------------------------------------------------
            # Run all AI models
            # -------------------------------------------------

            model_results = (
                self.run_all_models(
                    question=question
                )
            )

            # -------------------------------------------------
            # Detect failed models
            # -------------------------------------------------

            failed_models = []

            for (
                model_name,
                result,
            ) in model_results.items():

                if not isinstance(
                    result,
                    dict,
                ):

                    failed_models.append(
                        model_name
                    )

                    continue

                if (
                    result.get(
                        "status"
                    )
                    == "error"
                ):

                    failed_models.append(
                        model_name
                    )

            # -------------------------------------------------
            # Build unified decision input
            # -------------------------------------------------

            decision_input = (
                self.build_decision_input(
                    model_results
                )
            )

            # -------------------------------------------------
            # Run Decision Service
            # -------------------------------------------------

            decision_service = (
                DecisionService(
                    db=db
                )
            )

            decision_result = (
                decision_service.generate_decision(
                    decision_input
                )
            )

            execution_time = round(
                time.time()
                - start_time,
                3,
            )

            # -------------------------------------------------
            # Validate decision result
            # -------------------------------------------------

            if not isinstance(
                decision_result,
                dict,
            ):

                return {

                    "status":
                        "error",

                    "module":
                        "Enterprise Decision Intelligence",

                    "message":
                        (
                            "Decision Service returned "
                            "an invalid response."
                        ),

                    "models":
                        model_results,

                    "decision_input":
                        decision_input,

                    "decision":
                        {},

                    "failed_models":
                        failed_models,

                    "execution_time":
                        execution_time,
                }

            # -------------------------------------------------
            # Decision service error
            # -------------------------------------------------

            if (
                decision_result.get(
                    "status"
                )
                == "error"
            ):

                return {

                    "status":
                        "error",

                    "module":
                        "Enterprise Decision Intelligence",

                    "message":
                        decision_result.get(
                            "message",
                            "Decision generation failed.",
                        ),

                    "models":
                        model_results,

                    "decision_input":
                        decision_input,

                    "decision":
                        {},

                    "failed_models":
                        failed_models,

                    "execution_time":
                        execution_time,
                }

            # -------------------------------------------------
            # Successful result
            # -------------------------------------------------

            return {

                "status":
                    "success",

                "module":
                    "Enterprise Decision Intelligence",

                "decision_id":
                    decision_result.get(
                        "decision_id"
                    ),

                "decision":
                    decision_result.get(
                        "decision",
                        {},
                    ),

                "decision_input":
                    decision_input,

                "models":
                    model_results,

                "failed_models":
                    failed_models,

                "execution_time":
                    execution_time,
            }

        except Exception as error:

            logger.exception(
                "Enterprise Decision Engine failed."
            )

            return {

                "status":
                    "error",

                "module":
                    "Enterprise Decision Intelligence",

                "message":
                    str(error),

                "decision":
                    {},

                "execution_time":
                    round(
                        time.time()
                        - start_time,
                        3,
                    ),
            }

    # =====================================================
    # HEALTH
    # =====================================================

    def health(
        self,
    ):

        return {

            "service":
                "Enterprise AI Service",

            "status":
                "healthy",

            "models":
                {

                    "sales":
                        AIService._sales_model
                        is not None,

                    "inventory":
                        AIService._inventory_model
                        is not None,

                    "forecast":
                        AIService._forecast_model
                        is not None,

                    "customer":
                        AIService._customer_model
                        is not None,
                },

            "cache":
                {

                    "enabled":
                        True,

                    "entries":
                        list(
                            AIService._cache.keys()
                        ),

                    "count":
                        len(
                            AIService._cache
                        ),
                },
        }

    # =====================================================
    # CLEAR CACHE
    # =====================================================

    def clear_cache(
        self,
    ):

        with AIService._lock:

            AIService._cache.clear()

        logger.info(
            "Enterprise AI cache cleared"
        )

        return {

            "status":
                "success",

            "message":
                "AI cache cleared",

            "entries":
                0,
        }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    service = AIService()

    print(
        "\nEnterprise AI Service Health:\n"
    )

    print(
        service.health()
    )

    print(
        "\nAvailable Business Models:\n"
    )

    print(
        [
            "sales_prediction",
            "inventory_prediction",
            "demand_forecasting",
            "customer_segmentation",
        ]
    )