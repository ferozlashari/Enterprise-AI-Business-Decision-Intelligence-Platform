
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Dashboard Service

Responsible for:
- Executive Dashboard
- KPI Aggregation
- Business Alerts
- Executive Insights
- Health Monitoring
- Dashboard Analytics
- Frontend Dashboard Data

Author : Feroz Ali
=========================================================
"""

from __future__ import annotations

import logging

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.cache.decorators import redis_cache
from backend.database.database import SessionLocal
from backend.database.models import Alert
from backend.services.report_service import ReportService


logger = logging.getLogger("DashboardService")


class DashboardService:

    # =====================================================
    # EXECUTIVE DASHBOARD
    # =====================================================

    @staticmethod
    @redis_cache(expire=300)
    def executive_dashboard(
        question: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Generate the complete executive dashboard.

        The response shape is intentionally stable so the
        React frontend can consume it safely.
        """

        try:

            logger.info(
                "Generating executive dashboard..."
            )

            if question:

                logger.info(
                    "Dashboard question: %s",
                    question,
                )

            # -------------------------------------------------
            # LOAD REPORTS
            # -------------------------------------------------

            sales = ReportService.sales_report()

            inventory = ReportService.inventory_report()

            customer = ReportService.customer_report()

            forecast = ReportService.forecast_report()

            executive = ReportService.executive_summary()

            # -------------------------------------------------
            # LOAD DATABASE ALERTS
            # -------------------------------------------------

            alerts = DashboardService.dashboard_alerts()

            # -------------------------------------------------
            # BUILD RESPONSE
            # -------------------------------------------------

            dashboard = (
                DashboardService.build_dashboard_response(
                    sales=sales,
                    inventory=inventory,
                    customer=customer,
                    forecast=forecast,
                    executive=executive,
                    alerts=alerts,
                )
            )

            return {
                "status": "success",
                "executive": dashboard,
                "generated_at":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
            }

        except Exception as exc:

            logger.exception(
                "Executive dashboard generation failed"
            )

            return {
                "status": "error",
                "message": str(exc),
                "executive":
                    DashboardService.empty_dashboard(),
                "generated_at":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
            }

    # =====================================================
    # EMPTY DASHBOARD
    # =====================================================

    @staticmethod
    def empty_dashboard() -> dict[str, Any]:
        """
        Stable empty dashboard structure.

        Every frontend-consumed field is always present.
        """

        return {

            # -------------------------------------------------
            # KPIs
            # -------------------------------------------------

            "revenue": 0.0,

            "profit": 0.0,

            "profit_margin": 0.0,

            "growth": 0.0,

            # -------------------------------------------------
            # INVENTORY
            # -------------------------------------------------

            "inventory": 0,

            "inventory_demand": 0.0,

            "inventory_status": "Unknown",

            "inventory_coverage": 0.0,

            # -------------------------------------------------
            # CUSTOMERS
            # -------------------------------------------------

            "customers": 0,

            "customer_segments_count": 0,

            # -------------------------------------------------
            # CHART DATA
            # -------------------------------------------------

            "sales_trend": [],

            "forecast": [],

            "inventory_data": [],

            "customer_segments": [],

            # -------------------------------------------------
            # AI
            # -------------------------------------------------

            "insights": [],

            "recommendations": [],

            # -------------------------------------------------
            # ALERTS
            # -------------------------------------------------

            "alerts": 0,

            "alert_items": [],

            # -------------------------------------------------
            # MODEL INFORMATION
            # -------------------------------------------------

            "model_status": "unknown",

            "sales_model": "Unknown",

            "forecast_model": "Unknown",

            "sales_r2": 0.0,

            "customer_silhouette": 0.0,

            # -------------------------------------------------
            # SYSTEM
            # -------------------------------------------------

            "status": "unknown",

        }

    # =====================================================
    # BUILD DASHBOARD RESPONSE
    # =====================================================

    @staticmethod
    def build_dashboard_response(
        sales: Any = None,
        inventory: Any = None,
        customer: Any = None,
        forecast: Any = None,
        executive: Any = None,
        alerts: Any = None,
    ) -> dict[str, Any]:
        """
        Merge all report sources into one stable dashboard
        response consumed by the frontend.
        """

        dashboard = (
            DashboardService.empty_dashboard()
        )

        # =================================================
        # SALES
        # =================================================

        if isinstance(sales, dict):

            revenue = DashboardService.first_value(
                sales,
                "revenue",
                "total_sales",
                "Total Sales",
                "Total Revenue",
                "Revenue",
                default=0,
            )

            profit = DashboardService.first_value(
                sales,
                "profit",
                "Total Profit",
                "Profit",
                "Estimated Profit",
                default=0,
            )

            profit_margin = DashboardService.first_value(
                sales,
                "profit_margin",
                "Profit Margin",
                "margin",
                default=0,
            )

            growth = DashboardService.first_value(
                sales,
                "growth",
                "Growth",
                "growth_rate",
                "Growth Rate",
                default=0,
            )

            dashboard["revenue"] = (
                DashboardService.to_float(
                    revenue
                )
            )

            dashboard["profit"] = (
                DashboardService.to_float(
                    profit
                )
            )

            dashboard["profit_margin"] = (
                DashboardService.to_float(
                    profit_margin
                )
            )

            dashboard["growth"] = (
                DashboardService.to_float(
                    growth
                )
            )

            # -------------------------------------------------
            # SALES TREND
            # -------------------------------------------------

            sales_trend = DashboardService.first_value(
                sales,
                "sales_trend",
                "Sales Trend",
                "trend",
                "monthly_sales",
                "monthly_revenue",
                "trend_data",
                default=[],
            )

            dashboard["sales_trend"] = (
                DashboardService.normalize_sales_trend(
                    sales_trend
                )
            )

            # -------------------------------------------------
            # SALES MODEL
            # -------------------------------------------------

            dashboard["sales_model"] = str(
                DashboardService.first_value(
                    sales,
                    "model",
                    "model_name",
                    "Model",
                    "Model Name",
                    default="Unknown",
                )
            )

            # -------------------------------------------------
            # SALES R2
            # -------------------------------------------------

            dashboard["sales_r2"] = (
                DashboardService.to_float(
                    DashboardService.first_value(
                        sales,
                        "r2_score",
                        "r2",
                        "R2",
                        "R2 Score",
                        default=0,
                    )
                )
            )

        # =================================================
        # SALES FALLBACK
        # =================================================

        if not dashboard["sales_trend"]:

            dashboard["sales_trend"] = [
                {
                    "month": "Total Sales",
                    "sales": dashboard["revenue"],
                }
            ]

        # =================================================
        # INVENTORY
        # =================================================

        if isinstance(inventory, dict):

            # -------------------------------------------------
            # Prefer actual inventory quantity.
            # -------------------------------------------------

            raw_inventory = DashboardService.first_value(
                inventory,
                "inventory_units",
                "inventory_quantity",
                "Inventory Quantity",
                "Inventory Units",
                "inventory",
                "Inventory",
                "inventory_count",
                default=0,
            )

            # -------------------------------------------------
            # INVENTORY TOTAL
            # -------------------------------------------------

            if isinstance(
                raw_inventory,
                list,
            ):

                inventory_count = 0.0

                for item in raw_inventory:

                    if not isinstance(
                        item,
                        dict,
                    ):
                        continue

                    quantity = DashboardService.first_value(
                        item,
                        "quantity",
                        "stock",
                        "inventory",
                        "Inventory",
                        "value",
                        default=0,
                    )

                    inventory_count += (
                        DashboardService.to_float(
                            quantity
                        )
                    )

            elif isinstance(
                raw_inventory,
                dict,
            ):

                inventory_count = 0.0

                for value in raw_inventory.values():

                    if isinstance(
                        value,
                        dict,
                    ):

                        quantity = (
                            DashboardService.first_value(
                                value,
                                "quantity",
                                "stock",
                                "inventory",
                                "value",
                                default=0,
                            )
                        )

                        inventory_count += (
                            DashboardService.to_float(
                                quantity
                            )
                        )

                    else:

                        inventory_count += (
                            DashboardService.to_float(
                                value
                            )
                        )

            else:

                inventory_count = (
                    DashboardService.to_float(
                        raw_inventory
                    )
                )

            dashboard["inventory"] = (
                DashboardService.to_int(
                    inventory_count
                )
            )

            # -------------------------------------------------
            # INVENTORY DEMAND
            # -------------------------------------------------

            demand = DashboardService.first_value(
                inventory,
                "demand",
                "Demand",
                "inventory_demand",
                "predicted_demand",
                "Predicted Demand",
                default=0,
            )

            dashboard["inventory_demand"] = (
                DashboardService.to_float(
                    demand
                )
            )

            # -------------------------------------------------
            # INVENTORY STATUS
            # -------------------------------------------------

            dashboard["inventory_status"] = str(
                DashboardService.first_value(
                    inventory,
                    "stock_status",
                    "inventory_status",
                    "status",
                    default="Balanced",
                )
            )

            # -------------------------------------------------
            # INVENTORY COVERAGE
            # -------------------------------------------------

            dashboard["inventory_coverage"] = (
                DashboardService.to_float(
                    DashboardService.first_value(
                        inventory,
                        "inventory_coverage",
                        "coverage",
                        default=0,
                    )
                )
            )

            # -------------------------------------------------
            # INVENTORY DATA
            # -------------------------------------------------

            inventory_data = DashboardService.first_value(
                inventory,
                "inventory_data",
                "Inventory Data",
                "items",
                "products",
                "products_data",
                "Products Data",
                default=[],
            )

            dashboard["inventory_data"] = (
                DashboardService.normalize_inventory(
                    inventory_data
                )
            )

        # =================================================
        # CUSTOMER
        # =================================================

        if isinstance(customer, dict):

            raw_customers = DashboardService.first_value(
                customer,
                "customers",
                "Customers",
                "customer_count",
                "total_customers",
                "Total Customers",
                default=0,
            )

            # -------------------------------------------------
            # If customers is a list, count it.
            # -------------------------------------------------

            if isinstance(
                raw_customers,
                list,
            ):

                dashboard["customers"] = len(
                    raw_customers
                )

            elif isinstance(
                raw_customers,
                dict,
            ):

                dashboard["customers"] = len(
                    raw_customers
                )

            else:

                dashboard["customers"] = (
                    DashboardService.to_int(
                        raw_customers
                    )
                )

            # -------------------------------------------------
            # CUSTOMER SEGMENTS
            # -------------------------------------------------

            customer_segments = (
                DashboardService.first_value(
                    customer,
                    "customer_segments",
                    default=None,
                )
            )

            if customer_segments is None:

                customer_segments = (
                    DashboardService.first_value(
                        customer,
                        "segments",
                        "Clusters",
                        "clusters",
                        "Segment Distribution",
                        "segment_distribution",
                        default=[],
                    )
                )

            dashboard["customer_segments"] = (
                DashboardService.normalize_customer_segments(
                    customer_segments
                )
            )

            dashboard["customer_segments_count"] = len(
                dashboard["customer_segments"]
            )

            # -------------------------------------------------
            # SILHOUETTE
            # -------------------------------------------------

            dashboard["customer_silhouette"] = (
                DashboardService.to_float(
                    DashboardService.first_value(
                        customer,
                        "silhouette_score",
                        "Silhouette Score",
                        "customer_silhouette",
                        default=0,
                    )
                )
            )

        # =================================================
        # FORECAST
        # =================================================

        if isinstance(forecast, dict):

            forecast_data = DashboardService.first_value(
                forecast,
                "forecast",
                "Forecast",
                "predictions",
                "prediction",
                "demand",
                "forecast_data",
                "forecast_values",
                default=[],
            )

            dashboard["forecast"] = (
                DashboardService.normalize_forecast(
                    forecast_data
                )
            )

            dashboard["forecast_model"] = str(
                DashboardService.first_value(
                    forecast,
                    "model",
                    "model_name",
                    "Model",
                    "Model Name",
                    default="Facebook Prophet",
                )
            )

        # =================================================
        # EXECUTIVE FALLBACK
        # =================================================

        if isinstance(executive, dict):

            # -------------------------------------------------
            # REVENUE
            # -------------------------------------------------

            if dashboard["revenue"] == 0:

                dashboard["revenue"] = (
                    DashboardService.to_float(
                        DashboardService.first_value(
                            executive,
                            "revenue",
                            "total_sales",
                            "Total Sales",
                            "Total Revenue",
                            default=0,
                        )
                    )
                )

            # -------------------------------------------------
            # PROFIT
            # -------------------------------------------------

            if dashboard["profit"] == 0:

                dashboard["profit"] = (
                    DashboardService.to_float(
                        DashboardService.first_value(
                            executive,
                            "profit",
                            "Total Profit",
                            default=0,
                        )
                    )
                )

            # -------------------------------------------------
            # PROFIT MARGIN
            # -------------------------------------------------

            if dashboard["profit_margin"] == 0:

                dashboard["profit_margin"] = (
                    DashboardService.to_float(
                        DashboardService.first_value(
                            executive,
                            "profit_margin",
                            "Profit Margin",
                            default=0,
                        )
                    )
                )

            # -------------------------------------------------
            # GROWTH
            # -------------------------------------------------

            if dashboard["growth"] == 0:

                dashboard["growth"] = (
                    DashboardService.to_float(
                        DashboardService.first_value(
                            executive,
                            "growth",
                            "growth_rate",
                            "Growth",
                            "Growth Rate",
                            default=0,
                        )
                    )
                )

            # -------------------------------------------------
            # INVENTORY
            # -------------------------------------------------

            if dashboard["inventory"] == 0:

                dashboard["inventory"] = (
                    DashboardService.to_int(
                        DashboardService.first_value(
                            executive,
                            "inventory",
                            "inventory_units",
                            "inventory_quantity",
                            default=0,
                        )
                    )
                )

            # -------------------------------------------------
            # CUSTOMERS
            # -------------------------------------------------

            if dashboard["customers"] == 0:

                dashboard["customers"] = (
                    DashboardService.to_int(
                        DashboardService.first_value(
                            executive,
                            "customers",
                            "total_customers",
                            default=0,
                        )
                    )
                )

            # -------------------------------------------------
            # INVENTORY DEMAND FALLBACK
            # -------------------------------------------------

            if dashboard["inventory_demand"] == 0:

                dashboard["inventory_demand"] = (
                    DashboardService.to_float(
                        DashboardService.first_value(
                            executive,
                            "inventory_demand",
                            "demand",
                            "predicted_demand",
                            default=0,
                        )
                    )
                )

            # -------------------------------------------------
            # INSIGHTS
            # -------------------------------------------------

            insights = executive.get(
                "insights",
                [],
            )

            dashboard["insights"] = (
                insights
                if isinstance(
                    insights,
                    list,
                )
                else []
            )

            # -------------------------------------------------
            # RECOMMENDATIONS
            # -------------------------------------------------

            recommendations = executive.get(
                "recommendations",
                [],
            )

            dashboard["recommendations"] = (
                recommendations
                if isinstance(
                    recommendations,
                    list,
                )
                else []
            )

            # -------------------------------------------------
            # MODEL STATUS
            # -------------------------------------------------

            dashboard["model_status"] = str(
                DashboardService.first_value(
                    executive,
                    "model_status",
                    "status",
                    default="healthy",
                )
            )

        # =================================================
        # ALERTS
        # =================================================

        if isinstance(
            alerts,
            dict,
        ):

            dashboard["alerts"] = (
                DashboardService.to_int(
                    alerts.get(
                        "count",
                        0,
                    )
                )
            )

            raw_alerts = alerts.get(
                "alerts",
                [],
            )

            dashboard["alert_items"] = (
                raw_alerts
                if isinstance(
                    raw_alerts,
                    list,
                )
                else []
            )

        # =================================================
        # FINAL SANITIZATION
        # =================================================

        dashboard["revenue"] = round(
            DashboardService.to_float(
                dashboard["revenue"]
            ),
            2,
        )

        dashboard["profit"] = round(
            DashboardService.to_float(
                dashboard["profit"]
            ),
            2,
        )

        dashboard["profit_margin"] = round(
            DashboardService.to_float(
                dashboard["profit_margin"]
            ),
            2,
        )

        dashboard["growth"] = round(
            DashboardService.to_float(
                dashboard["growth"]
            ),
            2,
        )

        dashboard["inventory_demand"] = round(
            DashboardService.to_float(
                dashboard["inventory_demand"]
            ),
            2,
        )

        dashboard["inventory_coverage"] = round(
            DashboardService.to_float(
                dashboard["inventory_coverage"]
            ),
            4,
        )

        dashboard["inventory"] = (
            DashboardService.to_int(
                dashboard["inventory"]
            )
        )

        dashboard["customers"] = (
            DashboardService.to_int(
                dashboard["customers"]
            )
        )

        dashboard["alerts"] = (
            DashboardService.to_int(
                dashboard["alerts"]
            )
        )

        dashboard["sales_r2"] = round(
            DashboardService.to_float(
                dashboard["sales_r2"]
            ),
            4,
        )

        dashboard["customer_silhouette"] = round(
            DashboardService.to_float(
                dashboard["customer_silhouette"]
            ),
            4,
        )

        # =================================================
        # GUARANTEE ARRAY TYPES
        # =================================================

        array_fields = (
            "sales_trend",
            "forecast",
            "inventory_data",
            "customer_segments",
            "insights",
            "recommendations",
            "alert_items",
        )

        for key in array_fields:

            if not isinstance(
                dashboard.get(key),
                list,
            ):

                dashboard[key] = []

        # =================================================
        # FINAL COUNTS
        # =================================================

        dashboard["customer_segments_count"] = len(
            dashboard["customer_segments"]
        )

        # =================================================
        # FINAL MODEL STATUS
        # =================================================

        if not dashboard.get(
            "model_status"
        ):

            dashboard["model_status"] = (
                "unknown"
            )

        # =================================================
        # FINAL SYSTEM STATUS
        #
        # IMPORTANT FIX:
        #
        # Previously this was:
        #
        #     if not dashboard.get("status"):
        #         dashboard["status"] = "healthy"
        #
        # But empty_dashboard() initializes status as
        # "unknown", and "unknown" is truthy.
        #
        # Therefore the frontend always received:
        #
        #     status = "unknown"
        #
        # Now we perform an actual health check.
        # =================================================

        try:

            health = DashboardService.health()

            system_status = str(
                health.get(
                    "status",
                    "unknown",
                )
                or "unknown"
            ).strip().lower()

            if system_status not in {
                "healthy",
                "degraded",
                "unknown",
            }:

                system_status = "unknown"

            dashboard["status"] = (
                system_status
            )

            # Keep the explicit system field available
            # for frontend/API consumers.

            dashboard["system"] = (
                system_status
            )

            dashboard["database_status"] = str(
                health.get(
                    "database",
                    "unknown",
                )
                or "unknown"
            ).strip().lower()

        except Exception:

            logger.exception(
                "Unable to determine dashboard "
                "system status"
            )

            dashboard["status"] = (
                "unknown"
            )

            dashboard["system"] = (
                "unknown"
            )

            dashboard["database_status"] = (
                "unknown"
            )

        return dashboard

    # =====================================================
    # KPI DATA
    # =====================================================

    @staticmethod
    def get_kpis() -> dict[str, Any]:
        """
        Return lightweight KPI data.

        Uses executive_dashboard() so KPI calculations
        remain consistent with the main dashboard.
        """

        try:

            response = (
                DashboardService.executive_dashboard()
            )

            if not isinstance(
                response,
                dict,
            ):

                return {
                    "status": "error",
                    "message":
                        "Invalid dashboard response",
                }

            if response.get(
                "status"
            ) != "success":

                return {
                    "status": "error",
                    "message":
                        response.get(
                            "message",
                            "KPI generation failed",
                        ),
                }

            executive = (
                response.get("executive")
                or DashboardService.empty_dashboard()
            )

            return {

                "status": "success",

                "revenue":
                    DashboardService.to_float(
                        executive.get(
                            "revenue",
                            0,
                        )
                    ),

                "profit":
                    DashboardService.to_float(
                        executive.get(
                            "profit",
                            0,
                        )
                    ),

                "profit_margin":
                    DashboardService.to_float(
                        executive.get(
                            "profit_margin",
                            0,
                        )
                    ),

                "growth":
                    DashboardService.to_float(
                        executive.get(
                            "growth",
                            0,
                        )
                    ),

                "inventory":
                    DashboardService.to_int(
                        executive.get(
                            "inventory",
                            0,
                        )
                    ),

                "inventory_demand":
                    DashboardService.to_float(
                        executive.get(
                            "inventory_demand",
                            0,
                        )
                    ),

                "inventory_status":
                    str(
                        executive.get(
                            "inventory_status",
                            "Unknown",
                        )
                    ),

                "inventory_coverage":
                    DashboardService.to_float(
                        executive.get(
                            "inventory_coverage",
                            0,
                        )
                    ),

                "customers":
                    DashboardService.to_int(
                        executive.get(
                            "customers",
                            0,
                        )
                    ),

                "customer_segments":
                    DashboardService.to_int(
                        executive.get(
                            "customer_segments_count",
                            0,
                        )
                    ),

                "model_status":
                    str(
                        executive.get(
                            "model_status",
                            "unknown",
                        )
                    ),

                "alerts":
                    DashboardService.to_int(
                        executive.get(
                            "alerts",
                            0,
                        )
                    ),

                "sales_r2":
                    DashboardService.to_float(
                        executive.get(
                            "sales_r2",
                            0,
                        )
                    ),

                "customer_silhouette":
                    DashboardService.to_float(
                        executive.get(
                            "customer_silhouette",
                            0,
                        )
                    ),

                "system":
                    str(
                        executive.get(
                            "system",
                            executive.get(
                                "status",
                                "unknown",
                            ),
                        )
                    ),

            }

        except Exception as exc:

            logger.exception(
                "KPI generation failed"
            )

            return {
                "status": "error",
                "message": str(exc),
            }

    # =====================================================
    # DASHBOARD SUMMARY
    # =====================================================

    @staticmethod
    def dashboard_summary() -> dict[str, Any]:
        """
        Return the complete executive dashboard summary.

        Kept as a compatibility wrapper for existing
        API routes.
        """

        try:

            return (
                DashboardService.executive_dashboard()
            )

        except Exception as exc:

            logger.exception(
                "Dashboard summary failed"
            )

            return {
                "status": "error",
                "message": str(exc),
                "executive":
                    DashboardService.empty_dashboard(),
                "generated_at":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
            }

    # =====================================================
    # BUSINESS ALERTS
    # =====================================================

    @staticmethod
    def dashboard_alerts() -> dict[str, Any]:
        """
        Load unresolved business alerts from PostgreSQL.

        Alerts are prioritized by:

        1. Severity
        2. Newest creation time
        """

        db: Optional[Session] = None

        try:

            db = SessionLocal()

            # -------------------------------------------------
            # COUNT UNRESOLVED ALERTS
            # -------------------------------------------------

            count = (
                db.query(
                    func.count(Alert.id)
                )
                .filter(
                    Alert.is_resolved.is_(False)
                )
                .scalar()
            )

            count = DashboardService.to_int(
                count
            )

            # -------------------------------------------------
            # LOAD RECENT ALERTS
            # -------------------------------------------------

            rows = (
                db.query(Alert)
                .filter(
                    Alert.is_resolved.is_(False)
                )
                .order_by(
                    Alert.created_at.desc()
                )
                .limit(20)
                .all()
            )

            alert_items: list[
                dict[str, Any]
            ] = []

            for alert in rows:

                created_at = getattr(
                    alert,
                    "created_at",
                    None,
                )

                severity = str(
                    getattr(
                        alert,
                        "severity",
                        None,
                    )
                    or "MEDIUM"
                ).upper()

                title = (
                    getattr(
                        alert,
                        "title",
                        None,
                    )
                    or "Business Alert"
                )

                message = (
                    getattr(
                        alert,
                        "message",
                        None,
                    )
                    or ""
                )

                module = getattr(
                    alert,
                    "module",
                    None,
                )

                alert_type = getattr(
                    alert,
                    "alert_type",
                    None,
                )

                entity_id = getattr(
                    alert,
                    "entity_id",
                    None,
                )

                alert_items.append(
                    {
                        "id":
                            getattr(
                                alert,
                                "id",
                                None,
                            ),

                        "severity":
                            severity,

                        "title":
                            str(title),

                        "message":
                            str(message),

                        "category":
                            str(
                                module
                                or alert_type
                                or "System"
                            ),

                        "module":
                            module,

                        "entity_id":
                            entity_id,

                        "alert_type":
                            str(
                                alert_type
                                or "SYSTEM"
                            ),

                        "is_read":
                            bool(
                                getattr(
                                    alert,
                                    "is_read",
                                    False,
                                )
                            ),

                        "is_resolved":
                            bool(
                                getattr(
                                    alert,
                                    "is_resolved",
                                    False,
                                )
                            ),

                        "time":
                            (
                                created_at.isoformat()
                                if created_at
                                else None
                            ),

                        "created_at":
                            (
                                created_at.isoformat()
                                if created_at
                                else None
                            ),
                    }
                )

            # -------------------------------------------------
            # PRIORITIZE SEVERITY + RECENCY
            # -------------------------------------------------

            severity_order = {
                "CRITICAL": 0,
                "HIGH": 1,
                "MEDIUM": 2,
                "LOW": 3,
            }

            def alert_sort_key(
                item: dict[str, Any],
            ) -> tuple[int, float]:

                severity_rank = (
                    severity_order.get(
                        item.get(
                            "severity",
                            "MEDIUM",
                        ),
                        99,
                    )
                )

                time_value = item.get(
                    "time"
                )

                try:

                    timestamp = (
                        datetime.fromisoformat(
                            time_value
                        ).timestamp()
                        if time_value
                        else 0.0
                    )

                except (
                    TypeError,
                    ValueError,
                    OverflowError,
                ):

                    timestamp = 0.0

                return (
                    severity_rank,
                    -timestamp,
                )

            alert_items.sort(
                key=alert_sort_key
            )

            return {
                "status": "success",
                "count": count,
                "alerts": alert_items,
            }

        except Exception as exc:

            logger.exception(
                "Unable to load dashboard alerts"
            )

            return {
                "status": "error",
                "count": 0,
                "alerts": [],
                "message": str(exc),
            }

        finally:

            if db is not None:

                try:

                    db.close()

                except Exception:

                    logger.warning(
                        "Failed to close dashboard "
                        "database session"
                    )

    # =====================================================
    # HEALTH
    # =====================================================

    @staticmethod
    def health() -> dict[str, Any]:
        """
        Check dashboard service and PostgreSQL health.

        The dashboard uses this method as the authoritative
        source for the frontend System status.

        Possible statuses:

            healthy
            degraded
            unknown
        """

        db: Optional[Session] = None

        try:

            db = SessionLocal()

            # -------------------------------------------------
            # DATABASE CONNECTIVITY
            # -------------------------------------------------

            total_alerts = (
                db.query(
                    func.count(Alert.id)
                ).scalar()
            )

            active_alerts = (
                db.query(
                    func.count(Alert.id)
                )
                .filter(
                    Alert.is_resolved.is_(False)
                )
                .scalar()
            )

            unread_alerts = (
                db.query(
                    func.count(Alert.id)
                )
                .filter(
                    Alert.is_resolved.is_(False),
                    Alert.is_read.is_(False),
                )
                .scalar()
            )

            critical_alerts = (
                db.query(
                    func.count(Alert.id)
                )
                .filter(
                    Alert.is_resolved.is_(False),
                    Alert.severity == "CRITICAL",
                )
                .scalar()
            )

            # -------------------------------------------------
            # DATABASE IS REACHABLE
            # -------------------------------------------------

            database_status = "healthy"

            overall_status = "healthy"

            return {
                "service":
                    "Dashboard Service",

                "status":
                    overall_status,

                "system":
                    overall_status,

                "database":
                    database_status,

                "total_alerts":
                    DashboardService.to_int(
                        total_alerts
                    ),

                "active_alerts":
                    DashboardService.to_int(
                        active_alerts
                    ),

                "unread_alerts":
                    DashboardService.to_int(
                        unread_alerts
                    ),

                "critical_alerts":
                    DashboardService.to_int(
                        critical_alerts
                    ),

                "timestamp":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
            }

        except Exception as exc:

            logger.exception(
                "Dashboard health check failed"
            )

            return {
                "service":
                    "Dashboard Service",

                "status":
                    "degraded",

                "system":
                    "degraded",

                "database":
                    "unavailable",

                "total_alerts":
                    0,

                "active_alerts":
                    0,

                "unread_alerts":
                    0,

                "critical_alerts":
                    0,

                "message":
                    str(exc),

                "timestamp":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
            }

        finally:

            if db is not None:

                try:

                    db.close()

                except Exception:

                    logger.warning(
                        "Failed to close dashboard "
                        "health database session"
                    )

    # =====================================================
    # FIRST VALUE
    # =====================================================

    @staticmethod
    def first_value(
        data: dict[str, Any],
        *keys: str,
        default: Any = None,
    ) -> Any:
        """
        Return the first existing non-None value.
        """

        if not isinstance(
            data,
            dict,
        ):

            return default

        for key in keys:

            if (
                key in data
                and data[key] is not None
            ):

                return data[key]

        return default

    # =====================================================
    # SALES TREND NORMALIZATION
    # =====================================================

    @staticmethod
    def normalize_sales_trend(
        sales_trend: Any,
    ) -> list[dict[str, Any]]:
        """
        Normalize sales-trend data into:

        [
            {
                "month": "...",
                "sales": 123.45
            }
        ]
        """

        if not isinstance(
            sales_trend,
            list,
        ):

            return []

        fixed_sales: list[
            dict[str, Any]
        ] = []

        for index, item in enumerate(
            sales_trend
        ):

            if isinstance(
                item,
                dict,
            ):

                month = (
                    item.get("month")
                    or item.get("date")
                    or item.get("Date")
                    or item.get("category")
                    or item.get("period")
                    or item.get("name")
                    or f"Period {index + 1}"
                )

                value = DashboardService.first_value(
                    item,
                    "sales",
                    "Sales",
                    "value",
                    "revenue",
                    "Revenue",
                    "total_sales",
                    default=0,
                )

                fixed_sales.append(
                    {
                        "month": str(
                            month
                        ),
                        "sales":
                            DashboardService.to_float(
                                value
                            ),
                    }
                )

            elif isinstance(
                item,
                (int, float),
            ) and not isinstance(
                item,
                bool,
            ):

                fixed_sales.append(
                    {
                        "month":
                            f"Period {index + 1}",

                        "sales":
                            DashboardService.to_float(
                                item
                            ),
                    }
                )

        return fixed_sales

    # =====================================================
    # INVENTORY NORMALIZATION
    # =====================================================

    @staticmethod
    def normalize_inventory(
        inventory_data: Any,
    ) -> list[dict[str, Any]]:
        """
        Normalize inventory data for the frontend.
        """

        if not isinstance(
            inventory_data,
            list,
        ):

            return []

        fixed_inventory: list[
            dict[str, Any]
        ] = []

        for index, item in enumerate(
            inventory_data
        ):

            if not isinstance(
                item,
                dict,
            ):

                continue

            product = (
                item.get("product")
                or item.get("name")
                or item.get("Product")
                or item.get("Product Name")
                or item.get("product_name")
                or f"Product {index + 1}"
            )

            quantity = DashboardService.first_value(
                item,
                "quantity",
                "stock",
                "Inventory",
                "inventory",
                "inventory_units",
                "value",
                default=0,
            )

            demand = DashboardService.first_value(
                item,
                "demand",
                "predictedDemand",
                "predicted_demand",
                "predicted",
                "forecast",
                "prediction",
                "yhat",
                default=0,
            )

            fixed_inventory.append(
                {
                    "product":
                        str(product),

                    "quantity":
                        DashboardService.to_float(
                            quantity
                        ),

                    "demand":
                        DashboardService.to_float(
                            demand
                        ),
                }
            )

        return fixed_inventory

    # =====================================================
    # CUSTOMER SEGMENT NORMALIZATION
    # =====================================================

    @staticmethod
    def normalize_customer_segments(
        clusters: Any,
    ) -> list[dict[str, Any]]:
        """
        Normalize customer-clustering output.

        Supports dictionary and list formats.
        """

        # -------------------------------------------------
        # DICTIONARY
        # -------------------------------------------------

        if isinstance(
            clusters,
            dict,
        ):

            fixed_segments: list[
                dict[str, Any]
            ] = []

            for key, value in clusters.items():

                if isinstance(
                    value,
                    dict,
                ):

                    count = DashboardService.first_value(
                        value,
                        "customers",
                        "customer_count",
                        "count",
                        "value",
                        "size",
                        default=0,
                    )

                    name = (
                        value.get("segment")
                        or value.get("name")
                        or value.get("label")
                        or f"Cluster {key}"
                    )

                else:

                    count = value

                    name = (
                        f"Cluster {key}"
                    )

                fixed_segments.append(
                    {
                        "segment":
                            str(name),

                        "customers":
                            DashboardService.to_int(
                                count
                            ),
                    }
                )

            return fixed_segments

        # -------------------------------------------------
        # LIST
        # -------------------------------------------------

        if isinstance(
            clusters,
            list,
        ):

            fixed_segments: list[
                dict[str, Any]
            ] = []

            for index, item in enumerate(
                clusters
            ):

                if not isinstance(
                    item,
                    dict,
                ):

                    continue

                segment = (
                    item.get("segment")
                    or item.get("name")
                    or item.get("cluster_name")
                    or item.get("label")
                    or item.get("cluster")
                    or f"Segment {index + 1}"
                )

                count = DashboardService.first_value(
                    item,
                    "customers",
                    "customer_count",
                    "count",
                    "value",
                    "size",
                    default=0,
                )

                fixed_segments.append(
                    {
                        "segment":
                            str(segment),

                        "customers":
                            DashboardService.to_int(
                                count
                            ),

                        "cluster":
                            item.get(
                                "cluster"
                            ),
                    }
                )

            return fixed_segments

        return []

    # =====================================================
    # FORECAST NORMALIZATION
    # =====================================================

    @staticmethod
    def normalize_forecast(
        forecast_data: Any,
    ) -> list[dict[str, Any]]:
        """
        Normalize forecast output into a stable
        frontend structure.
        """

        if not isinstance(
            forecast_data,
            list,
        ):

            return []

        fixed_forecast: list[
            dict[str, Any]
        ] = []

        for index, item in enumerate(
            forecast_data
        ):

            # -------------------------------------------------
            # DICTIONARY
            # -------------------------------------------------

            if isinstance(
                item,
                dict,
            ):

                raw_ds = item.get(
                    "ds",
                    "",
                )

                date = (
                    item.get("date")
                    or item.get("month")
                    or item.get("Date")
                    or item.get("period")
                    or (
                        str(raw_ds)[:10]
                        if raw_ds
                        else None
                    )
                    or f"Period {index + 1}"
                )

                demand = DashboardService.first_value(
                    item,
                    "demand",
                    "forecast",
                    "prediction",
                    "yhat",
                    "predicted_demand",
                    "predictedDemand",
                    "value",
                    default=0,
                )

                # ---------------------------------------------
                # ACTUAL
                # ---------------------------------------------

                actual = None

                actual_value = item.get(
                    "actual"
                )

                if actual_value is None:

                    actual_value = item.get(
                        "Actual"
                    )

                if actual_value is not None:

                    actual = (
                        DashboardService.to_float(
                            actual_value
                        )
                    )

                # ---------------------------------------------
                # LOWER
                # ---------------------------------------------

                lower = None

                lower_value = (
                    item.get("lower")
                    if item.get("lower")
                    is not None
                    else item.get("yhat_lower")
                )

                if lower_value is not None:

                    lower = (
                        DashboardService.to_float(
                            lower_value
                        )
                    )

                # ---------------------------------------------
                # UPPER
                # ---------------------------------------------

                upper = None

                upper_value = (
                    item.get("upper")
                    if item.get("upper")
                    is not None
                    else item.get("yhat_upper")
                )

                if upper_value is not None:

                    upper = (
                        DashboardService.to_float(
                            upper_value
                        )
                    )

                # ---------------------------------------------
                # FORECAST TYPE
                # ---------------------------------------------

                forecast_type = (
                    item.get("forecast_type")
                    or item.get("type")
                    or (
                        "historical"
                        if actual is not None
                        else "future"
                    )
                )

                fixed_forecast.append(
                    {
                        "date":
                            str(date),

                        "demand":
                            DashboardService.to_float(
                                demand
                            ),

                        "actual":
                            actual,

                        "lower":
                            lower,

                        "upper":
                            upper,

                        "forecast_type":
                            str(
                                forecast_type
                            ),
                    }
                )

            # -------------------------------------------------
            # NUMERIC
            # -------------------------------------------------

            elif isinstance(
                item,
                (int, float),
            ) and not isinstance(
                item,
                bool,
            ):

                fixed_forecast.append(
                    {
                        "date":
                            f"Period {index + 1}",

                        "demand":
                            DashboardService.to_float(
                                item
                            ),

                        "actual":
                            None,

                        "lower":
                            None,

                        "upper":
                            None,

                        "forecast_type":
                            "future",
                    }
                )

        return fixed_forecast

    # =====================================================
    # NUMERIC HELPERS
    # =====================================================

    @staticmethod
    def to_float(
        value: Any,
    ) -> float:
        """
        Safely convert a value to float.

        Handles:
        - None
        - bool
        - numeric strings
        - commas
        - currency symbols
        - percentage symbols
        - invalid values
        """

        try:

            if value is None:

                return 0.0

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
                    .replace("€", "")
                    .replace("£", "")
                    .replace("%", "")
                    .strip()
                )

                if not value:

                    return 0.0

            return float(value)

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):

            return 0.0

    # =====================================================
    # INTEGER HELPER
    # =====================================================

    @staticmethod
    def to_int(
        value: Any,
    ) -> int:
        """
        Safely convert a value to integer.

        Handles:
        - None
        - bool
        - numeric strings
        - commas
        - decimal values
        - invalid values
        """

        try:

            if value is None:

                return 0

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

                if not value:

                    return 0

            return int(
                float(value)
            )

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):

            return 0


# =========================================================
# END OF DASHBOARD SERVICE
# =========================================================

