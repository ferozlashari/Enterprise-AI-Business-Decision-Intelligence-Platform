
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Dashboard API Router

Handles:
- Dashboard API status
- Dashboard health
- Dashboard summary
- Dashboard KPI data
- Executive dashboard
- Business alerts

Author : Feroz Ali
=========================================================
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.services.dashboard_service import DashboardService

from backend.auth.dependencies import (
    get_current_user,
    require_roles,
)


# =========================================================
# LOGGER
# =========================================================

logger = logging.getLogger("DashboardAPI")


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# =========================================================
# ROLE CONFIGURATION
# =========================================================

DASHBOARD_ROLES = [
    "Admin",
    "Executive",
    "Manager",
    "Analyst",
]


# =========================================================
# HELPER
# =========================================================

def serialize_user(user: Any) -> Any:
    """
    Convert authenticated user into a JSON-safe object.

    Supports:
    - dict
    - Pydantic v2
    - Pydantic v1
    - SQLAlchemy-like objects
    - primitive values
    """

    if user is None:
        return None

    # -----------------------------------------------------
    # Primitive
    # -----------------------------------------------------

    if isinstance(
        user,
        (str, int, float, bool),
    ):
        return user

    # -----------------------------------------------------
    # Dict
    # -----------------------------------------------------

    if isinstance(user, dict):
        return user

    # -----------------------------------------------------
    # Pydantic v2
    # -----------------------------------------------------

    model_dump = getattr(
        user,
        "model_dump",
        None,
    )

    if callable(model_dump):

        try:
            return model_dump()

        except Exception:
            logger.debug(
                "Pydantic v2 model_dump failed",
                exc_info=True,
            )

    # -----------------------------------------------------
    # Pydantic v1
    # -----------------------------------------------------

    dict_method = getattr(
        user,
        "dict",
        None,
    )

    if callable(dict_method):

        try:
            return dict_method()

        except Exception:
            logger.debug(
                "Pydantic v1 dict() failed",
                exc_info=True,
            )

    # -----------------------------------------------------
    # SQLAlchemy / Generic object
    # -----------------------------------------------------

    result: dict[str, Any] = {}

    for field in (
        "id",
        "username",
        "email",
        "role",
        "is_active",
    ):

        try:

            value = getattr(
                user,
                field,
                None,
            )

            if value is not None:
                result[field] = value

        except Exception:
            continue

    # -----------------------------------------------------
    # Fallback
    # -----------------------------------------------------

    if result:
        return result

    return str(user)


# =========================================================
# SAFE DICTIONARY
# =========================================================

def ensure_dict(
    value: Any,
    default: dict[str, Any] | None = None,
) -> dict[str, Any]:

    if isinstance(value, dict):
        return value

    return default.copy() if default else {}


# =========================================================
# NORMALIZE SYSTEM STATUS
# =========================================================

def normalize_system_status(
    dashboard: dict[str, Any],
) -> str:
    """
    Determine the system status from the dashboard service.

    Priority:
    1. status
    2. system_status
    3. systemStatus
    4. health
    5. state

    Never falsely reports success when the backend does not
    provide a real system status.
    """

    candidates = (
        dashboard.get("status"),
        dashboard.get("system_status"),
        dashboard.get("systemStatus"),
        dashboard.get("health"),
        dashboard.get("state"),
    )

    for value in candidates:

        if value is None:
            continue

        value = str(value).strip().lower()

        if not value:
            continue

        # -------------------------------------------------
        # Normalize common values
        # -------------------------------------------------

        if value in {
            "ok",
            "running",
            "healthy",
            "active",
            "success",
        }:
            return "healthy"

        if value in {
            "warning",
            "degraded",
        }:
            return "degraded"

        if value in {
            "error",
            "failed",
            "failure",
            "down",
            "unavailable",
        }:
            return "error"

        return value

    return "unknown"


# =========================================================
# NORMALIZE EXECUTIVE DASHBOARD
# =========================================================

