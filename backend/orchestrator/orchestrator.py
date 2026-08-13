
"""
Enterprise AI Business Decision Intelligence Platform

Enterprise Orchestrator

Author : Feroz Ali
"""

import logging

from backend.orchestrator.planner import Planner
from backend.orchestrator.executor import Executor
from backend.orchestrator.response_builder import ResponseBuilder


logger = logging.getLogger("EnterpriseOrchestrator")


class EnterpriseOrchestrator:

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        self.planner = Planner()

        self.executor = Executor()

        self.builder = ResponseBuilder()

        logger.info(
            "Enterprise Orchestrator initialized"
        )

    # =====================================================
    # ENTERPRISE AI CHAT
    # =====================================================

    def chat(
        self,
        question: str
    ):

        try:

            # =================================================
            # VALIDATE QUESTION
            # =================================================

            if not question:

                return {
                    "status": "error",
                    "message": "Question cannot be empty."
                }

            question = str(question).strip()

            if not question:

                return {
                    "status": "error",
                    "message": "Question cannot be empty."
                }

            logger.info(
                "Enterprise question: %s",
                question
            )

            # =================================================
            # CREATE BUSINESS PLAN
            # =================================================

            plan = self.planner.create_plan(
                question
            )

            if not plan:

                return {
                    "status": "error",
                    "message": "Unable to create AI plan."
                }

            logger.info(
                "Enterprise plan: %s",
                plan
            )

            # =================================================
            # EXECUTE PLAN
            # =================================================

            execution = self.executor.execute(
                {
                    "plan": plan,
                    "question": question
                }
            )

            if execution is None:

                execution = {
                    "status": "error",
                    "message": (
                        "Enterprise execution "
                        "returned no result."
                    )
                }

            # =================================================
            # BUILD FINAL RESPONSE
            # =================================================

            response = self.builder.build(
                execution
            )

            # =================================================
            # FINAL ENTERPRISE RESULT
            # =================================================

            return {

                "status": "success",

                "question": question,

                "intent": plan.get(
                    "intent",
                    "GENERAL"
                ),

                "plan": plan,

                "execution": execution,

                "response": response

            }

        except Exception as error:

            logger.exception(
                "Enterprise Orchestrator failed"
            )

            return {

                "status": "error",

                "question": (
                    question
                    if question
                    else ""
                ),

                "message": str(error)

            }

    # =====================================================
    # HEALTH
    # =====================================================

    def health(self):

        try:

            planner_health = (
                self.planner.health()
            )

            return {

                "service":
                    "Enterprise Orchestrator",

                "status":
                    "healthy",

                "planner":
                    planner_health,

                "executor":
                    "available",

                "response_builder":
                    "available"

            }

        except Exception as error:

            logger.exception(
                "Orchestrator health check failed"
            )

            return {

                "service":
                    "Enterprise Orchestrator",

                "status":
                    "error",

                "message":
                    str(error)

            }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    orchestrator = EnterpriseOrchestrator()

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

        result = orchestrator.chat(
            question
        )

        print(result)

