
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Alert API Router

Handles:

- Business alerts
- Active alerts
- Alert acknowledgement
- Alert resolution
- Alert generation
- Alert service health

Author : Feroz Ali
=========================================================
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.auth.dependencies import require_roles
from backend.services.alert_service import AlertService


# =========================================================
# LOGGER
# =========================================================

logger = logging.getLogger("AlertAPI")


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


# =========================================================
# ROLE CONFIGURATION
# =========================================================

ALERT_VIEW_ROLES = [
    "Admin",
    "Executive",
    "Manager",
    "Analyst",
]

ALERT_MANAGE_ROLES = [
    "Admin",
    "Executive",
    "Manager",
]


# =========================================================
# GET ACTIVE ALERTS
# =========================================================

@router.get(
    "/",
    summary="Get active business alerts",
)
def get_alerts(
    user=Depends(
        require_roles(ALERT_VIEW_ROLES)
    ),
) -> dict[str, Any]:
    """
    Return all currently active/unresolved alerts.
    """

    try:

        result = AlertService.get_active_alerts()

        if not isinstance(result, dict):

            raise HTTPException(
                status_code=500,
                detail="Invalid alert service response",
            )

        if result.get("status") == "error":

            raise HTTPException(
                status_code=500,
                detail=result.get(
                    "message",
                    "Unable to load alerts",
                ),
            )

        return {
            "status": "success",
            "user": user,
            "count": result.get("count", 0),
            "alerts": result.get("alerts", []),
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Failed to load business alerts"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to load business alerts",
        ) from exc


# =========================================================
# GENERATE BUSINESS ALERTS
# =========================================================

@router.post(
    "/generate",
    summary="Generate business alerts",
)
def generate_alerts(
    user=Depends(
        require_roles(ALERT_MANAGE_ROLES)
    ),
) -> dict[str, Any]:
    """
    Execute the business alert detection engine.
    """

    try:

        result = AlertService.generate_business_alerts()

        if not isinstance(result, dict):

            raise HTTPException(
                status_code=500,
                detail="Invalid alert generation response",
            )

        if result.get("status") == "error":

            raise HTTPException(
                status_code=500,
                detail=result.get(
                    "message",
                    "Alert generation failed",
                ),
            )

        return {
            "status": "success",
            "user": user,
            "generated": result.get(
                "generated",
                0,
            ),
            "alerts": result.get(
                "alerts",
                [],
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Business alert generation failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Business alert generation failed",
        ) from exc


# =========================================================
# ACKNOWLEDGE ALERT
# =========================================================

@router.post(
    "/{alert_id}/acknowledge",
    summary="Acknowledge a business alert",
)
def acknowledge_alert(
    alert_id: int,
    user=Depends(
        require_roles(ALERT_MANAGE_ROLES)
    ),
) -> dict[str, Any]:
    """
    Mark an alert as read/acknowledged.
    """

    try:

        if alert_id <= 0:

            raise HTTPException(
                status_code=400,
                detail="Invalid alert ID",
            )

        result = AlertService.acknowledge_alert(
            alert_id
        )

        if not isinstance(result, dict):

            raise HTTPException(
                status_code=500,
                detail="Invalid acknowledgement response",
            )

        if result.get("status") == "error":

            status_code = (
                404
                if result.get("not_found")
                else 500
            )

            raise HTTPException(
                status_code=status_code,
                detail=result.get(
                    "message",
                    "Unable to acknowledge alert",
                ),
            )

        return {
            "status": "success",
            "message": "Alert acknowledged successfully",
            "alert": result.get("alert"),
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Alert acknowledgement failed: %s",
            alert_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Alert acknowledgement failed",
        ) from exc


# =========================================================
# RESOLVE ALERT
# =========================================================

@router.post(
    "/{alert_id}/resolve",
    summary="Resolve a business alert",
)
def resolve_alert(
    alert_id: int,
    user=Depends(
        require_roles(ALERT_MANAGE_ROLES)
    ),
) -> dict[str, Any]:
    """
    Mark an alert as resolved.
    """

    try:

        if alert_id <= 0:

            raise HTTPException(
                status_code=400,
                detail="Invalid alert ID",
            )

        result = AlertService.resolve_alert(
            alert_id
        )

        if not isinstance(result, dict):

            raise HTTPException(
                status_code=500,
                detail="Invalid resolution response",
            )

        if result.get("status") == "error":

            status_code = (
                404
                if result.get("not_found")
                else 500
            )

            raise HTTPException(
                status_code=status_code,
                detail=result.get(
                    "message",
                    "Unable to resolve alert",
                ),
            )

        return {
            "status": "success",
            "message": "Alert resolved successfully",
            "alert": result.get("alert"),
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Alert resolution failed: %s",
            alert_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Alert resolution failed",
        ) from exc


# =========================================================
# HEALTH
# =========================================================

@router.get(
    "/health",
    summary="Check alert service health",
)
def alert_health() -> dict[str, Any]:
    """
    Check AlertService and PostgreSQL connectivity.
    """

    try:

        result = AlertService.health()

        if not isinstance(result, dict):

            raise HTTPException(
                status_code=503,
                detail="Invalid alert health response",
            )

        if result.get("status") != "healthy":

            raise HTTPException(
                status_code=503,
                detail=result.get(
                    "message",
                    "Alert service is unavailable",
                ),
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Alert service health check failed"
        )

        raise HTTPException(
            status_code=503,
            detail="Alert service health check failed",
        ) from exc

