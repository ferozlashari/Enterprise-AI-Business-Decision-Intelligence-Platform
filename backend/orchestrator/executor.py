
"""
Enterprise AI Business Decision Intelligence Platform

LangGraph Executor

Author : Feroz Ali
"""

import logging
import time


from backend.multi_agent.graph import graph


logger = logging.getLogger(
    "LangGraphExecutor"
)


class Executor:

    # =====================================================
    # SHARED LANGGRAPH
    # =====================================================

    _graph = graph

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        self.graph = Executor._graph

        logger.info(
            "LangGraph Executor initialized"
        )

    # =====================================================
    # NORMALIZE PLAN
    # =====================================================

    def normalize_plan(
        self,
        plan
    ):

        # -------------------------------------------------
        # Default enterprise workflow
        # -------------------------------------------------

        if not plan:

            return [

                "data",

                "sales",

                "inventory",

                "forecast",

                "customer",

                "risk",

                "decision",

                "executive"

            ]

        # -------------------------------------------------
        # Dictionary plan
        # -------------------------------------------------

        if isinstance(
            plan,
            dict
        ):

            # New Planner format

            if "workflow" in plan:

                return self.normalize_plan(
                    plan["workflow"]
                )

            # Older format

            if "tasks" in plan:

                return self.normalize_plan(
                    plan["tasks"]
                )

            # Older nested format

            if "plan" in plan:

                return self.normalize_plan(
                    plan["plan"]
                )

        # -------------------------------------------------
        # String plan
        # -------------------------------------------------

        if isinstance(
            plan,
            str
        ):

            return [
                plan.strip().lower()
            ]

        # -------------------------------------------------
        # List / Tuple
        # -------------------------------------------------

        if isinstance(
            plan,
            (list, tuple)
        ):

            normalized = []

            for item in plan:

                if isinstance(
                    item,
                    str
                ):

                    item = item.strip().lower()

                    if item:

                        normalized.append(
                            item
                        )

            return list(
                dict.fromkeys(
                    normalized
                )
            )

        # -------------------------------------------------
        # Unknown format
        # -------------------------------------------------

        logger.warning(
            "Unknown plan format: %s",
            type(plan)
        )

        return []

    # =====================================================
    # VALIDATE WORKFLOW
    # =====================================================

    def validate_plan(
        self,
        plan
    ):

        supported_nodes = {

            "data",

            "sales",

            "inventory",

            "forecast",

            "customer",

            "risk",

            "decision",

            "executive",

            "report"

        }

        valid = []

        unknown = []

        for node in plan:

            node = str(
                node
            ).strip().lower()

            if node in supported_nodes:

                valid.append(
                    node
                )

            else:

                unknown.append(
                    node
                )

        if unknown:

            logger.warning(
                "Unknown workflow nodes ignored: %s",
                unknown
            )

        return list(
            dict.fromkeys(
                valid
            )
        )

    # =====================================================
    # BUILD INITIAL STATE
    # =====================================================

    def build_initial_state(
        self,
        question,
        plan,
        start_time
    ):

        return {

            # -------------------------------------------------
            # User question
            # -------------------------------------------------

            "question":
                question,

            # -------------------------------------------------
            # Planner workflow
            # -------------------------------------------------

            "plan":
                plan,

            # -------------------------------------------------
            # Current node
            # -------------------------------------------------

            "current":
                "start",

            # -------------------------------------------------
            # Enterprise data
            # -------------------------------------------------

            "data":
                {},

            # -------------------------------------------------
            # Sales
            # -------------------------------------------------

            "sales":
                {},

            # -------------------------------------------------
            # Forecast
            # -------------------------------------------------

            "forecast":
                {},

            # -------------------------------------------------
            # Inventory
            # -------------------------------------------------

            "inventory":
                {},

            # -------------------------------------------------
            # Customer
            # -------------------------------------------------

            "customer":
                {},

            # -------------------------------------------------
            # Risk
            # -------------------------------------------------

            "risk":
                {},

            # -------------------------------------------------
            # Decision
            # -------------------------------------------------

            "decision":
                {},

            # -------------------------------------------------
            # Executive
            # -------------------------------------------------

            "executive":
                {},

            # -------------------------------------------------
            # Report
            # -------------------------------------------------

            "report":
                {},

            # -------------------------------------------------
            # Recommendations
            # -------------------------------------------------

            "recommendations":
                {},

            # -------------------------------------------------
            # Messages
            # -------------------------------------------------

            "messages":
                [],

            # -------------------------------------------------
            # Metadata
            # -------------------------------------------------

            "metadata": {

                "start_time":
                    start_time,

                "nodes":
                    [],

                "status":
                    "started"

            }

        }

    # =====================================================
    # EXECUTE LANGGRAPH WORKFLOW
    # =====================================================

    def execute(
        self,
        request,
        question=""
    ):

        start_time = time.time()

        try:

            logger.info(
                "LangGraph Execution Started"
            )

            # =============================================
            # EXTRACT REQUEST
            # =============================================

            if isinstance(
                request,
                dict
            ):

                plan = request.get(
                    "plan",
                    []
                )

                question = request.get(
                    "question",
                    question
                )

            else:

                plan = request

            # =============================================
            # NORMALIZE PLAN
            # =============================================

            plan = self.normalize_plan(
                plan
            )

            # =============================================
            # VALIDATE PLAN
            # =============================================

            plan = self.validate_plan(
                plan
            )

            # =============================================
            # QUESTION VALIDATION
            # =============================================

            question = str(
                question or ""
            ).strip()

            if not question:

                return {

                    "status":
                        "error",

                    "message":
                        "Question cannot be empty.",

                    "execution_time":
                        round(
                            time.time()
                            - start_time,
                            3
                        )

                }

            # =============================================
            # FALLBACK PLAN
            # =============================================

            if not plan:

                plan = [

                    "data",

                    "executive"

                ]

            logger.info(
                "Execution Plan: %s",
                plan
            )

            # =============================================
            # INITIAL STATE
            # =============================================

            initial_state = (
                self.build_initial_state(
                    question,
                    plan,
                    start_time
                )
            )

            # =============================================
            # EXECUTE GRAPH
            # =============================================

            result = self.graph.invoke(
                initial_state
            )

            # =============================================
            # NORMALIZE GRAPH RESULT
            # =============================================

            if not isinstance(
                result,
                dict
            ):

                result = {}

            # =============================================
            # EXECUTION TIME
            # =============================================

            execution_time = round(

                time.time()
                - start_time,

                3

            )

            # =============================================
            # METADATA
            # =============================================

            metadata = result.get(
                "metadata",
                {}
            )

            if not isinstance(
                metadata,
                dict
            ):

                metadata = {}

            metadata.update({

                "execution_time":
                    execution_time,

                "status":
                    "completed",

                "plan":
                    plan,

                "question":
                    question

            })

            result["metadata"] = metadata

            # =============================================
            # TOP-LEVEL EXECUTION INFORMATION
            # =============================================

            result["status"] = (
                result.get(
                    "status",
                    "success"
                )
            )

            result["question"] = question

            result["plan"] = plan

            # =============================================
            # LOG
            # =============================================

            logger.info(
                "LangGraph Completed in %ss",
                execution_time
            )

            return result

        # =============================================
        # ERROR HANDLING
        # =============================================

        except Exception as error:

            execution_time = round(

                time.time()
                - start_time,

                3

            )

            logger.exception(
                "LangGraph Execution Failed"
            )

            return {

                "status":
                    "error",

                "question":
                    question,

                "plan":
                    plan
                    if "plan" in locals()
                    else [],

                "message":
                    str(error),

                "execution_time":
                    execution_time,

                "metadata": {

                    "status":
                        "failed",

                    "execution_time":
                        execution_time

                }

            }

    # =====================================================
    # HEALTH
    # =====================================================

    def health(self):

        try:

            return {

                "service":
                    "LangGraph Executor",

                "status":
                    "healthy",

                "graph":
                    self.graph is not None,

                "supported_nodes": [

                    "data",
                    "sales",
                    "inventory",
                    "forecast",
                    "customer",
                    "risk",
                    "decision",
                    "executive",
                    "report"

                ]

            }

        except Exception as error:

            logger.exception(
                "Executor health check failed"
            )

            return {

                "service":
                    "LangGraph Executor",

                "status":
                    "error",

                "message":
                    str(error)

            }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    executor = Executor()

    questions = [

        "What are our top products?",

        "Summarize current inventory risk.",

        "What are the forecast risks?",

        "Which customers are most valuable?",

        "What are our biggest business risks?",

        "What should management prioritize this quarter?"

    ]

    for question in questions:

        print("\n" + "=" * 70)

        print(
            f"QUESTION: {question}"
        )

        print("=" * 70)

        result = executor.execute({

            "plan": [

                "data",

                "sales",

                "inventory",

                "forecast",

                "customer",

                "risk",

                "decision",

                "executive"

            ],

            "question":
                question

        })

        print(
            result
        )

