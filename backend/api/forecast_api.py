
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Forecast API

Provides:
- Demand / Sales Forecast
- Inventory Forecast
- Complete Forecast Intelligence
- Forecast Health Check

Author : Feroz Ali
=========================================================
"""

from fastapi import APIRouter, HTTPException

from backend.services.prediction_service import (
    PredictionService
)


router = APIRouter(
    prefix="/forecast",
    tags=["Forecast"]
)


# =========================================================
# FORECAST HOME
# =========================================================

@router.get("/")
def forecast_home():
    """
    Forecast API status endpoint.
    """

    return {
        "module": "Forecast API",
        "status": "Running",
        "service": "PredictionService"
    }


# =========================================================
# DEMAND / SALES FORECAST
# =========================================================

@router.get("/sales")
def sales_forecast():
    """
    Return demand/sales forecast.

    The underlying PredictionService reads:

        outputs/sales_forecast.csv

    and returns normalized frontend-compatible data:

        date
        forecast
        actual
        lower
        upper
    """

    try:

        result = PredictionService.get_forecast()

        if not isinstance(result, dict):

            raise ValueError(
                "Forecast service returned an invalid response."
            )

        return {
            "success": True,
            "module": "Demand Forecasting",
            "sales_forecast": result
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Unable to load sales forecast.",
                "error": str(error)
            }
        )


# =========================================================
# INVENTORY FORECAST
# =========================================================

@router.get("/inventory")
def inventory_forecast():
    """
    Return inventory prediction / forecast.
    """

    try:

        result = (
            PredictionService
            .get_inventory_prediction()
        )

        if not isinstance(result, dict):

            raise ValueError(
                "Inventory forecast service returned "
                "an invalid response."
            )

        return {
            "success": True,
            "module": "Inventory Forecasting",
            "inventory_forecast": result
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Unable to load inventory forecast.",
                "error": str(error)
            }
        )


# =========================================================
# COMPLETE FORECAST INTELLIGENCE
# =========================================================

@router.get("/all")
def all_forecasts():
    """
    Return all forecast-related intelligence.

    Includes:
        - Sales / Demand Forecast
        - Inventory Forecast
    """

    try:

        sales = (
            PredictionService
            .get_forecast()
        )

        inventory = (
            PredictionService
            .get_inventory_prediction()
        )

        return {
            "success": True,
            "module": "Forecast Intelligence",
            "sales_forecast": sales,
            "inventory_forecast": inventory
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Unable to load forecast intelligence.",
                "error": str(error)
            }
        )


# =========================================================
# FORECAST HEALTH CHECK
# =========================================================

@router.get("/health")
def forecast_health():
    """
    Forecast API health check.
    """

    try:

        service_health = (
            PredictionService
            .health()
        )

        return {
            "status": "Healthy",
            "service": "Forecast API",
            "prediction_service": service_health
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "status": "Unhealthy",
                "service": "Forecast API",
                "error": str(error)
            }
        )

