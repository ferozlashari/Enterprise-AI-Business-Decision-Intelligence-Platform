
"""
Enterprise AI Business Decision Intelligence Platform

LangGraph Nodes

Author : Feroz Ali
"""

import logging
import time


from backend.services.ai_service import (
    AIService
)

from backend.services.report_service import (
    ReportService
)

from backend.services.dashboard_service import (
    DashboardService
)

from backend.services.decision_service import (
    DecisionService
)


logger = logging.getLogger(
    "LangGraph"
)


# =========================================================
# LAZY SERVICES
# =========================================================

_ai_service = None

_report_service = None

_decision_service = None

_dashboard_service = None


# =========================================================
# AI SERVICE
# =========================================================

def get_ai_service():

    global _ai_service


    if _ai_service is None:

        logger.info(
            "Initializing AIService"
        )

        _ai_service = AIService()


    return _ai_service


# =========================================================
# REPORT SERVICE
# =========================================================

def get_report_service():

    global _report_service


    if _report_service is None:

        logger.info(
            "Initializing ReportService"
        )

        _report_service = ReportService()


    return _report_service


# =========================================================
# DECISION SERVICE
# =========================================================

def get_decision_service():

    global _decision_service


    if _decision_service is None:

        logger.info(
            "Initializing DecisionService"
        )

        _decision_service = DecisionService()


    return _decision_service


# =========================================================
# DASHBOARD SERVICE
# =========================================================

def get_dashboard_service():

    global _dashboard_service


    if _dashboard_service is None:

        logger.info(
            "Initializing DashboardService"
        )

        _dashboard_service = DashboardService()


    return _dashboard_service


# =========================================================
# SAFE DICT
# =========================================================

def ensure_dict(
    value
):

    if isinstance(
        value,
        dict
    ):

        return value


    return {

        "status":
            "success",

        "result":
            value

    }


# =========================================================
# EXTRACT MODEL RESULT
# =========================================================

def extract_result(
    value
):

    """
    Extract the actual model result from
    the standard AIService response.

    Example:

        {
            "module": "Sales Prediction",
            "status": "success",
            "result": {...}
        }

    returns:

        {...}
    """

    value = ensure_dict(
        value
    )


    result = value.get(
        "result"
    )


    if isinstance(
        result,
        dict
    ):

        return result


    if result is None:

        return {}


    return {

        "value":
            result

    }


# =========================================================
# GENERIC NODE EXECUTOR
# =========================================================

def execute_node(
    state,
    node_name,
    function
):

    start = time.time()


    state["current"] = node_name


    try:

        logger.info(
            "Running %s node",
            node_name
        )


        result = function()


        elapsed = round(

            time.time()
            - start,

            2

        )


        # -------------------------------------------------
        # Normalize result
        # -------------------------------------------------

        result = ensure_dict(
            result
        )


        # -------------------------------------------------
        # Store result
        # -------------------------------------------------

        state[node_name] = result


        # -------------------------------------------------
        # Metadata
        # -------------------------------------------------

        state.setdefault(
            "metadata",
            {}
        )


        state["metadata"].setdefault(
            "nodes",
            []
        )


        if node_name not in (
            state[
                "metadata"
            ][
                "nodes"
            ]
        ):

            state[
                "metadata"
            ][
                "nodes"
            ].append(
                node_name
            )


        state[
            "metadata"
        ][
            node_name
        ] = {

            "status":
                result.get(
                    "status",
                    "success"
                ),

            "execution_time":
                elapsed

        }


        logger.info(
            "%s completed in %ss",
            node_name,
            elapsed
        )


    except Exception as error:

        elapsed = round(

            time.time()
            - start,

            2

        )


        logger.exception(
            "%s failed",
            node_name
        )


        state[node_name] = {

            "status":
                "error",

            "message":
                str(error),

            "result":
                {}

        }


        state.setdefault(
            "metadata",
            {}
        )


        state[
            "metadata"
        ].setdefault(
            "nodes",
            []
        )


        if node_name not in (
            state[
                "metadata"
            ][
                "nodes"
            ]
        ):

            state[
                "metadata"
            ][
                "nodes"
            ].append(
                node_name
            )


        state[
            "metadata"
        ][
            node_name
        ] = {

            "status":
                "error",

            "execution_time":
                elapsed,

            "message":
                str(error)

        }


    return state


# =========================================================
# DATA NODE
# =========================================================

def data_node(
    state
):

    question = str(
        state.get(
            "question",
            ""
        )
        or ""
    ).strip()


    return execute_node(

        state,

        "data",

        lambda: {

            "status":
                "success",

            "message":
                "Enterprise data loaded successfully.",

            "question":
                question

        }

    )


# =========================================================
# SALES NODE
# =========================================================

