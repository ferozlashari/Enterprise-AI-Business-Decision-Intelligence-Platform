
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Dynamic LangGraph Workflow

Author : Feroz Ali
=========================================================
"""

from langgraph.graph import (
    StateGraph,
    END
)

from backend.multi_agent.state import AgentState

from backend.multi_agent.nodes import (
    data_node,
    sales_node,
    forecast_node,
    inventory_node,
    customer_node,
    risk_node,
    decision_node,
    report_node,
    executive_node
)


# =========================================================
# ENTERPRISE WORKFLOW
# =========================================================

WORKFLOW = [

    "data",

    "sales",

    "inventory",

    "forecast",

    "customer",

    "risk",

    "decision",

    "report",

    "executive"

]


# =========================================================
# VALID BUSINESS AGENTS
# =========================================================

VALID_NODES = set(
    WORKFLOW
)


# =========================================================
# CREATE GRAPH
# =========================================================

builder = StateGraph(
    AgentState
)


# =========================================================
# REGISTER NODES
# =========================================================

builder.add_node(
    "data",
    data_node
)

builder.add_node(
    "sales",
    sales_node
)

builder.add_node(
    "inventory",
    inventory_node
)

builder.add_node(
    "forecast",
    forecast_node
)

builder.add_node(
    "customer",
    customer_node
)

builder.add_node(
    "risk",
    risk_node
)

builder.add_node(
    "decision",
    decision_node
)

builder.add_node(
    "report",
    report_node
)

builder.add_node(
    "executive",
    executive_node
)


# =========================================================
# ENTRY POINT
# =========================================================
#
# Enterprise data must always be loaded first.
#
# =========================================================

builder.set_entry_point(
    "data"
)


# =========================================================
# NORMALIZE PLAN
# =========================================================

def normalize_plan(plan):

    """
    Normalize planner output into a clean list of
    valid workflow node names.
    """

    # -----------------------------------------------------
    # Empty plan
    # -----------------------------------------------------

    if not plan:

        return WORKFLOW.copy()


    # -----------------------------------------------------
    # Dictionary
    # -----------------------------------------------------

    if isinstance(
        plan,
        dict
    ):

        if "workflow" in plan:

            return normalize_plan(
                plan["workflow"]
            )


        if "tasks" in plan:

            return normalize_plan(
                plan["tasks"]
            )


        if "plan" in plan:

            return normalize_plan(
                plan["plan"]
            )


        # Planner may return matched_agents

        if "matched_agents" in plan:

            return normalize_plan(
                plan["matched_agents"]
            )


        return WORKFLOW.copy()


    # -----------------------------------------------------
    # String
    # -----------------------------------------------------

    if isinstance(
        plan,
        str
    ):

        plan = [
            plan
        ]


    # -----------------------------------------------------
    # List / Tuple / Set
    # -----------------------------------------------------

    if isinstance(
        plan,
        (list, tuple, set)
    ):

        normalized = []


        for item in plan:

            if item is None:

                continue


            item = str(
                item
            ).strip().lower()


            if not item:

                continue


            # -------------------------------------------------
            # Normalize aliases
            # -------------------------------------------------

            aliases = {

                "sales_prediction":
                    "sales",

                "sales-analysis":
                    "sales",

                "sales_analysis":
                    "sales",


                "inventory_prediction":
                    "inventory",

                "inventory-analysis":
                    "inventory",

                "inventory_analysis":
                    "inventory",


                "customer_segmentation":
                    "customer",

                "customer-analysis":
                    "customer",

                "customer_analysis":
                    "customer",


                "demand_forecasting":
                    "forecast",

                "forecasting":
                    "forecast",

                "forecast_analysis":
                    "forecast",


                "executive_analysis":
                    "executive",

                "executive_summary":
                    "executive"

            }


            item = aliases.get(
                item,
                item
            )


            # -------------------------------------------------
            # Keep only valid nodes
            # -------------------------------------------------

            if item in VALID_NODES:

                normalized.append(
                    item
                )


        # -------------------------------------------------
        # Remove duplicates while preserving order
        # -------------------------------------------------

        normalized = list(
            dict.fromkeys(
                normalized
            )
        )


        if normalized:

            return normalized


    # -----------------------------------------------------
    # Fallback
    # -----------------------------------------------------

    return WORKFLOW.copy()


# =========================================================
# BUILD EXECUTION PLAN
# =========================================================

def build_execution_plan(
    plan
):

    """
    Build a deterministic execution plan.

    Data always runs first.

    Other agents follow enterprise workflow order.

    Executive synthesis is included only if explicitly
    requested or if the planner selected the full workflow.
    """

    normalized = normalize_plan(
        plan
    )


    # -----------------------------------------------------
    # DATA MUST ALWAYS BE FIRST
    # -----------------------------------------------------

    requested = [

        node

        for node in normalized

        if node != "data"

    ]


    # -----------------------------------------------------
    # Determine whether executive was requested
    # -----------------------------------------------------

    executive_requested = (
        "executive"
        in requested
    )


    # -----------------------------------------------------
    # Remove executive temporarily
    # -----------------------------------------------------

    requested = [

        node

        for node in requested

        if node != "executive"

    ]


    # -----------------------------------------------------
    # Order according to enterprise workflow
    # -----------------------------------------------------

    ordered = []


    for node in WORKFLOW:

        if node in requested:

            ordered.append(
                node
            )


    # -----------------------------------------------------
    # Add executive only when requested
    # -----------------------------------------------------

    if executive_requested:

        ordered.append(
            "executive"
        )


    # -----------------------------------------------------
    # Final plan
    # -----------------------------------------------------

    return [

        "data",

        *ordered

    ]


# =========================================================
# GET NEXT NODE
# =========================================================

def next_step(
    current_node,
    state
):

    """
    Find the next node from the planner-selected
    execution plan.
    """

    plan = build_execution_plan(
        state.get(
            "plan",
            WORKFLOW
        )
    )


    try:

        current_index = plan.index(
            current_node
        )

    except ValueError:

        current_index = -1


    # -----------------------------------------------------
    # Find next node
    # -----------------------------------------------------

    if (
        current_index + 1
        <
        len(plan)
    ):

        return plan[
            current_index + 1
        ]


    # -----------------------------------------------------
    # Workflow completed
    # -----------------------------------------------------

    return END


# =========================================================
# DATA ROUTER
# =========================================================

def after_data(
    state
):

    return next_step(
        "data",
        state
    )


# =========================================================
# SALES ROUTER
# =========================================================

def after_sales(
    state
):

    return next_step(
        "sales",
        state
    )


# =========================================================
# INVENTORY ROUTER
# =========================================================

def after_inventory(
    state
):

    return next_step(
        "inventory",
        state
    )


# =========================================================
# FORECAST ROUTER
# =========================================================

def after_forecast(
    state
):

    return next_step(
        "forecast",
        state
    )


# =========================================================
# CUSTOMER ROUTER
# =========================================================

def after_customer(
    state
):

    return next_step(
        "customer",
        state
    )


# =========================================================
# RISK ROUTER
# =========================================================

def after_risk(
    state
):

    return next_step(
        "risk",
        state
    )


# =========================================================
# DECISION ROUTER
# =========================================================

def after_decision(
    state
):

    return next_step(
        "decision",
        state
    )


# =========================================================
# REPORT ROUTER
# =========================================================

def after_report(
    state
):

    return next_step(
        "report",
        state
    )


# =========================================================
# EXECUTIVE ROUTER
# =========================================================

def after_executive(
    state
):

    return END


# =========================================================
# CONDITIONAL EDGES
# =========================================================

builder.add_conditional_edges(
    "data",
    after_data
)

builder.add_conditional_edges(
    "sales",
    after_sales
)

builder.add_conditional_edges(
    "inventory",
    after_inventory
)

builder.add_conditional_edges(
    "forecast",
    after_forecast
)

builder.add_conditional_edges(
    "customer",
    after_customer
)

builder.add_conditional_edges(
    "risk",
    after_risk
)

builder.add_conditional_edges(
    "decision",
    after_decision
)

builder.add_conditional_edges(
    "report",
    after_report
)

builder.add_conditional_edges(
    "executive",
    after_executive
)


# =========================================================
# COMPILE GRAPH
# =========================================================

graph = builder.compile()


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print(
        "\nEnterprise AI LangGraph"
    )


    print(
        "Graph compiled successfully."
    )


    print(
        "\nAvailable Workflow Nodes:"
    )


    for node in WORKFLOW:

        print(
            f"  -> {node}"
        )


    # -----------------------------------------------------
    # Test plans
    # -----------------------------------------------------

    test_plans = [

        ["data", "sales"],

        ["data", "inventory"],

        ["data", "forecast"],

        ["data", "customer"],

        ["data", "sales", "executive"],

        ["data", "sales", "inventory", "executive"]

    ]


    print(
        "\nExecution Plan Tests:"
    )


    for test_plan in test_plans:

        print(
            f"\nInput : {test_plan}"
        )


        print(
            f"Output: "
            f"{build_execution_plan(test_plan)}"
        )