def normalize_executive_dashboard(
    dashboard: Any,
) -> dict[str, Any]:
    """
    Normalize the executive dashboard response.

    Backend/service values remain authoritative.

    This helper only fills missing structural fields and
    does not replace valid backend data.
    """

    data = ensure_dict(dashboard)

    # -----------------------------------------------------
    # System status
    # -----------------------------------------------------

    system_status = normalize_system_status(data)

    if (
        "status" not in data
        or data.get("status") in (None, "")
    ):
        data["status"] = system_status

    # -----------------------------------------------------
    # Model status
    # -----------------------------------------------------

    if not data.get("model_status"):

        model_status = (
            data.get("modelStatus")
            or data.get("ai_status")
            or data.get("aiStatus")
        )

        if model_status:
            data["model_status"] = str(
                model_status
            )

        else:
            # Do not claim that an AI model is successful
            # unless the service actually provides status.
            data["model_status"] = "unknown"

    # -----------------------------------------------------
    # KPI defaults
    # -----------------------------------------------------

    data.setdefault(
        "revenue",
        0,
    )

    data.setdefault(
        "profit",
        0,
    )

    data.setdefault(
        "inventory",
        0,
    )

    data.setdefault(
        "customers",
        0,
    )

    # -----------------------------------------------------
    # Analytics defaults
    # -----------------------------------------------------

    data.setdefault(
        "sales_trend",
        [],
    )

    data.setdefault(
        "forecast",
        [],
    )

    data.setdefault(
        "inventory_data",
        [],
    )

    data.setdefault(
        "customer_segments",
        [],
    )

    # -----------------------------------------------------
    # Alerts
    # -----------------------------------------------------

    if "alerts" not in data:

        data["alerts"] = 0

    if "alert_items" not in data:

        data["alert_items"] = []

    # -----------------------------------------------------
    # Recommendations
    # -----------------------------------------------------

    if "recommendations" not in data:

        data["recommendations"] = []

    return data


# =========================================================
# DASHBOARD ROOT
# =========================================================
#
# GET /dashboard/
#
# Public
#
# =========================================================

@router.get(
    "/",
    summary="Dashboard API status",
)
def dashboard() -> dict[str, Any]:

    return {
        "message": (
            "Enterprise AI Dashboard API Running"
        ),
        "status": "active",
        "service": "Dashboard Service",
    }


# =========================================================
# DASHBOARD SUMMARY
# =========================================================
#
# GET /dashboard/summary
#
# Protected
#
# =========================================================