def sales_node(
    state
):

    """
    Sales intelligence node.

    Used for:

    - Sales performance
    - Revenue
    - Regional sales
    - Profitability
    - Sales trends
    - Product performance
    """

    question = str(
        state.get(
            "question",
            ""
        )
        or ""
    ).strip()


    logger.info(
        "Sales node question: %s",
        question
    )


    return execute_node(

        state,

        "sales",

        lambda:

        get_ai_service().run_business_analysis(

            model="sales_prediction",

            question=question

        )

    )


# =========================================================
# FORECAST NODE
# =========================================================

def forecast_node(
    state
):

    """
    Forecast intelligence node.

    Used for:

    - Sales forecasting
    - Demand prediction
    - Growth
    - Future trends
    """

    question = str(
        state.get(
            "question",
            ""
        )
        or ""
    ).strip()


    logger.info(
        "Forecast node question: %s",
        question
    )


    return execute_node(

        state,

        "forecast",

        lambda:

        get_ai_service().run_business_analysis(

            model="demand_forecasting",

            question=question

        )

    )


# =========================================================
# INVENTORY NODE
# =========================================================

def inventory_node(
    state
):

    """
    Inventory intelligence node.

    Used for:

    - Stock levels
    - Inventory risk
    - Reorder
    - Shortage
    - Warehouse demand
    """

    question = str(
        state.get(
            "question",
            ""
        )
        or ""
    ).strip()


    logger.info(
        "Inventory node question: %s",
        question
    )


    return execute_node(

        state,

        "inventory",

        lambda:

        get_ai_service().run_business_analysis(

            model="inventory_prediction",

            question=question

        )

    )


# =========================================================
# CUSTOMER NODE
# =========================================================

def customer_node(
    state
):

    """
    Customer intelligence node.

    Used for:

    - Customer segmentation
    - Customer value
    - Churn
    - Retention
    """

    question = str(
        state.get(
            "question",
            ""
        )
        or ""
    ).strip()


    logger.info(
        "Customer node question: %s",
        question
    )


    return execute_node(

        state,

        "customer",

        lambda:

        get_ai_service().run_business_analysis(

            model="customer_segmentation",

            question=question

        )

    )


# =========================================================
# RISK NODE
# =========================================================

def risk_node(
    state
):

    """
    Enterprise risk node.

    Combines available business intelligence
    to identify major business risks.
    """

    sales = ensure_dict(
        state.get(
            "sales",
            {}
        )
    )


    forecast = ensure_dict(
        state.get(
            "forecast",
            {}
        )
    )


    inventory = ensure_dict(
        state.get(
            "inventory",
            {}
        )
    )


    customer = ensure_dict(
        state.get(
            "customer",
            {}
        )
    )


    question = str(
        state.get(
            "question",
            ""
        )
        or ""
    ).strip()


    business_data = {

        "question":
            question,

        "sales":
            sales,

        "forecast":
            forecast,

        "inventory":
            inventory,

        "customer":
            customer

    }


    def generate_risk():

        decision_service = (
            get_decision_service()
        )


        # -------------------------------------------------
        # Try dedicated risk method if available
        # -------------------------------------------------

        if hasattr(
            decision_service,
            "generate_risk"
        ):

            try:

                return (
                    decision_service.generate_risk(
                        business_data
                    )
                )

            except TypeError:

                logger.warning(
                    "generate_risk() does not "
                    "accept business_data."
                )


        # -------------------------------------------------
        # Fallback risk analysis
        # -------------------------------------------------

        risks = []


        # -------------------------------------------------
        # Inventory risk
        # -------------------------------------------------

        inventory_result = extract_result(
            inventory
        )


        inventory_value = (
            inventory_result.get(
                "inventory"
            )
        )


        if inventory_value is None:

            inventory_value = (
                inventory_result.get(
                    "stock"
                )
            )


        if inventory_value is None:

            inventory_value = (
                inventory_result.get(
                    "quantity"
                )
            )


        try:

            if (
                inventory_value is not None
                and
                float(
                    inventory_value
                ) <= 0
            ):

                risks.append({

                    "type":
                        "inventory",

                    "severity":
                        "high",

                    "message":
                        (
                            "Inventory availability "
                            "requires attention."
                        )

                })

        except (
            TypeError,
            ValueError
        ):

            pass


        # -------------------------------------------------
        # Forecast risk
        # -------------------------------------------------

        forecast_result = extract_result(
            forecast
        )


        growth = (
            forecast_result.get(
                "growth"
            )
        )


        if growth is None:

            growth = (
                forecast_result.get(
                    "growth_rate"
                )
            )


        if growth is None:

            growth = (
                forecast_result.get(
                    "forecast_growth"
                )
            )


        try:

            if (
                growth is not None
                and
                float(
                    growth
                ) < 0
            ):

                risks.append({

                    "type":
                        "forecast",

                    "severity":
                        "high",

                    "message":
                        (
                            "Forecast indicates "
                            "negative growth."
                        )

                })

        except (
            TypeError,
            ValueError
        ):

            pass


        # -------------------------------------------------
        # Customer churn risk
        # -------------------------------------------------

        customer_result = extract_result(
            customer
        )


        churn = (
            customer_result.get(
                "churn"
            )
        )


        if churn is None:

            churn = (
                customer_result.get(
                    "churn_rate"
                )
            )


        try:

            if (
                churn is not None
                and
                float(
                    churn
                ) > 0.20
            ):

                risks.append({

                    "type":
                        "customer",

                    "severity":
                        "medium",

                    "message":
                        (
                            "Customer churn "
                            "requires attention."
                        )

                })

        except (
            TypeError,
            ValueError
        ):

            pass


        return {

            "status":
                "success",

            "question":
                question,

            "risk_count":
                len(
                    risks
                ),

            "risks":
                risks,

            "business_data":
                business_data

        }


    return execute_node(

        state,

        "risk",

        generate_risk

    )


