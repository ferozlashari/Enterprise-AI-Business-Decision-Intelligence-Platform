
"""
Enterprise AI Business Decision Intelligence Platform

Enterprise AI Planner

Author : Feroz Ali
"""

import logging
import re


logger = logging.getLogger("EnterprisePlanner")


class Planner:

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        self.agent_keywords = {

            # -------------------------------------------------
            # SALES
            # -------------------------------------------------

            "sales": [

                "sales",
                "sale",
                "product",
                "products",
                "top product",
                "top products",
                "best product",
                "best products",
                "selling",
                "sell",
                "revenue",
                "profit",
                "sales performance",
                "sales trend",
                "sales trends",
                "region",
                "regions",
                "category",
                "categories",
                "discount",
                "order",
                "orders",
                "declining regions",
                "declining sales",
                "sales decline"

            ],

            # -------------------------------------------------
            # INVENTORY
            # -------------------------------------------------

            "inventory": [

                "inventory",
                "stock",
                "stocks",
                "warehouse",
                "warehouses",
                "supply",
                "supplies",
                "shortage",
                "shortages",
                "availability",
                "available stock",
                "stock level",
                "stock levels",
                "reorder",
                "reorder point",
                "reorder points",
                "safety stock",
                "overstock",
                "understock",
                "out of stock",
                "inventory risk",
                "inventory risks",
                "inventory shortage",
                "stock shortage"

            ],

            # -------------------------------------------------
            # FORECAST
            # -------------------------------------------------

            "forecast": [

                "forecast",
                "forecasts",
                "forecasting",
                "future sales",
                "future demand",
                "demand forecast",
                "demand prediction",
                "prediction",
                "predictions",
                "predict",
                "trend",
                "trends",
                "growth forecast",
                "expected sales",
                "expected demand",
                "sales forecast",
                "sales prediction",
                "forecast risk",
                "forecast risks"

            ],

            # -------------------------------------------------
            # CUSTOMER
            # -------------------------------------------------

            "customer": [

                "customer",
                "customers",
                "buyer",
                "buyers",
                "client",
                "clients",
                "segment",
                "segments",
                "segmentation",
                "retention",
                "loyalty",
                "churn",
                "customer churn",
                "customer value",
                "valuable customers",
                "top customers",
                "customer behavior",
                "customer performance",
                "most valuable customer",
                "most valuable customers"

            ],

            # -------------------------------------------------
            # RISK
            # -------------------------------------------------

            "risk": [

                "risk",
                "risks",
                "business risk",
                "business risks",
                "sales risk",
                "inventory risk",
                "forecast risk",
                "forecast risks",
                "financial risk",
                "loss",
                "losses",
                "danger",
                "threat",
                "threats",
                "problem",
                "problems",
                "issue",
                "issues",
                "declining",
                "decline",
                "warning",
                "warnings"

            ],

            # -------------------------------------------------
            # DECISION
            # -------------------------------------------------

            "decision": [

                "decision",
                "decisions",
                "strategy",
                "strategies",
                "recommend",
                "recommendation",
                "recommendations",
                "optimize",
                "optimization",
                "action",
                "actions",
                "what should we do",
                "what should we prioritize",
                "prioritize",
                "priority",
                "priorities",
                "improve",
                "improvement",
                "best action",
                "next action",
                "business decision",
                "business decisions",
                "management prioritize"

            ],

            # -------------------------------------------------
            # EXECUTIVE
            # -------------------------------------------------

            "executive": [

                "executive",
                "ceo",
                "management",
                "manager",
                "leadership",
                "board",
                "business overview",
                "company performance",
                "overall performance",
                "overall business",
                "enterprise performance",
                "enterprise overview",
                "quarter",
                "this quarter",
                "management prioritize",
                "executive summary"

            ]

        }

        logger.info(
            "Enterprise Planner initialized"
        )

    # =====================================================
    # NORMALIZE QUESTION
    # =====================================================

    def _normalize_question(
        self,
        question: str
    ):

        question = str(
            question or ""
        ).lower().strip()

        question = re.sub(
            r"\s+",
            " ",
            question
        )

        return question

    # =====================================================
    # FIND KEYWORD MATCHES
    # =====================================================

    def _find_matches(
        self,
        question: str
    ):

        matches = {}

        for agent, keywords in self.agent_keywords.items():

            hits = []

            for keyword in keywords:

                keyword = keyword.lower().strip()

                if not keyword:
                    continue

                # -----------------------------------------
                # Phrase matching
                # -----------------------------------------

                if " " in keyword:

                    if keyword in question:

                        hits.append(keyword)

                # -----------------------------------------
                # Single-word matching
                # -----------------------------------------

                else:

                    if re.search(
                        rf"\b{re.escape(keyword)}\b",
                        question
                    ):

                        hits.append(keyword)

            if hits:

                matches[agent] = list(
                    dict.fromkeys(hits)
                )

        return matches

    # =====================================================
    # DETERMINE PRIMARY INTENT
    # =====================================================

    def _determine_primary_intent(
        self,
        question: str,
        matches: dict
    ):

        # -------------------------------------------------
        # DECISION
        # -------------------------------------------------

        if any(
            phrase in question
            for phrase in [

                "what should we prioritize",
                "what should management prioritize",
                "what should we do",
                "what action should",
                "which action should",
                "recommend",
                "recommendation",
                "recommendations",
                "best action",
                "next action",
                "prioritize"

            ]
        ):

            return "DECISION"

        # -------------------------------------------------
        # INVENTORY
        # -------------------------------------------------

        if any(
            phrase in question
            for phrase in [

                "inventory risk",
                "inventory risks",
                "inventory shortage",
                "stock shortage",
                "reorder",
                "reorder point",
                "safety stock",
                "overstock",
                "understock",
                "out of stock"

            ]
        ):

            return "INVENTORY"

        # -------------------------------------------------
        # FORECAST
        # -------------------------------------------------

        if any(
            phrase in question
            for phrase in [

                "forecast risk",
                "forecast risks",
                "future demand",
                "future sales",
                "sales forecast",
                "demand forecast",
                "expected demand",
                "expected sales"

            ]
        ):

            return "FORECAST"

        # -------------------------------------------------
        # CUSTOMER
        # -------------------------------------------------

        if any(
            phrase in question
            for phrase in [

                "top customer",
                "top customers",
                "most valuable customer",
                "most valuable customers",
                "valuable customers",
                "customer value",
                "customer churn"

            ]
        ):

            return "CUSTOMER"

        # -------------------------------------------------
        # SALES
        # -------------------------------------------------

        if any(
            phrase in question
            for phrase in [

                "top product",
                "top products",
                "best product",
                "best products",
                "sales performance",
                "sales trend",
                "sales trends",
                "declining regions",
                "declining sales"

            ]
        ):

            return "SALES"

        # -------------------------------------------------
        # RISK
        # -------------------------------------------------

        if any(
            phrase in question
            for phrase in [

                "business risk",
                "business risks",
                "biggest risk",
                "biggest risks",
                "major risk",
                "major risks",
                "biggest business risks"

            ]
        ):

            return "RISK"

        # -------------------------------------------------
        # EXECUTIVE
        # -------------------------------------------------

        if any(
            phrase in question
            for phrase in [

                "executive summary",
                "business overview",
                "company performance",
                "overall business",
                "overall performance",
                "enterprise overview",
                "enterprise performance"

            ]
        ):

            return "EXECUTIVE"

        # -------------------------------------------------
        # SCORE MATCHES
        # -------------------------------------------------

        scores = {}

        for agent, hits in matches.items():

            scores[agent] = len(hits)

        if not scores:

            return "EXECUTIVE"

        # -------------------------------------------------
        # DECISION PRIORITY
        # -------------------------------------------------

        if (
            "decision" in scores
            and "risk" in scores
        ):

            return "DECISION"

        # -------------------------------------------------
        # MANAGEMENT / EXECUTIVE PRIORITY
        # -------------------------------------------------

        if "executive" in scores:

            if any(
                word in question
                for word in [

                    "management",
                    "ceo",
                    "leadership",
                    "board",
                    "quarter",
                    "executive"

                ]
            ):

                return "EXECUTIVE"

        # -------------------------------------------------
        # HIGHEST SCORE
        # -------------------------------------------------

        return max(
            scores,
            key=scores.get
        ).upper()

    # =====================================================
    # BUILD WORKFLOW
    #
    # IMPORTANT:
    # These names MUST match your LangGraph nodes.
    #
    # Current graph supports:
    # data
    # forecast
    # inventory
    # customer
    # decision
    # report
    # executive
    #
    # There is currently NO sales_node and NO risk_node.
    # =====================================================

    def _build_workflow(
        self,
        primary_intent: str
    ):

        # -------------------------------------------------
        # SALES
        #
        # Sales questions use existing report/data
        # infrastructure because there is currently no
        # dedicated sales LangGraph node.
        # -------------------------------------------------

        if primary_intent == "SALES":

            return [

                "data",
                "report",
                "executive"

            ]

        # -------------------------------------------------
        # INVENTORY
        # -------------------------------------------------

        if primary_intent == "INVENTORY":

            return [

                "data",
                "inventory"

            ]

        # -------------------------------------------------
        # FORECAST
        # -------------------------------------------------

        if primary_intent == "FORECAST":

            return [

                "data",
                "forecast"

            ]

        # -------------------------------------------------
        # CUSTOMER
        # -------------------------------------------------

        if primary_intent == "CUSTOMER":

            return [

                "data",
                "customer"

            ]

        # -------------------------------------------------
        # RISK
        #
        # Risk currently uses the available prediction
        # modules + decision engine.
        # -------------------------------------------------

        if primary_intent == "RISK":

            return [

                "data",
                "forecast",
                "inventory",
                "customer",
                "decision"

            ]

        # -------------------------------------------------
        # DECISION
        # -------------------------------------------------

        if primary_intent == "DECISION":

            return [

                "data",
                "forecast",
                "inventory",
                "customer",
                "decision"

            ]

        # -------------------------------------------------
        # EXECUTIVE
        # -------------------------------------------------

        if primary_intent == "EXECUTIVE":

            return [

                "data",
                "forecast",
                "inventory",
                "customer",
                "decision",
                "executive"

            ]

        # -------------------------------------------------
        # GENERAL
        # -------------------------------------------------

        return [

            "data",
            "report",
            "executive"

        ]

    # =====================================================
    # CREATE ENTERPRISE PLAN
    # =====================================================

    def create_plan(
        self,
        question: str
    ):

        question = self._normalize_question(
            question
        )

        # -------------------------------------------------
        # EMPTY QUESTION
        # -------------------------------------------------

        if not question:

            return {

                "status":
                    "error",

                "message":
                    "Question cannot be empty.",

                "question":
                    "",

                "intent":
                    "GENERAL",

                "workflow":
                    [],

                "reason":
                    {},

                "matched_agents":
                    [],

                "total_agents":
                    0,

                "confidence":
                    0.0

            }

        logger.info(
            "Creating enterprise plan for: %s",
            question
        )

        # -------------------------------------------------
        # FULL ENTERPRISE REQUEST
        # -------------------------------------------------

        full_business_request = any(

            phrase in question

            for phrase in [

                "all",
                "everything",
                "complete analysis",
                "complete business analysis",
                "full analysis",
                "full business analysis",
                "enterprise analysis",
                "entire business",
                "company overview",
                "business overview",
                "overall business"

            ]

        )

        if full_business_request:

            workflow = [

                "data",
                "forecast",
                "inventory",
                "customer",
                "decision",
                "executive"

            ]

            return {

                "status":
                    "success",

                "question":
                    question,

                "intent":
                    "EXECUTIVE",

                "workflow":
                    workflow,

                "reason": {

                    "workflow":
                        "Complete enterprise "
                        "business analysis requested."

                },

                "matched_agents": [

                    "forecast",
                    "inventory",
                    "customer",
                    "decision",
                    "executive"

                ],

                "total_agents":
                    len(workflow) - 1,

                "confidence":
                    1.0

            }

        # -------------------------------------------------
        # FIND MATCHES
        # -------------------------------------------------

        matches = self._find_matches(
            question
        )

        # -------------------------------------------------
        # PRIMARY INTENT
        # -------------------------------------------------

        primary_intent = (
            self._determine_primary_intent(
                question,
                matches
            )
        )

        # -------------------------------------------------
        # WORKFLOW
        # -------------------------------------------------

        workflow = self._build_workflow(
            primary_intent
        )

        # -------------------------------------------------
        # MATCHED AGENTS
        # -------------------------------------------------

        matched_agents = [

            agent

            for agent in [

                "sales",
                "inventory",
                "forecast",
                "customer",
                "risk",
                "decision",
                "executive"

            ]

            if agent in matches

        ]

        # -------------------------------------------------
        # REASONS
        # -------------------------------------------------

        reasons = {}

        for agent, hits in matches.items():

            reasons[agent] = hits

        # -------------------------------------------------
        # GENERAL QUESTION
        # -------------------------------------------------

        if not matches:

            primary_intent = "EXECUTIVE"

            workflow = [

                "data",
                "report",
                "executive"

            ]

            reasons["default"] = (
                "No specific business intent "
                "was detected. Using executive "
                "business analysis."
            )

            confidence = 0.70

        else:

            # -------------------------------------------------
            # CONFIDENCE
            # -------------------------------------------------

            total_hits = sum(

                len(hits)

                for hits in matches.values()

            )

            if total_hits >= 4:

                confidence = 0.95

            elif total_hits == 3:

                confidence = 0.93

            elif total_hits == 2:

                confidence = 0.90

            else:

                confidence = 0.85

        # -------------------------------------------------
        # FINAL PLAN
        # -------------------------------------------------

        plan = {

            "status":
                "success",

            "question":
                question,

            "intent":
                primary_intent,

            "workflow":
                workflow,

            "reason":
                reasons,

            "matched_agents":
                matched_agents,

            "total_agents":
                len(workflow) - 1,

            "confidence":
                confidence

        }

        logger.info(
            "Enterprise plan created: %s",
            plan
        )

        return plan

    # =====================================================
    # PLANNER HEALTH
    # =====================================================

    def health(self):

        return {

            "planner":
                "Enterprise Planner",

            "status":
                "healthy",

            "intents": [

                "SALES",
                "INVENTORY",
                "FORECAST",
                "CUSTOMER",
                "RISK",
                "DECISION",
                "EXECUTIVE"

            ],

            "agents":
                list(
                    self.agent_keywords.keys()
                )

        }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    planner = Planner()

    questions = [

        "What are our top products?",

        "Which regions are declining?",

        "Summarize current inventory risk.",

        "Which products need reorder?",

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

        result = planner.create_plan(
            question
        )

        print(
            "INTENT:",
            result.get("intent")
        )

        print(
            "WORKFLOW:",
            result.get("workflow")
        )

        print(
            "CONFIDENCE:",
            result.get("confidence")
        )

        print(
            "REASON:",
            result.get("reason")
        )