@router.get(
    "/summary",
    summary="Get dashboard summary",
)
def dashboard_summary(
    user=Depends(
        get_current_user
    ),
) -> dict[str, Any]:

    try:

        dashboard_data = (
            DashboardService.dashboard_summary()
        )

        # -------------------------------------------------
        # Validate response
        # -------------------------------------------------

        if not isinstance(
            dashboard_data,
            dict,
        ):

            logger.error(
                "Dashboard summary returned invalid "
                "response type: %s",
                type(dashboard_data).__name__,
            )

            raise HTTPException(
                status_code=500,
                detail="Invalid dashboard response",
            )

        # -------------------------------------------------
        # Service-level error
        # -------------------------------------------------

        if dashboard_data.get(
            "status"
        ) == "error":

            raise HTTPException(
                status_code=500,
                detail=dashboard_data.get(
                    "message",
                    "Dashboard summary generation failed",
                ),
            )

        # -------------------------------------------------
        # Normalize
        # -------------------------------------------------

        dashboard_data = ensure_dict(
            dashboard_data
        )

        # -------------------------------------------------
        # Success
        # -------------------------------------------------

        return {
            "status": "success",
            "user": serialize_user(user),
            "dashboard": dashboard_data,
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Dashboard summary endpoint failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# DASHBOARD KPI
# =========================================================
#
# GET /dashboard/kpi
#
# Accessible by:
# - Admin
# - Executive
# - Manager
# - Analyst
#
# =========================================================

@router.get(
    "/kpi",
    summary="Get dashboard KPI data",
)
def dashboard_kpi(
    user=Depends(
        require_roles(
            DASHBOARD_ROLES
        )
    ),
) -> dict[str, Any]:

    try:

        kpi = (
            DashboardService.get_kpis()
        )

        # -------------------------------------------------
        # Validate response
        # -------------------------------------------------

        if not isinstance(
            kpi,
            dict,
        ):

            logger.error(
                "KPI service returned invalid response type: %s",
                type(kpi).__name__,
            )

            raise HTTPException(
                status_code=500,
                detail="Invalid KPI response",
            )

        # -------------------------------------------------
        # Service-level error
        # -------------------------------------------------

        if kpi.get(
            "status"
        ) == "error":

            raise HTTPException(
                status_code=500,
                detail=kpi.get(
                    "message",
                    "KPI generation failed",
                ),
            )

        # -------------------------------------------------
        # Success
        # -------------------------------------------------

        return {
            "status": "success",
            "user": serialize_user(user),
            "kpi": kpi,
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Dashboard KPI endpoint failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# EXECUTIVE DASHBOARD
# =========================================================
#
# GET /dashboard/executive
#
# Accessible by:
# - Admin
# - Executive
# - Manager
# - Analyst
#
# =========================================================

@router.get(
    "/executive",
    summary="Get executive dashboard",
)
def executive_dashboard(
    user=Depends(
        require_roles(
            DASHBOARD_ROLES
        )
    ),
) -> dict[str, Any]:

    try:

        dashboard_data = (
            DashboardService.executive_dashboard()
        )

        # -------------------------------------------------
        # Validate response
        # -------------------------------------------------

        if not isinstance(
            dashboard_data,
            dict,
        ):

            logger.error(
                "Executive dashboard returned invalid "
                "response type: %s",
                type(dashboard_data).__name__,
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "Invalid executive dashboard response"
                ),
            )

        # -------------------------------------------------
        # Service-level error
        # -------------------------------------------------

        if dashboard_data.get(
            "status"
        ) == "error":

            raise HTTPException(
                status_code=500,
                detail=dashboard_data.get(
                    "message",
                    "Dashboard generation failed",
                ),
            )

        # -------------------------------------------------
        # Normalize dashboard
        # -------------------------------------------------

        dashboard_data = (
            normalize_executive_dashboard(
                dashboard_data
            )
        )

        # -------------------------------------------------
        # Determine API status
        #
        # API status describes request success.
        # Dashboard status describes actual system health.
        # They are intentionally separate.
        # -------------------------------------------------

        api_status = "success"

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        return {
            "status": api_status,

            "user": serialize_user(user),

            "executive": dashboard_data,

            # -------------------------------------------------
            # Explicit system status
            #
            # This makes the status easy for frontend clients
            # to consume without having to inspect executive.
            # -------------------------------------------------

            "system_status": dashboard_data.get(
                "status",
                "unknown",
            ),

            "model_status": dashboard_data.get(
                "model_status",
                "unknown",
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Executive dashboard endpoint failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# BUSINESS ALERTS
# =========================================================
#
# GET /dashboard/alerts
#
# Accessible by:
# - Admin
# - Executive
# - Manager
# - Analyst
#
# =========================================================

@router.get(
    "/alerts",
    summary="Get unresolved business alerts",
)
def dashboard_alerts(
    user=Depends(
        require_roles(
            DASHBOARD_ROLES
        )
    ),
) -> dict[str, Any]:

    try:

        alerts = (
            DashboardService.dashboard_alerts()
        )

        # -------------------------------------------------
        # Validate response
        # -------------------------------------------------

        if not isinstance(
            alerts,
            dict,
        ):

            logger.error(
                "Dashboard alerts returned invalid "
                "response type: %s",
                type(alerts).__name__,
            )

            raise HTTPException(
                status_code=500,
                detail="Invalid alerts response",
            )

        # -------------------------------------------------
        # Service-level error
        # -------------------------------------------------

        if alerts.get(
            "status"
        ) == "error":

            raise HTTPException(
                status_code=500,
                detail=alerts.get(
                    "message",
                    "Unable to load dashboard alerts",
                ),
            )

        # -------------------------------------------------
        # Success
        # -------------------------------------------------

        return {
            "status": "success",
            "user": serialize_user(user),
            "alerts": alerts,
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Dashboard alerts endpoint failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# DASHBOARD HEALTH
# =========================================================
#
# GET /dashboard/health
#
# Public
#
# =========================================================

@router.get(
    "/health",
    summary="Check dashboard service health",
)
def dashboard_health() -> dict[str, Any]:

    try:

        health = (
            DashboardService.health()
        )

        # -------------------------------------------------
        # Validate response
        # -------------------------------------------------

        if not isinstance(
            health,
            dict,
        ):

            logger.error(
                "Dashboard health returned invalid "
                "response type: %s",
                type(health).__name__,
            )

            raise HTTPException(
                status_code=503,
                detail=(
                    "Invalid dashboard health response"
                ),
            )

        # -------------------------------------------------
        # Determine service status
        # -------------------------------------------------

        service_status = str(
            health.get(
                "status",
                "degraded",
            )
        ).strip().lower()

        # -------------------------------------------------
        # Healthy
        # -------------------------------------------------

        if service_status in {
            "healthy",
            "ok",
            "running",
            "active",
            "success",
        }:

            return {
                "status": "healthy",
                "backend": "Running",
                **health,
            }

        # -------------------------------------------------
        # Degraded
        #
        # Return payload instead of raising 503 so the
        # frontend and monitoring layer can inspect it.
        # -------------------------------------------------

        return {
            "status": "degraded",
            "backend": "Running",
            **health,
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Dashboard health endpoint failed"
        )

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

