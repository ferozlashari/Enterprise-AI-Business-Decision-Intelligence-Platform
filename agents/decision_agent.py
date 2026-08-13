
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform
Decision Intelligence Agent

Author : Feroz Ali

Responsibilities
----------------
1. Coordinate inventory intelligence.
2. Coordinate forecast intelligence.
3. Combine business intelligence signals.
4. Calculate deterministic business risk.
5. Generate executive AI recommendations.
6. Provide a stable agent interface.
7. Safely handle malformed or missing input.
8. Keep database persistence outside the agent.

Database persistence is handled by:
    backend.services.decision_service.DecisionService

IMPORTANT
---------
This agent is intentionally database-independent.
=========================================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, List

from agents.base_agent import BaseAgent
from agents.forecast_agent import ForecastAgent
from agents.inventory_agent import InventoryAgent

from backend.llm.groq_client import ask_llm


logger = logging.getLogger("DecisionAgent")


class DecisionAgent(BaseAgent):

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self) -> None:

        super().__init__("Decision Agent")

        self.forecast_agent = ForecastAgent()
        self.inventory_agent = InventoryAgent()

        logger.info(
            "DecisionAgent initialized successfully."
        )

    # =====================================================
    # SAFE HELPERS
    # =====================================================

    @staticmethod
    def _to_float(
        value: Any,
        default: float = 0.0,
    ) -> float:

        if value is None:
            return default

        if isinstance(value, bool):
            return 1.0 if value else 0.0

        try:

            if isinstance(value, str):
                value = (
                    value
                    .replace(",", "")
                    .replace("$", "")
                    .replace("%", "")
                    .strip()
                )

            result = float(value)

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
        ):

            return default

    @staticmethod
    def _to_int(
        value: Any,
        default: int = 0,
    ) -> int:

        try:
            return int(
                DecisionAgent._to_float(
                    value,
                    default,
                )
            )
        except Exception:
            return default

    @staticmethod
    def _clamp(
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:

        return max(
            minimum,
            min(
                maximum,
                value,
            ),
        )

    # =====================================================
    # INVENTORY INTELLIGENCE
    # =====================================================

    def inventory_decision(
        self,
    ) -> Dict[str, Any]:

        """
        Execute inventory intelligence.

        Database independent.
        """

        try:

            logger.info(
                "Running inventory health analysis."
            )

            health_result = (
                self.inventory_agent.execute(
                    {
                        "action": "health"
                    }
                )
            )

            logger.info(
                "Running inventory recommendation analysis."
            )

            recommendation_result = (
                self.inventory_agent.execute(
                    {
                        "action": "recommendation"
                    }
                )
            )

            return {

                "status": "success",

                "health": (
                    health_result
                ),

                "recommendations": (
                    recommendation_result
                ),

            }

        except Exception as exc:

            logger.exception(
                "Inventory decision failed."
            )

            return {

                "status": "error",

                "health": None,

                "recommendations": [],

                "message": (
                    "Inventory intelligence failed: "
                    f"{str(exc)}"
                ),

            }

    # =====================================================
    # FORECAST INTELLIGENCE
    # =====================================================

    def forecast_decision(
        self,
        model: Optional[str] = None,
        data: Any = None,
    ) -> Dict[str, Any]:

        """
        Execute forecast intelligence.
        """

        try:

            if not model:

                return {

                    "status": "error",

                    "message": (
                        "Forecast model was not provided."
                    ),

                }

            if data is None:

                return {

                    "status": "error",

                    "message": (
                        "Forecast data was not provided."
                    ),

                }

            logger.info(
                "Running forecast decision. model=%s",
                model,
            )

            result = (
                self.forecast_agent.execute(
                    {
                        "action": "forecast",

                        "model": model,

                        "data": data,
                    }
                )
            )

            if result is None:

                return {

                    "status": "error",

                    "message": (
                        "Forecast agent returned no result."
                    ),

                }

            if isinstance(
                result,
                dict,
            ):

                return result

            return {

                "status": "success",

                "forecast": result,

            }

        except Exception as exc:

            logger.exception(
                "Forecast decision failed."
            )

            return {

                "status": "error",

                "message": (
                    "Forecast intelligence failed: "
                    f"{str(exc)}"
                ),

            }

    # =====================================================
    # NORMALIZE BUSINESS INPUT
    # =====================================================

    def normalize_business_input(
        self,
        business_input: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:

        if not isinstance(
            business_input,
            dict,
        ):

            business_input = {}

        predicted_sales = max(
            0.0,
            self._to_float(
                business_input.get(
                    "predicted_sales",
                    business_input.get(
                        "predictedSales",
                        business_input.get(
                            "sales",
                            0,
                        ),
                    ),
                )
            ),
        )

        inventory = max(
            0.0,
            self._to_float(
                business_input.get(
                    "inventory",
                    business_input.get(
                        "inventory_units",
                        business_input.get(
                            "current_stock",
                            0,
                        ),
                    ),
                )
            ),
        )

        forecast_growth = self._clamp(
            self._to_float(
                business_input.get(
                    "forecast_growth",
                    business_input.get(
                        "forecastGrowth",
                        business_input.get(
                            "growth",
                            0,
                        ),
                    ),
                )
            ),
            -100,
            100,
        )

        customer_churn = self._clamp(
            self._to_float(
                business_input.get(
                    "customer_churn",
                    business_input.get(
                        "customerChurn",
                        business_input.get(
                            "churn",
                            0,
                        ),
                    ),
                )
            ),
            0,
            100,
        )

        revenue = max(
            0.0,
            self._to_float(
                business_input.get(
                    "revenue",
                    business_input.get(
                        "total_revenue",
                        0,
                    ),
                )
            ),
        )

        profit = self._to_float(
            business_input.get(
                "profit",
                business_input.get(
                    "total_profit",
                    business_input.get(
                        "net_profit",
                        0,
                    ),
                ),
            )
        )

        customers = max(
            0,
            self._to_int(
                business_input.get(
                    "customers",
                    business_input.get(
                        "customer_count",
                        business_input.get(
                            "total_customers",
                            0,
                        ),
                    ),
                )
            ),
        )

        profit_margin = self._to_float(
            business_input.get(
                "profit_margin",
                business_input.get(
                    "profitMargin",
                    0,
                ),
            )
        )

        # -------------------------------------------------
        # Calculate margin if it was not explicitly supplied
        # -------------------------------------------------

        if (
            profit_margin == 0
            and revenue > 0
        ):

            profit_margin = (
                profit / revenue
            ) * 100

        return {

            "predicted_sales": predicted_sales,

            "inventory": inventory,

            "forecast_growth": forecast_growth,

            "customer_churn": customer_churn,

            "revenue": revenue,

            "profit": profit,

            "profit_margin": profit_margin,

            "customers": customers,

        }

    # =====================================================
    # SALES HEALTH
    # =====================================================

    @staticmethod
    def calculate_sales_health(
        predicted_sales: float,
    ) -> int:

        """
        Normalize predicted sales to 0-100.

        This is intentionally conservative.
        """

        sales = max(
            0.0,
            predicted_sales,
        )

        if sales <= 0:
            return 0

        # Reference point for normalization.
        reference = 1_000_000.0

        import math

        score = (
            50
            + 20
            * math.log10(
                max(
                    1,
                    sales / reference,
                )
            )
        )

        return int(
            round(
                max(
                    0,
                    min(
                        100,
                        score,
                    ),
                )
            )
        )

    # =====================================================
    # INVENTORY HEALTH
    # =====================================================

    @staticmethod
    def calculate_inventory_health(
        inventory: float,
    ) -> int:

        """
        Inventory health.

        IMPORTANT:
        Inventory units alone should not automatically
        mean that inventory is healthy.

        Until demand/stock-ratio data is available,
        this function uses conservative thresholds.
        """

        stock = max(
            0.0,
            inventory,
        )

        if stock <= 0:
            return 0

        if stock < 25:
            return 15

        if stock < 50:
            return 35

        if stock < 100:
            return 55

        if stock < 250:
            return 70

        if stock < 500:
            return 85

        return 100

    # =====================================================
    # GROWTH HEALTH
    # =====================================================

    @staticmethod
    def calculate_growth_health(
        growth: float,
    ) -> int:

        growth = float(growth)

        if growth <= -20:
            return 0

        if growth < -10:

            return int(
                25
                + (
                    (growth + 20)
                    / 10
                )
                * 25
            )

        if growth < 0:

            return int(
                25
                + (
                    (growth + 10)
                    / 10
                )
                * 25
            )

        if growth < 10:

            return int(
                50
                + (
                    growth / 10
                )
                * 25
            )

        if growth < 20:

            return int(
                75
                + (
                    (growth - 10)
                    / 10
                )
                * 25
            )

        return 100

    # =====================================================
    # CHURN HEALTH
    # =====================================================

    @staticmethod
    def calculate_churn_health(
        churn: float,
    ) -> int:

        churn = max(
            0,
            min(
                100,
                churn,
            ),
        )

        # 0% churn = 100 health
        # 50% churn = 0 health
        score = 100 - (
            churn * 2
        )

        return int(
            max(
                0,
                min(
                    100,
                    score,
                ),
            )
        )

    # =====================================================
    # RISK ASSESSMENT
    # =====================================================

    def calculate_risk_assessment(
        self,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:

        """
        Deterministic business risk engine.

        Risk score:
            0   = no risk
            100 = maximum risk
        """

        predicted_sales = (
            self._to_float(
                metrics.get(
                    "predicted_sales"
                )
            )
        )

        inventory = (
            self._to_float(
                metrics.get(
                    "inventory"
                )
            )
        )

        growth = (
            self._to_float(
                metrics.get(
                    "forecast_growth"
                )
            )
        )

        churn = (
            self._to_float(
                metrics.get(
                    "customer_churn"
                )
            )
        )

        profit_margin = (
            self._to_float(
                metrics.get(
                    "profit_margin"
                )
            )
        )

        risks: List[str] = []
        risk_points = 0

        # =================================================
        # INVENTORY RISK
        # =================================================

        if inventory < 25:

            risks.append(
                "Critical inventory shortage risk"
            )

            risk_points += 30

        elif inventory < 50:

            risks.append(
                "Inventory shortage risk"
            )

            risk_points += 25

        elif inventory < 100:

            risks.append(
                "Low inventory buffer"
            )

            risk_points += 15

        # =================================================
        # CHURN RISK
        # =================================================

        if churn >= 50:

            risks.append(
                "Critical customer churn risk"
            )

            risk_points += 35

        elif churn >= 30:

            risks.append(
                "High customer churn"
            )

            risk_points += 25

        elif churn >= 15:

            risks.append(
                "Elevated customer churn"
            )

            risk_points += 15

        # =================================================
        # GROWTH RISK
        # =================================================

        if growth <= -10:

            risks.append(
                "Negative business growth"
            )

            risk_points += 25

        elif growth < 0:

            risks.append(
                "Business growth is slowing"
            )

            risk_points += 15

        # =================================================
        # PROFIT MARGIN RISK
        # =================================================

        if profit_margin < 0:

            risks.append(
                "Negative profit margin"
            )

            risk_points += 30

        elif profit_margin < 5:

            risks.append(
                "Low profit margin"
            )

            risk_points += 20

        elif profit_margin < 10:

            risks.append(
                "Profit margin requires monitoring"
            )

            risk_points += 10

        # =================================================
        # SALES RISK
        # =================================================

        if predicted_sales <= 0:

            risks.append(
                "Sales prediction unavailable"
            )

            risk_points += 15

        # =================================================
        # FINAL RISK SCORE
        # =================================================

        risk_score = int(
            self._clamp(
                risk_points,
                0,
                100,
            )
        )

        # =================================================
        # RISK LEVEL
        # =================================================

        if risk_score >= 75:

            risk_level = "CRITICAL"

        elif risk_score >= 50:

            risk_level = "HIGH"

        elif risk_score >= 25:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"

        # =================================================
        # SUMMARY
        # =================================================

        if risk_level == "CRITICAL":

            summary = (
                "Critical business risks require "
                "immediate management intervention."
            )

        elif risk_level == "HIGH":

            summary = (
                "Several business indicators require "
                "immediate attention."
            )

        elif risk_level == "MEDIUM":

            summary = (
                "Some business indicators require "
                "monitoring and corrective action."
            )

        else:

            summary = (
                "Business indicators are currently "
                "within an acceptable risk range."
            )

        return {

            "risk_level": risk_level,

            "risk_score": risk_score,

            "risk_count": len(risks),

            "identified_risks": risks,

            "summary": summary,

        }

    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    def generate_rule_based_recommendations(
        self,
        metrics: Dict[str, Any],
        risk: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        """
        Generate deterministic recommendations.

        These recommendations are always available,
        even when Groq is unavailable.
        """

        recommendations = []

        inventory = self._to_float(
            metrics.get("inventory")
        )

        growth = self._to_float(
            metrics.get("forecast_growth")
        )

        churn = self._to_float(
            metrics.get("customer_churn")
        )

        profit_margin = self._to_float(
            metrics.get("profit_margin")
        )

        # =================================================
        # INVENTORY
        # =================================================

        if inventory < 50:

            recommendations.append({

                "title": "Increase stock replenishment",

                "recommendation": (
                    "Increase replenishment priority "
                    "for low-stock inventory."
                ),

                "priority": "HIGH",

            })

        elif inventory < 100:

            recommendations.append({

                "title": "Monitor inventory levels",

                "recommendation": (
                    "Monitor inventory closely and "
                    "prepare replenishment before "
                    "stock reaches critical levels."
                ),

                "priority": "MEDIUM",

            })

        # =================================================
        # SALES
        # =================================================

        recommendations.append({

            "title": "Maintain current sales strategy",

            "recommendation": (
                "Continue monitoring sales performance "
                "while protecting high-performing "
                "products and channels."
            ),

            "priority": "MEDIUM",

        })

        # =================================================
        # GROWTH
        # =================================================

        if growth >= 10:

            recommendations.append({

                "title": "Scale successful growth initiatives",

                "recommendation": (
                    "Consider increasing investment in "
                    "successful growth initiatives."
                ),

                "priority": "HIGH",

            })

        elif growth < 0:

            recommendations.append({

                "title": "Address declining growth",

                "recommendation": (
                    "Review declining sales drivers, "
                    "pricing, demand and market performance."
                ),

                "priority": "HIGH",

            })

        # =================================================
        # CHURN
        # =================================================

        if churn >= 30:

            recommendations.append({

                "title": "Launch customer retention campaign",

                "recommendation": (
                    "Prioritize retention campaigns for "
                    "high-risk customer segments."
                ),

                "priority": "HIGH",

            })

        elif churn >= 15:

            recommendations.append({

                "title": "Strengthen customer retention",

                "recommendation": (
                    "Monitor churn drivers and introduce "
                    "targeted retention initiatives."
                ),

                "priority": "MEDIUM",

            })

        # =================================================
        # PROFIT
        # =================================================

        if profit_margin < 5:

            recommendations.append({

                "title": "Review costs and profitability",

                "recommendation": (
                    "Review costs, pricing and product "
                    "profitability to improve margins."
                ),

                "priority": "HIGH",

            })

        return recommendations

    # =====================================================
    # LLM EXECUTIVE ANALYSIS
    # =====================================================

    def generate_ai_recommendation(
        self,
        decisions: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        """
        Generate executive analysis using Groq.

        LLM failure never breaks the decision engine.
        """

        if not isinstance(
            decisions,
            dict,
        ):

            decisions = {}

        prompt = f"""
You are an Enterprise Decision Intelligence AI.

Analyze the following enterprise business intelligence.

BUSINESS INTELLIGENCE DATA:

{decisions}

Generate a concise professional executive analysis.

Cover:

1. Current business risks
2. Growth opportunities
3. Inventory actions
4. Sales strategy
5. Expected business impact

Requirements:

- Use only the information provided.
- Do not invent numerical business metrics.
- Prioritize the most important risks.
- Provide practical management actions.
- Keep the response concise.
- Use clear headings.
- Do not mention that you are an AI.
"""

        try:

            logger.info(
                "Generating executive recommendation using Groq."
            )

            response = ask_llm(
                prompt
            )

            if response is None:

                return {

                    "status": "fallback",

                    "message": (
                        "LLM returned no response. "
                        "Rule-based analysis remains available."
                    ),

                }

            if isinstance(
                response,
                str,
            ):

                cleaned = response.strip()

                if not cleaned:

                    return {

                        "status": "fallback",

                        "message": (
                            "LLM returned an empty response."
                        ),

                    }

                return {

                    "status": "success",

                    "analysis": cleaned,

                }

            if isinstance(
                response,
                dict,
            ):

                return {

                    "status": response.get(
                        "status",
                        "success",
                    ),

                    "analysis": response.get(
                        "analysis",
                        response.get(
                            "message",
                            str(response),
                        ),
                    ),

                }

            return {

                "status": "success",

                "analysis": str(
                    response
                ),

            }

        except Exception as exc:

            logger.exception(
                "LLM executive analysis failed."
            )

            return {

                "status": "fallback",

                "message": (
                    "LLM unavailable. "
                    "Rule-based business analysis remains available."
                ),

            }

    # =====================================================
    # COMPLETE BUSINESS DECISION
    # =====================================================

    def business_decision(
        self,
        model_name: Optional[str] = None,
        forecast_data: Any = None,
        business_input: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Dict[str, Any]:

        """
        Complete Decision Intelligence workflow.

        Workflow:

            Business Input
                 |
                 +---- Inventory
                 |
                 +---- Forecast
                 |
                 +---- Risk Engine
                 |
                 +---- Recommendations
                 |
                 +---- Groq Executive Analysis
                 |
                 v
            Final Decision

        No database operations occur here.
        """

        logger.info(
            "Starting complete business decision workflow."
        )

        # =================================================
        # NORMALIZE INPUT
        # =================================================

        metrics = (
            self.normalize_business_input(
                business_input
            )
        )

        # =================================================
        # INVENTORY
        # =================================================

        inventory_result = (
            self.inventory_decision()
        )

        # =================================================
        # FORECAST
        # =================================================

        if (
            model_name
            and forecast_data is not None
        ):

            forecast_result = (
                self.forecast_decision(
                    model=model_name,
                    data=forecast_data,
                )
            )

        else:

            forecast_result = {

                "status": "skipped",

                "message": (
                    "Forecast analysis was skipped "
                    "because model or forecast data "
                    "was not provided."
                ),

            }

        # =================================================
        # HEALTH
        # =================================================

        sales_health = (
            self.calculate_sales_health(
                metrics[
                    "predicted_sales"
                ]
            )
        )

        inventory_health = (
            self.calculate_inventory_health(
                metrics[
                    "inventory"
                ]
            )
        )

        growth_health = (
            self.calculate_growth_health(
                metrics[
                    "forecast_growth"
                ]
            )
        )

        churn_health = (
            self.calculate_churn_health(
                metrics[
                    "customer_churn"
                ]
            )
        )

        overall_health = int(
            round(
                (
                    sales_health
                    + inventory_health
                    + growth_health
                    + churn_health
                )
                / 4
            )
        )

        # =================================================
        # ADD HEALTH TO METRICS
        # =================================================

        metrics.update({

            "sales_health":
                sales_health,

            "inventory_health":
                inventory_health,

            "growth_health":
                growth_health,

            "churn_health":
                churn_health,

            "overall_health":
                overall_health,

        })

        # =================================================
        # RISK
        # =================================================

        risk = (
            self.calculate_risk_assessment(
                metrics
            )
        )

        # =================================================
        # RULE-BASED RECOMMENDATIONS
        # =================================================

        recommendations = (
            self.generate_rule_based_recommendations(
                metrics,
                risk,
            )
        )

        # =================================================
        # PREPARE LLM DATA
        # =================================================

        ai_input = {

            "metrics": metrics,

            "risk": risk,

            "recommendations": recommendations,

            "inventory": inventory_result,

            "forecast": forecast_result,

        }

        # =================================================
        # EXECUTIVE ANALYSIS
        # =================================================

        executive_result = (
            self.generate_ai_recommendation(
                ai_input
            )
        )

        # =================================================
        # WORKFLOW STATUS
        # =================================================

        component_errors = []

        if (
            isinstance(
                inventory_result,
                dict,
            )
            and inventory_result.get(
                "status"
            ) == "error"
        ):

            component_errors.append(
                "inventory"
            )

        if (
            isinstance(
                forecast_result,
                dict,
            )
            and forecast_result.get(
                "status"
            ) == "error"
        ):

            component_errors.append(
                "forecast"
            )

        status = (
            "partial"
            if component_errors
            else "success"
        )

        # =================================================
        # FINAL RESPONSE
        # =================================================

        decision = {

            "status": status,

            "agent": "Decision Agent",

            "metrics": metrics,

            "risk_level":
                risk[
                    "risk_level"
                ],

            "risk_score":
                risk[
                    "risk_score"
                ],

            "risk_count":
                risk[
                    "risk_count"
                ],

            "identified_risks":
                risk[
                    "identified_risks"
                ],

            "recommendations":
                recommendations,

            "summary":
                risk[
                    "summary"
                ],

            "insights": [],

            "inventory":
                inventory_result,

            "forecast":
                forecast_result,

            "executive_recommendation":
                executive_result,

        }

        if component_errors:

            decision[
                "component_errors"
            ] = component_errors

        logger.info(
            "Business decision workflow completed. "
            "status=%s risk=%s score=%s",
            status,
            decision["risk_level"],
            decision["risk_score"],
        )

        return decision

    # =====================================================
    # AGENT INTERFACE
    # =====================================================

    def execute(
        self,
        task: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Dict[str, Any]:

        """
        Standard BaseAgent interface.

        Supported actions:

            decision
            business_decision
            inventory
            inventory_decision
            forecast
            forecast_decision
            recommendation
            executive_recommendation
            health
        """

        # =================================================
        # VALIDATE TASK
        # =================================================

        if task is None:

            task = {}

        if not isinstance(
            task,
            dict,
        ):

            return {

                "status": "error",

                "message": (
                    "Decision Agent task must "
                    "be a dictionary."
                ),

            }

        # =================================================
        # ACTION
        # =================================================

        action = str(
            task.get(
                "action",
                "",
            )
        ).strip().lower()

        # =================================================
        # COMPLETE DECISION
        # =================================================

        if action in {
            "decision",
            "business_decision",
        }:

            return self.business_decision(

                model_name=(
                    task.get(
                        "model"
                    )
                ),

                forecast_data=(
                    task.get(
                        "data"
                    )
                ),

                business_input=(
                    task.get(
                        "business_input",
                        {},
                    )
                ),

            )

        # =================================================
        # INVENTORY
        # =================================================

        if action in {
            "inventory",
            "inventory_decision",
        }:

            return (
                self.inventory_decision()
            )

        # =================================================
        # FORECAST
        # =================================================

        if action in {
            "forecast",
            "forecast_decision",
        }:

            return self.forecast_decision(

                model=(
                    task.get(
                        "model"
                    )
                ),

                data=(
                    task.get(
                        "data"
                    )
                ),

            )

        # =================================================
        # RECOMMENDATION
        # =================================================

        if action in {
            "recommendation",
            "recommendations",
            "executive_recommendation",
        }:

            business_data = task.get(
                "business_input",
                task.get(
                    "data",
                    {},
                ),
            )

            if not isinstance(
                business_data,
                dict,
            ):

                business_data = {}

            return (
                self.generate_ai_recommendation(
                    business_data
                )
            )

        # =================================================
        # HEALTH
        # =================================================

        if action == "health":

            return {

                "status": "healthy",

                "agent": "Decision Agent",

                "components": {

                    "inventory_agent":
                        "available",

                    "forecast_agent":
                        "available",

                    "llm":
                        "configured",

                },

            }

        # =================================================
        # NO ACTION
        # =================================================

        if not action:

            return {

                "status": "error",

                "message": (
                    "Decision Agent action "
                    "was not provided."
                ),

                "supported_actions": [

                    "decision",

                    "business_decision",

                    "inventory",

                    "inventory_decision",

                    "forecast",

                    "forecast_decision",

                    "recommendation",

                    "executive_recommendation",

                    "health",

                ],

            }

        # =================================================
        # UNKNOWN ACTION
        # =================================================

        logger.warning(
            "Unknown Decision Agent action: %s",
            action,
        )

        return {

            "status": "error",

            "message": (
                f"Unknown decision action: {action}"
            ),

            "supported_actions": [

                "decision",

                "business_decision",

                "inventory",

                "inventory_decision",

                "forecast",

                "forecast_decision",

                "recommendation",

                "executive_recommendation",

                "health",

            ],

        }

