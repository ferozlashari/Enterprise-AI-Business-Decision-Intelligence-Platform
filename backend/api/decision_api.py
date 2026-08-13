
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Decision Intelligence API

Author : Feroz Ali

Responsibilities:
- Run enterprise decision analysis
- Return latest decision
- Return recommendations
- Provide Decision Engine health status
- Maintain stable API responses for React frontend
=========================================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.services.decision_service import DecisionService


logger = logging.getLogger("DecisionAPI")


# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    prefix="/decision",
    tags=["Decision Engine"],
)


# =====================================================
# REQUEST SCHEMA
# =====================================================

class DecisionInput(BaseModel):
    """
    Business metrics supplied to the Decision Engine.
    """

    predicted_sales: float = Field(
        default=0.0,
        ge=0.0,
        description="Predicted sales value.",
    )

    inventory: float = Field(
        default=0.0,
        ge=0.0,
        description="Available inventory units.",
    )

    forecast_growth: float = Field(
        default=0.0,
        ge=-100.0,
        le=100.0,
        description="Forecasted business growth percentage.",
    )

    customer_churn: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Customer churn percentage.",
    )

    revenue: float = Field(
        default=0.0,
        ge=0.0,
        description="Business revenue.",
    )

    profit: float = Field(
        default=0.0,
        description="Business profit.",
    )

    customers: int = Field(
        default=0,
        ge=0,
        description="Number of customers.",
    )


# =====================================================
# RESPONSE NORMALIZATION
# =====================================================

def _normalize_decision(
    result: Any,
) -> Dict[str, Any]:
    """
    Normalize DecisionService.generate_decision() output.

    Expected service response:

        {
            "status": "success",
            "module": "Decision Engine",
            "decision_id": "...",
            "decision": {...}
        }

    The API converts this into a predictable structure
    for the React frontend.
    """

    if not isinstance(result, dict):
        return {
            "status": "error",
            "decision_id": None,
            "decision": None,
            "message": (
                "Decision Engine returned "
                "an invalid response."
            ),
        }

    service_status = str(
        result.get("status", "success")
        or "success"
    ).strip().lower()

    if service_status == "error":
        return {
            "status": "error",
            "decision_id": result.get(
                "decision_id"
            ),
            "decision": None,
            "message": result.get(
                "message",
                "Decision generation failed.",
            ),
        }

    decision = result.get(
        "decision",
        {},
    )

    if decision is None:
        decision = {}

    if not isinstance(
        decision,
        dict,
    ):
        decision = {
            "value": decision,
        }

    return {
        "status": "success",
        "decision_id": result.get(
            "decision_id"
        ),
        "decision": decision,
    }


# =====================================================
# RUN DECISION ENGINE
# =====================================================

