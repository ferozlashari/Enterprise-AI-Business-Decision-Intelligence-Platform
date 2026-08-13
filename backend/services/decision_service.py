
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Decision Intelligence Service

Author : Feroz Ali

Responsibilities
---------------------------------------------------------
1. Evaluate enterprise business metrics.
2. Calculate business risks.
3. Calculate business health scores.
4. Generate recommendations.
5. Persist decisions into Decision.
6. Persist decision snapshots into DecisionHistory.
7. Persist structured recommendations into Recommendation.
8. Return stable service responses for the API layer.
9. Provide latest/recommendation/health services.
10. Safely handle missing or malformed input.
11. Maintain transactional database integrity.
12. Prevent orphan DecisionHistory records.
13. Completely clear Decision Engine history.

Database Architecture
---------------------------------------------------------

Decision
    |
    +---- DecisionHistory
    |
    +---- Recommendation

The service is database-aware.

The Decision Engine logic remains database-independent.

=========================================================
"""

from __future__ import annotations

import json
import logging
import math
import uuid

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.database.models import (
    Decision,
    DecisionHistory,
    Recommendation,
)


logger = logging.getLogger("DecisionService")


class DecisionService:

    # =====================================================
    # CONFIGURATION
    # =====================================================

    # -----------------------------------------------------
    # Inventory configuration
    # -----------------------------------------------------

    INVENTORY_MINIMUM = 100
    INVENTORY_MAXIMUM = 10000

    # -----------------------------------------------------
    # Inventory demand ratios
    # -----------------------------------------------------

    INVENTORY_HIGH_RATIO = 0.10
    INVENTORY_CRITICAL_RATIO = 0.25

    # -----------------------------------------------------
    # Sales target
    # -----------------------------------------------------

    SALES_TARGET = 1_000_000

    # -----------------------------------------------------
    # Customer churn thresholds
    # -----------------------------------------------------

    HIGH_CHURN_THRESHOLD = 30.0
    ELEVATED_CHURN_THRESHOLD = 15.0

    # -----------------------------------------------------
    # Profit margin threshold
    # -----------------------------------------------------

    LOW_PROFIT_MARGIN_THRESHOLD = 10.0

    # -----------------------------------------------------
    # Growth thresholds
    # -----------------------------------------------------

    NEGATIVE_GROWTH_THRESHOLD = 0.0
    STRONG_GROWTH_THRESHOLD = 20.0

    # -----------------------------------------------------
    # Risk scores
    # -----------------------------------------------------

    RISK_SCORE_MAP = {
        "LOW": 0,
        "MEDIUM": 30,
        "HIGH": 65,
        "CRITICAL": 90,
    }

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        db: Session,
    ) -> None:

        if db is None:
            raise ValueError(
                "Database session is required."
            )

        self.db = db

        logger.info(
            "DecisionService initialized successfully."
        )

    # =====================================================
    # GENERATE DECISION
    # =====================================================

    def generate_decision(
        self,
        state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a business decision and persist it.

        Flow:

            API
              ↓
            state
              ↓
            make_decision()
              ↓
            _save_decision()
              ↓
            Decision
              ↓
            DecisionHistory
              ↓
            Recommendation
              ↓
            commit
        """

        try:

            if not isinstance(
                state,
                dict,
            ):
                state = {}

            logger.info(
                "Generating enterprise business decision."
            )

            decision = self.make_decision(
                state
            )

            record = self._save_decision(
                state,
                decision,
            )

            logger.info(
                "Decision generated successfully. "
                "Decision ID=%s",
                record.decision_id,
            )

            return {
                "status": "success",
                "module": "Decision Engine",
                "decision_id": record.decision_id,
                "decision": decision,
            }

        except Exception as exc:

            self._safe_rollback()

            logger.exception(
                "Decision generation failed."
            )

            return {
                "status": "error",
                "module": "Decision Engine",
                "decision_id": None,
                "decision": None,
                "message": str(exc),
            }

    # =====================================================
    # SAVE DECISION
    # =====================================================

    def _save_decision(
        self,
        state: Dict[str, Any],
        decision: Dict[str, Any],
    ) -> DecisionHistory:
        """
        Persist Decision, DecisionHistory and
        Recommendation records atomically.
        """

        if not isinstance(
            state,
            dict,
        ):
            state = {}

        if not isinstance(
            decision,
            dict,
        ):
            raise ValueError(
                "Decision result must be a dictionary."
            )

        metrics = decision.get(
            "metrics",
            {},
        )

        if not isinstance(
            metrics,
            dict,
        ):
            metrics = {}

        # -------------------------------------------------
        # Risk
        # -------------------------------------------------

        risk_level = str(
            decision.get(
                "risk_level",
                "LOW",
            )
            or "LOW"
        ).strip().upper()

        if risk_level not in self.RISK_SCORE_MAP:
            risk_level = "LOW"

        risk_score = self.to_float(
            decision.get(
                "risk_score",
                self.RISK_SCORE_MAP[risk_level],
            )
        )

        risk_score = max(
            0.0,
            min(
                100.0,
                risk_score,
            ),
        )

        # -------------------------------------------------
        # Lists
        # -------------------------------------------------

        identified_risks = self._normalize_list(
            decision.get(
                "identified_risks",
                [],
            )
        )

        recommendations = self._normalize_list(
            decision.get(
                "recommendations",
                [],
            )
        )

        insights = self._normalize_list(
            decision.get(
                "insights",
                [],
            )
        )

        risk_count = len(
            identified_risks
        )

        # -------------------------------------------------
        # Summary
        # -------------------------------------------------

        summary = str(
            decision.get(
                "summary",
                "",
            )
            or ""
        ).strip()

        # -------------------------------------------------
        # Health
        # -------------------------------------------------

        health_status = str(
            decision.get(
                "health_status",
                "Healthy",
            )
            or "Healthy"
        ).strip()

        if not health_status:
            health_status = "Healthy"

        business_health = decision.get(
            "business_health",
            {},
        )

        if not isinstance(
            business_health,
            dict,
        ):
            business_health = {}

        # -------------------------------------------------
        # Decision ID
        # -------------------------------------------------

        decision_id = (
            f"DEC-{uuid.uuid4().hex[:12].upper()}"
        )

        now = datetime.now(
            timezone.utc
        )

        try:

            # =================================================
            # DECISION
            # =================================================

            decision_record = Decision(
                decision_id=decision_id,
                decision_type="BUSINESS",
                title="Enterprise Business Decision",
                status="ACTIVE",
                risk_level=risk_level,
                risk_score=risk_score,
                summary=summary,
                decision=summary,
                identified_risks=self._serialize_list(
                    identified_risks
                ),
                recommendations=self._serialize_list(
                    recommendations
                ),
                insights=self._serialize_list(
                    insights
                ),
                input_data=self._safe_database_value(
                    state
                ),
                output_data=self._safe_database_value(
                    decision
                ),
                created_at=now,
                updated_at=now,
            )

            self.db.add(
                decision_record
            )

            # -------------------------------------------------
            # Flush parent before child records
            # -------------------------------------------------

            self.db.flush()

            # =================================================
            # DECISION HISTORY
            # =================================================

            history_record = DecisionHistory(
                decision_id=decision_id,
                created_at=now,
                risk_level=risk_level,
                risk_score=risk_score,
                risk_count=risk_count,

                predicted_sales=self.to_float(
                    metrics.get(
                        "predicted_sales",
                        0,
                    )
                ),

                inventory=self.to_float(
                    metrics.get(
                        "inventory",
                        0,
                    )
                ),

                forecast_growth=self.to_float(
                    metrics.get(
                        "forecast_growth",
                        0,
                    )
                ),

                customer_churn=self.to_float(
                    metrics.get(
                        "customer_churn",
                        0,
                    )
                ),

                revenue=self.to_float(
                    metrics.get(
                        "revenue",
                        0,
                    )
                ),

                profit=self.to_float(
                    metrics.get(
                        "profit",
                        0,
                    )
                ),

                profit_margin=self.to_float(
                    metrics.get(
                        "profit_margin",
                        0,
                    )
                ),

                customers=self.to_int(
                    metrics.get(
                        "customers",
                        0,
                    )
                ),

                identified_risks=self._serialize_list(
                    identified_risks
                ),

                recommendations=self._serialize_list(
                    recommendations
                ),

                insights=self._serialize_list(
                    insights
                ),

                summary=summary,

                health_status=health_status,

                business_health=self._safe_database_value(
                    business_health
                ),
            )

            self.db.add(
                history_record
            )

            # =================================================
            # STRUCTURED RECOMMENDATIONS
            # =================================================

            recommendation_priority = (
                self._recommendation_priority(
                    risk_level
                )
            )

            for recommendation_text in recommendations:

                recommendation_text = str(
                    recommendation_text
                ).strip()

                if not recommendation_text:
                    continue

                recommendation_record = Recommendation(
                    decision_id=decision_id,

                    title="Business Recommendation",

                    recommendation=recommendation_text,

                    priority=recommendation_priority,

                    category="BUSINESS",

                    expected_impact=(
                        "Improve business performance "
                        "and reduce identified operational risk."
                    ),

                    status="PENDING",

                    created_at=now,
                )

                self.db.add(
                    recommendation_record
                )

            # =================================================
            # COMMIT TRANSACTION
            # =================================================

            self.db.commit()

            # -------------------------------------------------
            # Refresh history record
            # -------------------------------------------------

            try:

                self.db.refresh(
                    history_record
                )

            except SQLAlchemyError:

                logger.warning(
                    "Unable to refresh DecisionHistory "
                    "after commit.",
                    exc_info=True,
                )

            logger.info(
                "Decision persisted successfully. "
                "decision_id=%s risks=%s recommendations=%s",
                decision_id,
                risk_count,
                len(recommendations),
            )

            return history_record

        except Exception:

            self._safe_rollback()

            logger.exception(
                "Failed to persist business decision."
            )

            raise

    # =====================================================
    # MAIN DECISION ENGINE
    # =====================================================

    def make_decision(
        self,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate enterprise business metrics.
        """

        if not isinstance(
            data,
            dict,
        ):
            data = {}

        recommendations: List[str] = []
        risks: List[str] = []
        insights: List[str] = []

        # =================================================
        # EXTRACT INPUTS
        # =================================================

        predicted_sales = self.to_float(
            self.first_value(
                data.get("predicted_sales"),
                data.get("predictedSales"),
                data.get("prediction"),
                data.get("sales_prediction"),
            )
        )

        inventory = self.to_float(
            self.first_value(
                data.get("inventory"),
                data.get("inventory_units"),
                data.get("inventory_count"),
                data.get("current_stock"),
            )
        )

        forecast_growth = self.to_float(
            self.first_value(
                data.get("forecast_growth"),
                data.get("forecastGrowth"),
                data.get("growth"),
            )
        )

        customer_churn = self.to_float(
            self.first_value(
                data.get("customer_churn"),
                data.get("customerChurn"),
                data.get("churn"),
                data.get("churn_rate"),
            )
        )

        revenue = self.to_float(
            self.first_value(
                data.get("revenue"),
                data.get("total_revenue"),
            )
        )

        profit = self.to_float(
            self.first_value(
                data.get("profit"),
                data.get("total_profit"),
                data.get("net_profit"),
            )
        )

        customers = self.to_int(
            self.first_value(
                data.get("customers"),
                data.get("customer_count"),
                data.get("total_customers"),
            )
        )

        # =================================================
        # OPTIONAL INVENTORY DEMAND
        # =================================================

        daily_demand = self.to_float(
            self.first_value(
                data.get("daily_demand"),
                data.get("dailyDemand"),
            )
        )

        monthly_demand = self.to_float(
            self.first_value(
                data.get("monthly_demand"),
                data.get("monthlyDemand"),
            )
        )

        annual_demand = self.to_float(
            self.first_value(
                data.get("annual_demand"),
                data.get("annualDemand"),
            )
        )

        inventory_turnover = self.to_float(
            self.first_value(
                data.get("inventory_turnover"),
                data.get("inventoryTurnover"),
            )
        )

        lead_time_days = self.to_float(
            self.first_value(
                data.get("lead_time_days"),
                data.get("leadTimeDays"),
            )
        )

        # =================================================
        # SANITIZE
        # =================================================

        predicted_sales = max(
            0.0,
            predicted_sales,
        )

        inventory = max(
            0.0,
            inventory,
        )

        forecast_growth = max(
            -100.0,
            min(
                100.0,
                forecast_growth,
            ),
        )

        customer_churn = max(
            0.0,
            min(
                100.0,
                customer_churn,
            ),
        )

        revenue = max(
            0.0,
            revenue,
        )

        customers = max(
            0,
            customers,
        )

        daily_demand = max(
            0.0,
            daily_demand,
        )

        monthly_demand = max(
            0.0,
            monthly_demand,
        )

        annual_demand = max(
            0.0,
            annual_demand,
        )

        inventory_turnover = max(
            0.0,
            inventory_turnover,
        )

        lead_time_days = max(
            0.0,
            lead_time_days,
        )

        # =================================================
        # DERIVE DAILY DEMAND
        # =================================================

        if daily_demand > 0:

            effective_daily_demand = daily_demand

        elif monthly_demand > 0:

            effective_daily_demand = (
                monthly_demand / 30.0
            )

        elif annual_demand > 0:

            effective_daily_demand = (
                annual_demand / 365.0
            )

        else:

            effective_daily_demand = 0.0

        # =================================================
        # PROFIT MARGIN
        # =================================================

        if revenue > 0:

            profit_margin = (
                profit / revenue
            ) * 100.0

        else:

            profit_margin = 0.0

        # =================================================
        # INVENTORY ANALYSIS
        # =================================================

        inventory_state = "healthy"

        inventory_coverage_days = None

        if effective_daily_demand > 0:

            inventory_coverage_days = (
                inventory
                / effective_daily_demand
            )

            # ---------------------------------------------
            # Lead-time shortage
            # ---------------------------------------------

            if (
                lead_time_days > 0
                and inventory_coverage_days < lead_time_days
            ):

                inventory_state = "shortage"

                risks.append(
                    "Inventory shortage risk"
                )

                recommendations.append(
                    "Increase stock replenishment "
                    "to cover supplier lead time"
                )

                insights.append(
                    "Available inventory may not cover "
                    "the expected supplier lead-time demand."
                )

            # ---------------------------------------------
            # Very low coverage
            # ---------------------------------------------

            elif inventory_coverage_days < 7:

                inventory_state = "low"

                risks.append(
                    "Low inventory coverage"
                )

                recommendations.append(
                    "Increase replenishment and monitor "
                    "near-term stock availability"
                )

                insights.append(
                    "Inventory coverage is below "
                    "approximately one week of demand."
                )

            # ---------------------------------------------
            # Excessive coverage
            # ---------------------------------------------

            elif inventory_coverage_days > 180:

                inventory_state = "excess"

                risks.append(
                    "Over inventory risk"
                )

                recommendations.append(
                    "Reduce purchasing and optimize "
                    "inventory levels"
                )

                insights.append(
                    "Inventory represents more than "
                    "approximately six months of estimated demand."
                )

            # ---------------------------------------------
            # High coverage
            # ---------------------------------------------

            elif inventory_coverage_days > 90:

                inventory_state = "high"

                risks.append(
                    "Elevated inventory level"
                )

                recommendations.append(
                    "Review purchasing frequency and "
                    "inventory turnover"
                )

                insights.append(
                    "Inventory coverage is relatively high "
                    "compared with estimated demand."
                )

            else:

                inventory_state = "healthy"

                recommendations.append(
                    "Maintain inventory within the "
                    "current demand-based operating range"
                )

                insights.append(
                    "Inventory coverage is currently "
                    "aligned with estimated demand."
                )

        else:

            # ---------------------------------------------
            # No demand information
            # ---------------------------------------------

            if inventory <= 0:

                inventory_state = "shortage"

                risks.append(
                    "Inventory shortage risk"
                )

                recommendations.append(
                    "Increase stock replenishment immediately"
                )

                insights.append(
                    "Inventory is unavailable or "
                    "below the minimum operating level."
                )

            elif inventory < self.INVENTORY_MINIMUM:

                inventory_state = "low"

                risks.append(
                    "Inventory shortage risk"
                )

                recommendations.append(
                    "Increase stock replenishment"
                )

                insights.append(
                    "Inventory is below the configured "
                    "minimum operating level."
                )

            elif inventory > self.INVENTORY_MAXIMUM:

                inventory_state = "excess"

                risks.append(
                    "Over inventory risk"
                )

                recommendations.append(
                    "Review inventory demand before reducing stock"
                )

                insights.append(
                    "Inventory is above the configured fallback "
                    "operating range, but demand data was not "
                    "available for a more precise assessment."
                )

            else:

                inventory_state = "healthy"

                recommendations.append(
                    "Inventory level is healthy"
                )

                insights.append(
                    "Inventory is currently within the "
                    "configured operating range."
                )

        # =================================================
        # SALES ANALYSIS
        # =================================================

        if predicted_sales <= 0:

            risks.append(
                "Sales prediction unavailable"
            )

            recommendations.append(
                "Review sales forecasting pipeline"
            )

            insights.append(
                "The decision engine did not receive "
                "a valid positive sales prediction."
            )

        elif predicted_sales < self.SALES_TARGET:

            risks.append(
                "Low sales prediction"
            )

            recommendations.append(
                "Improve marketing campaigns and "
                "sales conversion"
            )

            insights.append(
                "Predicted sales are below "
                "the configured business target."
            )

        else:

            recommendations.append(
                "Maintain current sales strategy"
            )

            insights.append(
                "Predicted sales are above "
                "the configured business target."
            )

        # =================================================
        # FORECAST ANALYSIS
        # =================================================

        if forecast_growth < self.NEGATIVE_GROWTH_THRESHOLD:

            risks.append(
                "Negative growth forecast"
            )

            recommendations.append(
                "Review pricing, demand generation, "
                "and sales strategy"
            )

            insights.append(
                "The forecast indicates potential "
                "decline in future business performance."
            )

        elif forecast_growth == 0:

            recommendations.append(
                "Monitor flat forecast performance"
            )

            insights.append(
                "The forecast indicates stable "
                "but limited growth."
            )

        elif forecast_growth >= self.STRONG_GROWTH_THRESHOLD:

            recommendations.append(
                "Consider scaling successful "
                "growth initiatives"
            )

            insights.append(
                "The forecast indicates strong "
                "positive business growth."
            )

        else:

            insights.append(
                "The forecast indicates positive "
                "business growth."
            )

        # =================================================
        # CUSTOMER CHURN ANALYSIS
        # =================================================

        if customer_churn > self.HIGH_CHURN_THRESHOLD:

            risks.append(
                "High customer churn"
            )

            recommendations.append(
                "Launch customer retention campaign"
            )

            insights.append(
                "Customer churn is above "
                "the high-risk threshold."
            )

        elif customer_churn > self.ELEVATED_CHURN_THRESHOLD:

            risks.append(
                "Elevated customer churn"
            )

            recommendations.append(
                "Increase customer engagement "
                "and retention monitoring"
            )

            insights.append(
                "Customer churn requires "
                "proactive monitoring."
            )

        else:

            insights.append(
                "Customer churn is currently "
                "within an acceptable range."
            )

        # =================================================
        # PROFITABILITY ANALYSIS
        # =================================================

        if revenue > 0 and profit < 0:

            risks.append(
                "Negative profitability"
            )

            recommendations.append(
                "Review operating costs "
                "and pricing strategy"
            )

            insights.append(
                "The business is generating revenue "
                "but reporting negative profit."
            )

        elif (
            revenue > 0
            and profit_margin
            < self.LOW_PROFIT_MARGIN_THRESHOLD
        ):

            risks.append(
                "Low profit margin"
            )

            recommendations.append(
                "Review costs, pricing, "
                "and product profitability"
            )

            insights.append(
                "Profit margin is below "
                "the recommended operating level."
            )

        elif (
            revenue > 0
            and profit_margin
            >= self.LOW_PROFIT_MARGIN_THRESHOLD
        ):

            insights.append(
                "Profit margin is within "
                "the recommended operating range."
            )

        # =================================================
        # CUSTOMER BASE
        # =================================================

        if customers > 0:

            insights.append(
                "Current customer base contains "
                f"approximately {customers:,} customers."
            )

        # =================================================
        # INVENTORY COVERAGE
        # =================================================

        if inventory_coverage_days is not None:

            insights.append(
                "Estimated inventory coverage is "
                f"{inventory_coverage_days:.1f} days."
            )

        # =================================================
        # INVENTORY TURNOVER
        # =================================================

        if inventory_turnover > 0:

            if inventory_turnover < 2:

                insights.append(
                    "Inventory turnover is relatively low "
                    "and should be monitored."
                )

            elif inventory_turnover >= 6:

                insights.append(
                    "Inventory turnover indicates "
                    "strong stock movement."
                )

        # =================================================
        # REMOVE DUPLICATES
        # =================================================

        unique_risks = list(
            dict.fromkeys(
                risks
            )
        )

        unique_recommendations = list(
            dict.fromkeys(
                recommendations
            )
        )

        unique_insights = list(
            dict.fromkeys(
                insights
            )
        )

        # =================================================
        # RISK
        # =================================================

        risk_count = len(
            unique_risks
        )

        risk_level = self.calculate_risk_level(
            unique_risks
        )

        risk_score = self.calculate_risk_score(
            unique_risks,
            risk_level,
        )

        # =================================================
        # BUSINESS HEALTH
        # =================================================

        sales_health = self.calculate_sales_health(
            predicted_sales
        )

        inventory_health = self.calculate_inventory_health(
            inventory=inventory,
            daily_demand=effective_daily_demand,
            inventory_state=inventory_state,
        )

        growth_health = self.calculate_growth_health(
            forecast_growth
        )

        churn_health = self.calculate_churn_health(
            customer_churn
        )

        profitability_health = (
            self.calculate_profit_health(
                profit_margin,
                revenue,
                profit,
            )
        )

        overall_health = round(
            (
                sales_health
                + inventory_health
                + growth_health
                + churn_health
                + profitability_health
            )
            / 5
        )

        overall_health = max(
            0,
            min(
                100,
                overall_health,
            ),
        )

        final_health_status = self.health_status(
            overall_health
        )

        # =================================================
        # SUMMARY
        # =================================================

        summary = self.build_summary(
            risk_level,
            risk_count,
        )

        # =================================================
        # TIMESTAMP
        # =================================================

        decision_timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        # =================================================
        # FINAL RESULT
        # =================================================

        return {
            "risk_level": risk_level,

            "risk_score": risk_score,

            "risk_count": risk_count,

            "identified_risks": unique_risks,

            "recommendations": unique_recommendations,

            "insights": unique_insights,

            "summary": summary,

            "health_status": final_health_status,

            "business_health": {
                "overall": overall_health,
                "sales": sales_health,
                "inventory": inventory_health,
                "growth": growth_health,
                "churn": churn_health,
                "profitability": profitability_health,
            },

            "metrics": {
                "predicted_sales": round(
                    predicted_sales,
                    2,
                ),

                "inventory": round(
                    inventory,
                    2,
                ),

                "forecast_growth": round(
                    forecast_growth,
                    2,
                ),

                "customer_churn": round(
                    customer_churn,
                    2,
                ),

                "revenue": round(
                    revenue,
                    2,
                ),

                "profit": round(
                    profit,
                    2,
                ),

                "profit_margin": round(
                    profit_margin,
                    2,
                ),

                "customers": customers,

                "daily_demand": round(
                    effective_daily_demand,
                    2,
                ),

                "inventory_coverage_days": (
                    round(
                        inventory_coverage_days,
                        2,
                    )
                    if inventory_coverage_days is not None
                    else None
                ),

                "inventory_turnover": round(
                    inventory_turnover,
                    2,
                ),

                "lead_time_days": round(
                    lead_time_days,
                    2,
                ),
            },

            "decision_timestamp": decision_timestamp,
        }

    # =====================================================
    # INVENTORY HEALTH
    # =====================================================

    def calculate_inventory_health(
        self,
        inventory: float,
        predicted_sales: float = 0.0,
        daily_demand: float = 0.0,
        inventory_state: str = "healthy",
    ) -> int:
        """
        Calculate inventory health.

        Demand-aware evaluation is used when daily demand
        is available.

        Otherwise configured inventory ranges are used.
        """

        inventory = max(
            0.0,
            self.to_float(inventory),
        )

        daily_demand = max(
            0.0,
            self.to_float(daily_demand),
        )

        state = str(
            inventory_state
            or "healthy"
        ).strip().lower()

        # =================================================
        # DEMAND-AWARE MODE
        # =================================================

        if daily_demand > 0:

            coverage_days = (
                inventory
                / daily_demand
            )

            if coverage_days < 3:
                return 20

            if coverage_days < 7:
                return 45

            if coverage_days < 30:
                return 85

            if coverage_days <= 90:
                return 100

            if coverage_days <= 180:
                return 80

            if coverage_days <= 365:
                return 55

            return 35

        # =================================================
        # STATE
        # =================================================

        if state == "shortage":
            return 20

        if state == "low":
            return 50

        if state == "excess":
            return 55

        if state == "high":
            return 75

        # =================================================
        # FALLBACK
        # =================================================

        if inventory <= 0:
            return 0

        if inventory < self.INVENTORY_MINIMUM:

            ratio = (
                inventory
                / self.INVENTORY_MINIMUM
            )

            return max(
                10,
                min(
                    60,
                    round(
                        ratio * 60
                    ),
                ),
            )

        if inventory <= self.INVENTORY_MAXIMUM:
            return 100

        excess_ratio = (
            inventory
            / self.INVENTORY_MAXIMUM
        )

        if excess_ratio <= 1.25:
            return 85

        if excess_ratio <= 1.50:
            return 70

        if excess_ratio <= 2.0:
            return 55

        return 35

    # =====================================================
    # RISK LEVEL
    # =====================================================

    @staticmethod
    def calculate_risk_level(
        risks: List[str],
    ) -> str:

        if not isinstance(
            risks,
            list,
        ):
            risks = []

        count = len(risks)

        if count == 0:
            return "LOW"

        if count == 1:
            return "MEDIUM"

        if count <= 3:
            return "HIGH"

        return "CRITICAL"

    # =====================================================
    # RISK SCORE
    # =====================================================

    def calculate_risk_score(
        self,
        risks: List[str],
        risk_level: str,
    ) -> int:

        if not isinstance(
            risks,
            list,
        ):
            risks = []

        risk_level = str(
            risk_level or "LOW"
        ).strip().upper()

        base_score = self.RISK_SCORE_MAP.get(
            risk_level,
            0,
        )

        if not risks:
            return 0

        severe_risks = {
            "Negative profitability",
            "High customer churn",
            "Inventory shortage risk",
            "Negative growth forecast",
        }

        moderate_risks = {
            "Low sales prediction",
            "Low profit margin",
            "Elevated customer churn",
            "Over inventory risk",
        }

        severe_count = sum(
            1
            for risk in risks
            if str(risk).strip() in severe_risks
        )

        moderate_count = sum(
            1
            for risk in risks
            if str(risk).strip() in moderate_risks
        )

        score = (
            base_score
            + (severe_count * 10)
            + (moderate_count * 5)
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
    # SALES HEALTH
    # =====================================================

    def calculate_sales_health(
        self,
        predicted_sales: float,
    ) -> int:

        predicted_sales = self.to_float(
            predicted_sales
        )

        if predicted_sales <= 0:
            return 0

        ratio = (
            predicted_sales
            / self.SALES_TARGET
        )

        if ratio >= 2.0:
            return 100

        if ratio >= 1.25:
            return 95

        if ratio >= 1.0:
            return 85

        if ratio >= 0.75:
            return 70

        if ratio >= 0.50:
            return 50

        if ratio >= 0.25:
            return 30

        return 15

    # =====================================================
    # GROWTH HEALTH
    # =====================================================

    @staticmethod
    def calculate_growth_health(
        growth: float,
    ) -> int:

        try:
            growth = float(growth)
        except (
            TypeError,
            ValueError,
        ):
            growth = 0.0

        if growth <= -20:
            return 0

        if growth < -10:

            return round(
                25
                + (
                    (growth + 20)
                    / 10
                )
                * 25
            )

        if growth < 0:

            return round(
                50
                + (
                    (growth + 10)
                    / 10
                )
                * 10
            )

        if growth < 10:

            return round(
                60
                + (
                    growth
                    / 10
                )
                * 20
            )

        if growth < 20:

            return round(
                80
                + (
                    (growth - 10)
                    / 10
                )
                * 20
            )

        return 100

    # =====================================================
    # CUSTOMER CHURN HEALTH
    # =====================================================

    @staticmethod
    def calculate_churn_health(
        churn: float,
    ) -> int:

        try:
            churn = float(churn)
        except (
            TypeError,
            ValueError,
        ):
            churn = 0.0

        churn = max(
            0.0,
            min(
                100.0,
                churn,
            ),
        )

        if churn <= 5:
            return 100

        if churn <= 10:
            return 80

        if churn <= 15:
            return 65

        if churn <= 30:
            return 40

        return 15

    # =====================================================
    # PROFITABILITY HEALTH
    # =====================================================

    @staticmethod
    def calculate_profit_health(
        profit_margin: float,
        revenue: float,
        profit: float,
    ) -> int:

        try:
            profit_margin = float(
                profit_margin
            )
        except (
            TypeError,
            ValueError,
        ):
            profit_margin = 0.0

        try:
            revenue = float(
                revenue
            )
        except (
            TypeError,
            ValueError,
        ):
            revenue = 0.0

        try:
            profit = float(
                profit
            )
        except (
            TypeError,
            ValueError,
        ):
            profit = 0.0

        if revenue <= 0:
            return 50

        if profit < 0:
            return 10

        if profit_margin < 5:
            return 35

        if profit_margin < 10:
            return 55

        if profit_margin < 20:
            return 80

        return 100

    # =====================================================
    # HEALTH STATUS
    # =====================================================

    @staticmethod
    def health_status(
        health: int,
    ) -> str:

        try:
            health = int(
                float(
                    health
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            health = 0

        health = max(
            0,
            min(
                100,
                health,
            ),
        )

        if health >= 80:
            return "Healthy"

        if health >= 60:
            return "Watch"

        if health >= 40:
            return "At Risk"

        return "Critical"

    # =====================================================
    # BUILD SUMMARY
    # =====================================================

    @staticmethod
    def build_summary(
        risk_level: str,
        risk_count: int,
    ) -> str:

        risk_level = str(
            risk_level or "LOW"
        ).upper()

        try:
            risk_count = int(
                risk_count
            )
        except (
            TypeError,
            ValueError,
        ):
            risk_count = 0

        if risk_level == "LOW":

            return (
                "Business conditions are currently "
                "stable with no major identified risks."
            )

        if risk_level == "MEDIUM":

            return (
                f"Business conditions require monitoring. "
                f"{risk_count} risk indicator(s) were identified."
            )

        if risk_level == "HIGH":

            return (
                f"Business conditions require management "
                f"attention. {risk_count} risk indicator(s) "
                f"were identified."
            )

        return (
            f"Business conditions are critical. "
            f"{risk_count} significant risk indicator(s) "
            f"were identified and immediate attention "
            f"is recommended."
        )

    # =====================================================
    # GET DECISION HISTORY
    # =====================================================

    def get_decisions(
        self,
    ) -> Dict[str, Any]:
        """
        Return valid DecisionHistory records.

        This service method exists for internal/admin use.

        The Decision API intentionally does not expose
        this endpoint.
        """

        try:

            logger.info(
                "Fetching Decision Engine history."
            )

            records = (
                self.db.query(
                    DecisionHistory
                )
                .join(
                    Decision,
                    Decision.decision_id
                    == DecisionHistory.decision_id,
                )
                .order_by(
                    DecisionHistory.created_at.desc()
                )
                .all()
            )

            history = []

            for record in records:

                try:

                    history.append(
                        self._record_to_dict(
                            record
                        )
                    )

                except Exception:

                    logger.exception(
                        "Failed to serialize DecisionHistory "
                        "record. decision_id=%s",
                        getattr(
                            record,
                            "decision_id",
                            None,
                        ),
                    )

                    continue

            return {
                "status": "success",
                "total_decisions": len(history),
                "history": history,
            }

        except SQLAlchemyError as exc:

            logger.exception(
                "Database error while retrieving "
                "Decision Engine history."
            )

            self._safe_rollback()

            return {
                "status": "error",
                "total_decisions": 0,
                "history": [],
                "message": (
                    "Unable to retrieve decision history."
                ),
                "error": str(exc),
            }

        except Exception as exc:

            logger.exception(
                "Unexpected error while retrieving "
                "Decision Engine history."
            )

            return {
                "status": "error",
                "total_decisions": 0,
                "history": [],
                "message": str(exc),
            }

    # =====================================================
    # GET RECOMMENDATIONS
    # =====================================================

    def get_recommendations(
        self,
    ) -> Dict[str, Any]:
        """
        Return structured business recommendations.

        Only recommendations whose parent Decision exists
        are returned.
        """

        try:

            logger.info(
                "Fetching Decision Engine recommendations."
            )

            records = (
                self.db.query(
                    Recommendation
                )
                .join(
                    Decision,
                    Decision.decision_id
                    == Recommendation.decision_id,
                )
                .filter(
                    Recommendation.status != "CANCELLED"
                )
                .order_by(
                    Recommendation.created_at.desc()
                )
                .all()
            )

            recommendations = []

            seen = set()

            for record in records:

                text = str(
                    getattr(
                        record,
                        "recommendation",
                        "",
                    )
                    or ""
                ).strip()

                if not text:
                    continue

                normalized = (
                    text
                    .casefold()
                    .strip()
                )

                if normalized in seen:
                    continue

                seen.add(
                    normalized
                )

                recommendations.append(
                    {
                        "id": getattr(
                            record,
                            "id",
                            None,
                        ),

                        "decision_id": getattr(
                            record,
                            "decision_id",
                            None,
                        ),

                        "title": (
                            getattr(
                                record,
                                "title",
                                None,
                            )
                            or "Business Recommendation"
                        ),

                        "recommendation": text,

                        "priority": (
                            getattr(
                                record,
                                "priority",
                                None,
                            )
                            or "LOW"
                        ),

                        "category": (
                            getattr(
                                record,
                                "category",
                                None,
                            )
                            or "BUSINESS"
                        ),

                        "expected_impact": (
                            getattr(
                                record,
                                "expected_impact",
                                None,
                            )
                            or (
                                "Improve business performance "
                                "and reduce identified "
                                "operational risk."
                            )
                        ),

                        "status": (
                            getattr(
                                record,
                                "status",
                                None,
                            )
                            or "PENDING"
                        ),

                        "created_at": self._timestamp(
                            getattr(
                                record,
                                "created_at",
                                None,
                            )
                        ),
                    }
                )

            return {
                "status": "success",
                "total_recommendations": len(
                    recommendations
                ),
                "recommendations": recommendations,
            }

        except SQLAlchemyError as exc:

            logger.exception(
                "Database error while retrieving "
                "recommendations."
            )

            self._safe_rollback()

            return {
                "status": "error",
                "total_recommendations": 0,
                "recommendations": [],
                "message": (
                    "Unable to retrieve recommendations."
                ),
                "error": str(exc),
            }

        except Exception as exc:

            logger.exception(
                "Unexpected error while retrieving "
                "recommendations."
            )

            return {
                "status": "error",
                "total_recommendations": 0,
                "recommendations": [],
                "message": str(exc),
            }

    # =====================================================
    # GET LATEST DECISION
    # =====================================================

    def get_latest_decision(
        self,
    ) -> Dict[str, Any]:
        """
        Return the latest valid decision.

        An INNER JOIN prevents orphan history records
        from becoming the latest decision.
        """

        try:

            logger.info(
                "Fetching latest Decision Engine decision."
            )

            latest = (
                self.db.query(
                    DecisionHistory
                )
                .join(
                    Decision,
                    Decision.decision_id
                    == DecisionHistory.decision_id,
                )
                .order_by(
                    DecisionHistory.created_at.desc()
                )
                .first()
            )

            if latest is None:

                return {
                    "status": "success",
                    "message": (
                        "No decisions generated yet."
                    ),
                    "decision": None,
                }

            try:

                decision = self._record_to_dict(
                    latest
                )

            except Exception as exc:

                logger.exception(
                    "Failed to serialize latest "
                    "DecisionHistory record."
                )

                return {
                    "status": "error",
                    "decision": None,
                    "message": (
                        "Latest decision could not "
                        "be processed."
                    ),
                    "error": str(exc),
                }

            return {
                "status": "success",
                "decision": decision,
            }

        except SQLAlchemyError as exc:

            logger.exception(
                "Database error while retrieving "
                "latest decision."
            )

            self._safe_rollback()

            return {
                "status": "error",
                "decision": None,
                "message": (
                    "Unable to retrieve latest decision."
                ),
                "error": str(exc),
            }

        except Exception as exc:

            logger.exception(
                "Unexpected error while retrieving "
                "latest decision."
            )

            return {
                "status": "error",
                "decision": None,
                "message": str(exc),
            }

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health(
        self,
    ) -> Dict[str, Any]:
        """
        Check whether the Decision Engine service and
        database are available.
        """

        try:

            # -------------------------------------------------
            # Simple database connectivity test
            # -------------------------------------------------

            self.db.query(
                Decision
            ).limit(1).first()

            return {
                "status": "healthy",
                "engine": (
                    "Enterprise Decision Intelligence"
                ),
                "database": "connected",
                "service": "DecisionService",
            }

        except SQLAlchemyError as exc:

            logger.exception(
                "Decision Engine database health check failed."
            )

            self._safe_rollback()

            return {
                "status": "unhealthy",
                "engine": (
                    "Enterprise Decision Intelligence"
                ),
                "database": "disconnected",
                "service": "DecisionService",
                "message": str(exc),
            }

        except Exception as exc:

            logger.exception(
                "Decision Engine health check failed."
            )

            return {
                "status": "unhealthy",
                "engine": (
                    "Enterprise Decision Intelligence"
                ),
                "database": "unknown",
                "service": "DecisionService",
                "message": str(exc),
            }

    # =====================================================
    # CLEAR COMPLETE DECISION HISTORY
    # =====================================================

    def clear_history(
        self,
    ) -> Dict[str, Any]:
        """
        Completely clear Decision Engine persistence.

        Deletion order:

            Recommendation
                    ↓
            DecisionHistory
                    ↓
            Decision

        The operation is transactional.
        """

        try:

            logger.warning(
                "Starting complete Decision Engine "
                "history cleanup."
            )

            decision_count = (
                self.db.query(
                    Decision
                ).count()
            )

            history_count = (
                self.db.query(
                    DecisionHistory
                ).count()
            )

            recommendation_count = (
                self.db.query(
                    Recommendation
                ).count()
            )

            logger.info(
                "Before cleanup: "
                "decisions=%s, history=%s, recommendations=%s",
                decision_count,
                history_count,
                recommendation_count,
            )

            # -------------------------------------------------
            # Delete recommendations first
            # -------------------------------------------------

            deleted_recommendations = (
                self.db.query(
                    Recommendation
                )
                .delete(
                    synchronize_session=False
                )
            )

            # -------------------------------------------------
            # Delete history
            # -------------------------------------------------

            deleted_history = (
                self.db.query(
                    DecisionHistory
                )
                .delete(
                    synchronize_session=False
                )
            )

            # -------------------------------------------------
            # Delete decisions
            # -------------------------------------------------

            deleted_decisions = (
                self.db.query(
                    Decision
                )
                .delete(
                    synchronize_session=False
                )
            )

            self.db.commit()

            # -------------------------------------------------
            # Verify
            # -------------------------------------------------

            remaining_decisions = (
                self.db.query(
                    Decision
                ).count()
            )

            remaining_history = (
                self.db.query(
                    DecisionHistory
                ).count()
            )

            remaining_recommendations = (
                self.db.query(
                    Recommendation
                ).count()
            )

            cleanup_successful = (
                remaining_decisions == 0
                and remaining_history == 0
                and remaining_recommendations == 0
            )

            if not cleanup_successful:

                logger.error(
                    "Decision Engine cleanup verification failed."
                )

                return {
                    "status": "error",
                    "message": (
                        "History cleanup did not completely "
                        "clear the Decision Engine tables."
                    ),
                    "deleted": {
                        "decisions": deleted_decisions,
                        "decision_history": deleted_history,
                        "recommendations": (
                            deleted_recommendations
                        ),
                    },
                    "remaining": {
                        "decisions": remaining_decisions,
                        "decision_history": remaining_history,
                        "recommendations": (
                            remaining_recommendations
                        ),
                    },
                }

            logger.info(
                "Decision Engine history cleanup completed."
            )

            return {
                "status": "success",

                "message": (
                    "Complete Decision Engine history "
                    "cleared successfully."
                ),

                "deleted": {
                    "decisions": deleted_decisions,
                    "decision_history": deleted_history,
                    "recommendations": (
                        deleted_recommendations
                    ),
                },

                "remaining": {
                    "decisions": remaining_decisions,
                    "decision_history": remaining_history,
                    "recommendations": (
                        remaining_recommendations
                    ),
                },
            }

        except SQLAlchemyError as exc:

            self._safe_rollback()

            logger.exception(
                "Database error while clearing "
                "Decision Engine history."
            )

            return {
                "status": "error",

                "message": (
                    "Database error while clearing "
                    "Decision Engine history."
                ),

                "error": str(exc),

                "deleted": {
                    "decisions": 0,
                    "decision_history": 0,
                    "recommendations": 0,
                },

                "remaining": {
                    "decisions": 0,
                    "decision_history": 0,
                    "recommendations": 0,
                },
            }

        except Exception as exc:

            self._safe_rollback()

            logger.exception(
                "Unexpected error while clearing "
                "Decision Engine history."
            )

            return {
                "status": "error",

                "message": str(exc),

                "deleted": {
                    "decisions": 0,
                    "decision_history": 0,
                    "recommendations": 0,
                },

                "remaining": {
                    "decisions": 0,
                    "decision_history": 0,
                    "recommendations": 0,
                },
            }

    # =====================================================
    # SERIALIZATION HELPERS
    # =====================================================

    @staticmethod
    def _normalize_list(
        value: Any,
    ) -> List[Any]:
        """
        Convert arbitrary input into a clean list.
        """

        if value is None:
            return []

        if isinstance(
            value,
            list,
        ):
            return [
                item
                for item in value
                if item is not None
            ]

        if isinstance(
            value,
            tuple,
        ):
            return list(value)

        if isinstance(
            value,
            set,
        ):
            return list(value)

        return [value]

    @staticmethod
    def _serialize_list(
        value: Any,
    ) -> Any:
        """
        Prepare list values for SQLAlchemy JSON/Text fields.

        If the database column accepts JSON objects/lists,
        returning the list directly is preferred.

        Otherwise this remains safely serializable.
        """

        normalized = (
            DecisionService._normalize_list(
                value
            )
        )

        return normalized

    @staticmethod
    def _safe_database_value(
        value: Any,
    ) -> Any:
        """
        Convert arbitrary values into database-safe
        JSON-compatible structures.
        """

        if value is None:
            return None

        if isinstance(
            value,
            (str, int, float, bool),
        ):
            return value

        if isinstance(
            value,
            datetime,
        ):
            return value.isoformat()

        if isinstance(
            value,
            dict,
        ):
            return {
                str(key): DecisionService._safe_database_value(
                    item
                )
                for key, item in value.items()
            }

        if isinstance(
            value,
            (list, tuple, set),
        ):
            return [
                DecisionService._safe_database_value(
                    item
                )
                for item in value
            ]

        try:

            if hasattr(
                value,
                "item",
            ):
                return value.item()

        except Exception:
            pass

        return str(value)

    @staticmethod
    def _timestamp(
        value: Any,
    ) -> Optional[str]:
        """
        Convert datetime values into ISO strings.
        """

        if value is None:
            return None

        if isinstance(
            value,
            datetime,
        ):
            return value.isoformat()

        return str(value)

    # =====================================================
    # HISTORY SERIALIZATION
    # =====================================================

    def _record_to_dict(
        self,
        record: DecisionHistory,
    ) -> Dict[str, Any]:
        """
        Convert DecisionHistory SQLAlchemy record into
        a frontend-safe dictionary.
        """

        if record is None:
            return {}

        return {
            "decision_id": getattr(
                record,
                "decision_id",
                None,
            ),

            "created_at": self._timestamp(
                getattr(
                    record,
                    "created_at",
                    None,
                )
            ),

            "risk_level": getattr(
                record,
                "risk_level",
                "LOW",
            ),

            "risk_score": self.to_float(
                getattr(
                    record,
                    "risk_score",
                    0,
                )
            ),

            "risk_count": self.to_int(
                getattr(
                    record,
                    "risk_count",
                    0,
                )
            ),

            "predicted_sales": self.to_float(
                getattr(
                    record,
                    "predicted_sales",
                    0,
                )
            ),

            "inventory": self.to_float(
                getattr(
                    record,
                    "inventory",
                    0,
                )
            ),

            "forecast_growth": self.to_float(
                getattr(
                    record,
                    "forecast_growth",
                    0,
                )
            ),

            "customer_churn": self.to_float(
                getattr(
                    record,
                    "customer_churn",
                    0,
                )
            ),

            "revenue": self.to_float(
                getattr(
                    record,
                    "revenue",
                    0,
                )
            ),

            "profit": self.to_float(
                getattr(
                    record,
                    "profit",
                    0,
                )
            ),

            "profit_margin": self.to_float(
                getattr(
                    record,
                    "profit_margin",
                    0,
                )
            ),

            "customers": self.to_int(
                getattr(
                    record,
                    "customers",
                    0,
                )
            ),

            "identified_risks": self._deserialize_value(
                getattr(
                    record,
                    "identified_risks",
                    [],
                )
            ),

            "recommendations": self._deserialize_value(
                getattr(
                    record,
                    "recommendations",
                    [],
                )
            ),

            "insights": self._deserialize_value(
                getattr(
                    record,
                    "insights",
                    [],
                )
            ),

            "summary": str(
                getattr(
                    record,
                    "summary",
                    "",
                )
                or ""
            ),

            "health_status": str(
                getattr(
                    record,
                    "health_status",
                    "Healthy",
                )
                or "Healthy"
            ),

            "business_health": self._deserialize_value(
                getattr(
                    record,
                    "business_health",
                    {},
                )
            ),
        }

    @staticmethod
    def _deserialize_value(
        value: Any,
    ) -> Any:
        """
        Safely deserialize JSON strings when database
        columns store JSON as text.
        """

        if value is None:
            return []

        if isinstance(
            value,
            (dict, list, tuple),
        ):
            return value

        if isinstance(
            value,
            str,
        ):

            stripped = value.strip()

            if not stripped:
                return []

            try:
                return json.loads(
                    stripped
                )

            except (
                json.JSONDecodeError,
                TypeError,
                ValueError,
            ):

                return value

        return value

    # =====================================================
    # VALUE HELPERS
    # =====================================================

    @staticmethod
    def first_value(
        *values: Any,
    ) -> Any:
        """
        Return the first meaningful value.

        Zero is considered a valid value.
        """

        for value in values:

            if value is None:
                continue

            if isinstance(
                value,
                str,
            ):

                if not value.strip():
                    continue

            return value

        return 0

    @staticmethod
    def to_float(
        value: Any,
        default: float = 0.0,
    ) -> float:
        """
        Safely convert a value to float.
        """

        try:

            if value is None:
                return default

            if isinstance(
                value,
                bool,
            ):
                return float(value)

            result = float(value)

            if not math.isfinite(
                result
            ):
                return default

            return result

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):

            return default

    @staticmethod
    def to_int(
        value: Any,
        default: int = 0,
    ) -> int:
        """
        Safely convert a value to integer.
        """

        try:

            if value is None:
                return default

            if isinstance(
                value,
                bool,
            ):
                return int(value)

            return int(
                float(value)
            )

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):

            return default

    # =====================================================
    # RECOMMENDATION PRIORITY
    # =====================================================

    @staticmethod
    def _recommendation_priority(
        risk_level: str,
    ) -> str:
        """
        Convert decision risk level into recommendation
        priority.
        """

        level = str(
            risk_level or "LOW"
        ).strip().upper()

        if level == "CRITICAL":
            return "CRITICAL"

        if level == "HIGH":
            return "HIGH"

        if level == "MEDIUM":
            return "MEDIUM"

        return "LOW"

    # =====================================================
    # DATABASE ROLLBACK
    # =====================================================

    def _safe_rollback(
        self,
    ) -> None:
        """
        Safely rollback the current SQLAlchemy transaction.
        """

        try:

            if self.db is not None:
                self.db.rollback()

        except Exception:

            logger.exception(
                "Database rollback failed."
            )