# =========================================================
# DECISION NODE
# =========================================================

def decision_node(
    state
):

    question = str(
        state.get(
            "question",
            ""
        )
        or ""
    ).strip()


    sales = ensure_dict(
        state.get(
            "sales",
            {}
        )
    )


    forecast = ensure_dict(
        state.get(
            "forecast",
            {}
        )
    )


    inventory = ensure_dict(
        state.get(
            "inventory",
            {}
        )
    )


    customer = ensure_dict(
        state.get(
            "customer",
            {}
        )
    )


    risk = ensure_dict(
        state.get(
            "risk",
            {}
        )
    )


    # -----------------------------------------------------
    # Extract actual model results
    # -----------------------------------------------------

    sales_result = extract_result(
        sales
    )


    forecast_result = extract_result(
        forecast
    )


    inventory_result = extract_result(
        inventory
    )


    customer_result = extract_result(
        customer
    )


    business_data = {

        "question":
            question,

        # Sales
        "sales":
            sales,

        # Forecast
        "forecast":
            forecast,

        # Inventory
        "inventory":
            inventory,

        # Customer
        "customer":
            customer,

        # Risk
        "risk":
            risk,

        # Compatibility fields
        "predicted_sales":
            forecast_result.get(
                "predicted_sales",
                forecast_result.get(
                    "prediction",
                    sales_result.get(
                        "predicted_sales",
                        0
                    )
                )
            ),

        "forecast_growth":
            forecast_result.get(
                "growth",
                forecast_result.get(
                    "growth_rate",
                    0
                )
            ),

        "inventory_stock":
            inventory_result.get(
                "inventory",
                inventory_result.get(
                    "stock",
                    inventory_result.get(
                        "quantity",
                        0
                    )
                )
            ),

        "customer_churn":
            customer_result.get(
                "churn",
                customer_result.get(
                    "churn_rate",
                    0
                )
            )

    }


    def generate_decision():

        decision_service = (
            get_decision_service()
        )


        try:

            return (
                decision_service.generate_decision(
                    business_data
                )
            )

        except TypeError:

            logger.warning(
                "DecisionService.generate_decision "
                "does not accept business_data."
            )

            return (
                decision_service.generate_decision()
            )


    return execute_node(

        state,

        "decision",

        generate_decision

    )


# =========================================================
# REPORT NODE
# =========================================================

def report_node(
    state
):

    question = str(
        state.get(
            "question",
            ""
        )
        or ""
    ).strip()


    def generate_report():

        report_service = (
            get_report_service()
        )


        try:

            return (
                report_service.all_reports(
                    question=question
                )
            )

        except TypeError:

            logger.info(
                "ReportService.all_reports() "
                "does not accept question. "
                "Using legacy call."
            )

            return (
                report_service.all_reports()
            )


    return execute_node(

        state,

        "report",

        generate_report

    )


# =========================================================
# EXECUTIVE NODE
# =========================================================

def executive_node(
    state
):

    """
    Final executive synthesis.

    Combines the outputs of all previously
    executed business intelligence nodes.
    """

    question = str(
        state.get(
            "question",
            ""
        )
        or ""
    ).strip()


    def generate_executive():

        dashboard_service = (
            get_dashboard_service()
        )


        # -------------------------------------------------
        # Prefer question-aware executive dashboard
        # -------------------------------------------------

        try:

            return (
                dashboard_service.executive_dashboard(
                    question=question
                )
            )

        except TypeError:

            logger.info(
                "DashboardService.executive_dashboard() "
                "does not accept question. "
                "Using legacy call."
            )

            return (
                dashboard_service.executive_dashboard()
            )


    return execute_node(

        state,

        "executive",

        generate_executive

    )