@router.post("/run")
def run_engine(
    data: DecisionInput,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Execute the Enterprise Decision Engine.

    Flow:

        React
          ↓
        DecisionInput
          ↓
        DecisionService
          ↓
        make_decision()
          ↓
        Database persistence
          ↓
        Stable API response
          ↓
        React
    """

    try:
        logger.info(
            "Decision Engine request received."
        )

        # -------------------------------------------------
        # Convert Pydantic model to dictionary
        # -------------------------------------------------

        payload = data.model_dump()

        logger.info(
            "Decision metrics received: "
            "predicted_sales=%s, inventory=%s, "
            "forecast_growth=%s, customer_churn=%s, "
            "revenue=%s, profit=%s, customers=%s",
            payload.get("predicted_sales"),
            payload.get("inventory"),
            payload.get("forecast_growth"),
            payload.get("customer_churn"),
            payload.get("revenue"),
            payload.get("profit"),
            payload.get("customers"),
        )

        # -------------------------------------------------
        # Create service
        # -------------------------------------------------

        service = DecisionService(
            db=db,
        )

        # -------------------------------------------------
        # Generate decision
        # -------------------------------------------------

        result = service.generate_decision(
            payload
        )

        # -------------------------------------------------
        # Normalize service response
        # -------------------------------------------------

        response = _normalize_decision(
            result
        )

        # -------------------------------------------------
        # Service failure
        # -------------------------------------------------

        if response["status"] == "error":

            logger.error(
                "Decision Engine failed: %s",
                response.get("message"),
            )

            raise HTTPException(
                status_code=500,
                detail=response.get(
                    "message",
                    "Decision generation failed.",
                ),
            )

        logger.info(
            "Decision Engine completed successfully. "
            "decision_id=%s",
            response.get("decision_id"),
        )

        # -------------------------------------------------
        # Stable frontend response
        # -------------------------------------------------

        return {
            "success": True,
            "status": "success",
            "engine": (
                "Enterprise Decision Intelligence"
            ),
            "decision_id": response.get(
                "decision_id"
            ),
            "decision": response.get(
                "decision",
                {},
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Decision Engine API failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Decision Engine failed: "
                f"{str(exc)}"
            ),
        )


# =====================================================
# CURRENT DECISION
# =====================================================

@router.get("/")
def current_decision(
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Return the latest valid Decision Intelligence result.

    No history is returned.
    """

    try:
        logger.info(
            "Loading current Decision Engine result."
        )

        service = DecisionService(
            db=db,
        )

        result = service.get_latest_decision()

        # -------------------------------------------------
        # Invalid service response
        # -------------------------------------------------

        if not isinstance(
            result,
            dict,
        ):
            return {
                "success": True,
                "status": "success",
                "decision": None,
                "message": (
                    "No decision generated yet."
                ),
            }

        service_status = str(
            result.get(
                "status",
                "success",
            )
            or "success"
        ).strip().lower()

        # -------------------------------------------------
        # Service error
        # -------------------------------------------------

        if service_status == "error":

            logger.error(
                "Failed to load current decision: %s",
                result.get("message"),
            )

            raise HTTPException(
                status_code=500,
                detail=result.get(
                    "message",
                    "Unable to load current decision.",
                ),
            )

        # -------------------------------------------------
        # Latest decision
        # -------------------------------------------------

        decision = result.get(
            "decision"
        )

        return {
            "success": True,
            "status": "success",
            "decision": decision,
            "message": result.get(
                "message"
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Failed to load current decision."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to load current decision: "
                f"{str(exc)}"
            ),
        )


# =====================================================
# RECOMMENDATIONS
# =====================================================

@router.get("/recommendations")
def recommendations(
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Return current Decision Engine recommendations.

    ALWAYS returns recommendations as a list.
    """

    try:
        logger.info(
            "Loading Decision Engine recommendations."
        )

        service = DecisionService(
            db=db,
        )

        result = service.get_recommendations()

        # -------------------------------------------------
        # Extract recommendations
        # -------------------------------------------------

        if isinstance(
            result,
            dict,
        ):

            service_status = str(
                result.get(
                    "status",
                    "success",
                )
                or "success"
            ).strip().lower()

            if service_status == "error":

                logger.error(
                    "Recommendation service failed: %s",
                    result.get("message"),
                )

                raise HTTPException(
                    status_code=500,
                    detail=result.get(
                        "message",
                        "Unable to load recommendations.",
                    ),
                )

            recommendations_data = result.get(
                "recommendations",
                [],
            )

        elif isinstance(
            result,
            list,
        ):

            recommendations_data = result

        else:

            recommendations_data = []

        # -------------------------------------------------
        # Guarantee list
        # -------------------------------------------------

        if recommendations_data is None:

            recommendations_data = []

        elif not isinstance(
            recommendations_data,
            list,
        ):

            recommendations_data = [
                recommendations_data
            ]

        logger.info(
            "Decision Engine recommendations loaded. "
            "count=%s",
            len(recommendations_data),
        )

        return {
            "success": True,
            "status": "success",
            "total_recommendations": len(
                recommendations_data
            ),
            "recommendations": (
                recommendations_data
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Failed to load recommendations."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to load recommendations: "
                f"{str(exc)}"
            ),
        )


# =====================================================
# LATEST DECISION
# =====================================================

@router.get("/latest")
def latest_decision(
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Return the most recently generated decision.

    Historical decisions are not exposed.
    """

    try:
        logger.info(
            "Loading latest Decision Engine decision."
        )

        service = DecisionService(
            db=db,
        )

        result = service.get_latest_decision()

        # -------------------------------------------------
        # Invalid service response
        # -------------------------------------------------

        if not isinstance(
            result,
            dict,
        ):

            return {
                "success": True,
                "status": "success",
                "decision": None,
                "message": (
                    "No decisions generated yet."
                ),
            }

        service_status = str(
            result.get(
                "status",
                "success",
            )
            or "success"
        ).strip().lower()

        # -------------------------------------------------
        # Service failure
        # -------------------------------------------------

        if service_status == "error":

            logger.error(
                "Latest decision service failed: %s",
                result.get("message"),
            )

            raise HTTPException(
                status_code=500,
                detail=result.get(
                    "message",
                    "Unable to load latest decision.",
                ),
            )

        # -------------------------------------------------
        # Stable response
        # -------------------------------------------------

        return {
            "success": True,
            "status": "success",
            "decision": result.get(
                "decision"
            ),
            "message": result.get(
                "message"
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Failed to load latest decision."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to load latest decision: "
                f"{str(exc)}"
            ),
        )


# =====================================================
# HEALTH CHECK
# =====================================================

@router.get("/health")
def decision_health(
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Check Decision Engine availability.

    This endpoint intentionally does NOT depend on a
    DecisionService.health() method. The service code
    provided earlier does not currently implement that
    method.

    Instead, this verifies that a DecisionService can be
    initialized and the database session is available.
    """

    try:

        logger.info(
            "Checking Decision Engine health."
        )

        # -------------------------------------------------
        # Verify service/database initialization
        # -------------------------------------------------

        service = DecisionService(
            db=db,
        )

        if service.db is None:

            raise RuntimeError(
                "Database session is unavailable."
            )

        return {
            "success": True,
            "status": "healthy",
            "engine": (
                "Enterprise Decision Intelligence"
            ),
            "database": "connected",
        }

    except Exception as exc:

        logger.exception(
            "Decision Engine health check failed."
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Decision Engine health check failed: "
                f"{str(exc)}"
            ),
        )

