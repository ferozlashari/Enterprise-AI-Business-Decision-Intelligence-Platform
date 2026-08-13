
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Reports API

Responsibilities:
- Reports API endpoints
- Sales reports
- Inventory reports
- Customer segmentation reports
- Forecast reports
- Business KPI reports
- Executive summary
- Dashboard analytics
- AI Copilot analytics context
- Available report files
- Report service health

Author: Feroz Ali
=========================================================
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from config.settings import settings
from backend.services.report_service import ReportService


# =========================================================
# LOGGER
# =========================================================

logger = logging.getLogger("ReportsAPI")


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


# =========================================================
# REPORT DIRECTORIES
# =========================================================

REPORT_DIR = Path(
    getattr(
        settings,
        "REPORT_DIR",
        "reports",
    )
)

JSON_REPORT_DIR = REPORT_DIR / "json"


# =========================================================
# DIRECTORY INITIALIZATION
# =========================================================

try:
    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    JSON_REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

except Exception:
    logger.exception(
        "Unable to initialize report directories"
    )


# =========================================================
# INTERNAL ERROR RESPONSE
# =========================================================

def _error_response(
    message: str,
    exc: Exception,
    status_code: int = 500,
) -> JSONResponse:
    """
    Build a consistent API error response.
    """

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": message,
            "detail": str(exc),
        },
    )


# =========================================================
# REPORTS HOME
# =========================================================

@router.get(
    "/",
    response_model=None,
)
def reports_home() -> dict[str, Any]:
    """
    Reports API health/home endpoint.
    """

    return {
        "module": "Enterprise Report API",
        "service": "ReportService",
        "status": "Running",
        "report_directory": str(
            REPORT_DIR.resolve()
        ),
        "json_report_directory": str(
            JSON_REPORT_DIR.resolve()
        ),
    }


# =========================================================
# ALL REPORTS
# =========================================================

@router.get(
    "/all",
    response_model=None,
)
def all_reports() -> dict[str, Any] | JSONResponse:
    """
    Return all normalized enterprise reports.
    """

    try:
        result = ReportService.get_all_reports()

        if isinstance(result, dict):
            return result

        return {
            "status": "success",
            "data": result,
        }

    except Exception as exc:
        logger.exception(
            "Failed to load all reports"
        )

        return _error_response(
            "Unable to load reports.",
            exc,
        )


# =========================================================
# SALES REPORT
# =========================================================

@router.get(
    "/sales",
    response_model=None,
)
def sales_report() -> dict[str, Any] | JSONResponse:
    """
    Return normalized sales report.
    """

    try:
        result = ReportService.sales_report()

        if isinstance(result, dict):
            return result

        return {
            "status": "success",
            "data": result,
        }

    except Exception as exc:
        logger.exception(
            "Sales report failed"
        )

        return _error_response(
            "Unable to load sales report.",
            exc,
        )


# =========================================================
# INVENTORY REPORT
# =========================================================

@router.get(
    "/inventory",
    response_model=None,
)
def inventory_report() -> dict[str, Any] | JSONResponse:
    """
    Return normalized inventory report.
    """

    try:
        result = ReportService.inventory_report()

        if isinstance(result, dict):
            return result

        return {
            "status": "success",
            "data": result,
        }

    except Exception as exc:
        logger.exception(
            "Inventory report failed"
        )

        return _error_response(
            "Unable to load inventory report.",
            exc,
        )


# =========================================================
# CUSTOMER REPORT
# =========================================================

@router.get(
    "/customer",
    response_model=None,
)
def customer_report() -> dict[str, Any] | JSONResponse:
    """
    Return normalized customer segmentation report.
    """

    try:
        result = ReportService.customer_report()

        if isinstance(result, dict):
            return result

        return {
            "status": "success",
            "data": result,
        }

    except Exception as exc:
        logger.exception(
            "Customer report failed"
        )

        return _error_response(
            "Unable to load customer report.",
            exc,
        )


# =========================================================
# FORECAST REPORT
# =========================================================

@router.get(
    "/forecast",
    response_model=None,
)
def forecast_report() -> dict[str, Any] | JSONResponse:
    """
    Return normalized enterprise forecast report.
    """

    try:
        result = ReportService.forecast_report()

        if isinstance(result, dict):
            return result

        return {
            "status": "success",
            "data": result,
        }

    except Exception as exc:
        logger.exception(
            "Forecast report failed"
        )

        return _error_response(
            "Unable to load forecast report.",
            exc,
        )


# =========================================================
# BUSINESS KPI REPORT
# =========================================================

@router.get(
    "/business",
    response_model=None,
)
def business_report() -> dict[str, Any] | JSONResponse:
    """
    Return unified enterprise KPI report.
    """

    try:
        result = ReportService.business_kpi_report()

        if isinstance(result, dict):
            return result

        return {
            "status": "success",
            "data": result,
        }

    except Exception as exc:
        logger.exception(
            "Business KPI report failed"
        )

        return _error_response(
            "Unable to load business KPI report.",
            exc,
        )


# =========================================================
# KPI ALIAS
# =========================================================

@router.get(
    "/kpi",
    response_model=None,
)
def kpi_report() -> dict[str, Any] | JSONResponse:
    """
    Alias endpoint for the business KPI report.

    Example:
        GET /reports/kpi
    """

    try:
        result = ReportService.business_kpi_report()

        if isinstance(result, dict):
            return result

        return {
            "status": "success",
            "data": result,
        }

    except Exception as exc:
        logger.exception(
            "KPI report failed"
        )

        return _error_response(
            "Unable to load KPI report.",
            exc,
        )


# =========================================================
# EXECUTIVE REPORT
# =========================================================

@router.get(
    "/executive",
    response_model=None,
)
def executive_report() -> dict[str, Any] | JSONResponse:
    """
    Return executive summary report.
    """

    try:
        result = ReportService.executive_summary()

        if isinstance(result, dict):
            return result

        return {
            "status": "success",
            "data": result,
        }

    except Exception as exc:
        logger.exception(
            "Executive report failed"
        )

        return _error_response(
            "Unable to load executive report.",
            exc,
        )


# =========================================================
# DASHBOARD ANALYTICS
# =========================================================

@router.get(
    "/dashboard",
    response_model=None,
)
def dashboard_report() -> dict[str, Any] | JSONResponse:
    """
    Return the complete normalized dashboard
    analytics payload.
    """

    try:
        result = ReportService.dashboard_analytics()

        if isinstance(result, dict):
            return result

        return {
            "status": "success",
            "data": result,
        }

    except Exception as exc:
        logger.exception(
            "Dashboard analytics failed"
        )

        return _error_response(
            "Unable to load dashboard analytics.",
            exc,
        )


# =========================================================
# AI COPILOT CONTEXT
# =========================================================

@router.get(
    "/copilot",
    response_model=None,
)
def copilot_report() -> dict[str, Any] | JSONResponse:
    """
    Return compact analytics context for:

    - AI Copilot
    - RAG
    - LLM
    """

    try:
        result = ReportService.copilot_context()

        if isinstance(result, dict):
            return result

        return {
            "status": "success",
            "data": result,
        }

    except Exception as exc:
        logger.exception(
            "Copilot analytics context failed"
        )

        return _error_response(
            "Unable to load Copilot analytics context.",
            exc,
        )


# =========================================================
# AVAILABLE REPORT FILES
# =========================================================

@router.get(
    "/files",
    response_model=None,
)
def report_files() -> dict[str, Any] | JSONResponse:
    """
    Return available JSON report files.

    Search order:
        1. reports/json
        2. reports
    """

    try:

        # -------------------------------------------------
        # Prefer JSON report directory
        # -------------------------------------------------

        search_dir = JSON_REPORT_DIR

        if not search_dir.exists():
            search_dir = REPORT_DIR

        # -------------------------------------------------
        # Directory does not exist
        # -------------------------------------------------

        if not search_dir.exists():

            return {
                "status": "success",
                "message": "Reports folder not found.",
                "total_reports": 0,
                "files": [],
                "directory": str(
                    search_dir.resolve()
                ),
            }

        # -------------------------------------------------
        # Collect JSON files
        # -------------------------------------------------

        files = sorted(
            [
                file.name
                for file in search_dir.iterdir()
                if file.is_file()
                and file.suffix.lower() == ".json"
            ]
        )

        return {
            "status": "success",
            "total_reports": len(files),
            "files": files,
            "directory": str(
                search_dir.resolve()
            ),
        }

    except Exception as exc:

        logger.exception(
            "Unable to list report files"
        )

        return _error_response(
            "Unable to list report files.",
            exc,
        )


# =========================================================
# REPORT SERVICE HEALTH
# =========================================================

@router.get(
    "/health",
    response_model=None,
)
def reports_health() -> dict[str, Any]:
    """
    Return ReportService health information.
    """

    try:

        result = ReportService.health()

        if isinstance(result, dict):
            return result

        return {
            "status": "healthy",
            "service": "ReportService",
            "reports_directory": str(
                REPORT_DIR.resolve()
            ),
            "json_directory": str(
                JSON_REPORT_DIR.resolve()
            ),
            "reports_directory_exists":
                REPORT_DIR.exists(),
            "json_directory_exists":
                JSON_REPORT_DIR.exists(),
        }

    except Exception as exc:

        logger.exception(
            "Report service health check failed"
        )

        return {
            "status": "unhealthy",
            "service": "ReportService",
            "reports_directory": str(
                REPORT_DIR.resolve()
            ),
            "json_directory": str(
                JSON_REPORT_DIR.resolve()
            ),
            "reports_directory_exists":
                REPORT_DIR.exists(),
            "json_directory_exists":
                JSON_REPORT_DIR.exists(),
            "error": str(exc),
        }


# =========================================================
# PUBLIC EXPORTS
# =========================================================

__all__ = [
    "router",
    "reports_home",
    "all_reports",
    "sales_report",
    "inventory_report",
    "customer_report",
    "forecast_report",
    "business_report",
    "kpi_report",
    "executive_report",
    "dashboard_report",
    "copilot_report",
    "report_files",
    "reports_health",
]

