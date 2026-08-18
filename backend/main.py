
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform
Main FastAPI Application
=========================================================

Responsibilities:

- Create FastAPI application
- Configure CORS
- Register database models
- Register all API routers
- Configure application lifespan
- Provide system health endpoints
- Start Uvicorn when executed directly

Author : Feroz Ali
=========================================================
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# =========================================================
# DATABASE / MODEL REGISTRATION
# =========================================================
#
# Importing models registers all SQLAlchemy models
# with Base.metadata.
#
# This is important for:
#
# - SQLAlchemy
# - Alembic
# - PostgreSQL
# - Relationships
# - Foreign keys
#
# =========================================================

from backend.database import models  # noqa: F401



from config.settings import settings


# =========================================================
# API ROUTERS
# =========================================================

# ---------------------------------------------------------
# Authentication
# ---------------------------------------------------------

from backend.auth.auth_router import (
    router as auth_router,
)


# ---------------------------------------------------------
# AI Prediction Modules
# ---------------------------------------------------------

from backend.api.sales_api import (
    router as sales_router,
)

from backend.api.inventory_api import (
    router as inventory_router,
)

from backend.api.forecast_api import (
    router as forecast_router,
)

from backend.api.customer_api import (
    router as customer_router,
)


# ---------------------------------------------------------
# Business Intelligence
# ---------------------------------------------------------

from backend.api.dashboard_api import (
    router as dashboard_router,
)

from backend.api.reports_api import (
    router as reports_router,
)


# ---------------------------------------------------------
# Decision Intelligence
# ---------------------------------------------------------

from backend.api.decision_api import (
    router as decision_router,
)

from backend.api.recommendation_api import (
    router as recommendation_router,
)


# ---------------------------------------------------------
# AI / Copilot
# ---------------------------------------------------------

from backend.api.copilot_api import (
    router as copilot_router,
)

from backend.api.multi_agent_api import (
    router as multi_agent_router,
)


# ---------------------------------------------------------
# Alerts
# ---------------------------------------------------------

from backend.api.alert_api import (
    router as alert_router,
)


# ---------------------------------------------------------
# Tasks / Cache
# ---------------------------------------------------------

from backend.api.cache_api import (
    router as cache_router,
)

from backend.api.task_api import (
    router as task_router,
)


# =========================================================
# MONITORING
# =========================================================

from backend.monitoring.monitor_api import (
    router as monitor_router,
)


# =========================================================
# APPLICATION LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    """

    # =====================================================
    # STARTUP
    # =====================================================

    print()
    print("=" * 70)
    print("Enterprise AI Platform Starting...")
    print("=" * 70)

    print("Database       : PostgreSQL")
    print("ORM            : SQLAlchemy 2.x")
    print("Migrations     : Alembic")
    print("Decision Engine: Enabled")
    print("AI Services    : Enabled")
    print("RAG / Copilot  : Enabled")
    print("Multi-Agent    : Enabled")
    print("Alerts         : Enabled")
    print("Monitoring     : Enabled")
    print("Authentication : Enabled")

    print("=" * 70)
    print()

    # Application is now ready
    yield

    # =====================================================
    # SHUTDOWN
    # =====================================================

    print()
    print("=" * 70)
    print("Enterprise AI Platform Shutting Down...")
    print("=" * 70)
    print()


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title=(
        "Enterprise AI Business "
        "Decision Intelligence Platform"
    ),
    version="1.0.0",
    description=(
        "Enterprise AI platform for:\n\n"
        "- Sales Prediction\n"
        "- Demand Forecasting\n"
        "- Inventory Intelligence\n"
        "- Customer Segmentation\n"
        "- Executive Decision Support\n"
        "- AI Copilot\n"
        "- Multi Agent Business Intelligence\n"
        "- Decision Intelligence\n"
        "- Business Risk Assessment\n"
        "- Business Alerts\n"
        "- Recommendation Engine\n"
        "- Enterprise Reporting\n"
        "- Knowledge Base / RAG\n"
        "- AI Model Monitoring"
    ),
    lifespan=lifespan,
)


# =========================================================
# CORS CONFIGURATION
# =========================================================
#
# React/Vite development:
#
# http://localhost:5173
# http://127.0.0.1:5173
#
# Vite preview:
#
# http://localhost:4173
# http://127.0.0.1:4173
#
# =========================================================

ALLOWED_ORIGINS = [
    # Vite development server
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    # Vite production preview
    "http://localhost:4173",
    "http://127.0.0.1:4173",

    # Dockerized nginx frontend (default compose mapping)
    "http://localhost:3000",
    "http://127.0.0.1:3000",

    # Configured frontend URL (.env FRONTEND_URL — covers any
    # deployment origin that isn't one of the defaults above)
    settings.FRONTEND_URL,
]

# De-duplicate while preserving order.
ALLOWED_ORIGINS = list(dict.fromkeys(ALLOWED_ORIGINS))


app.add_middleware(
    CORSMiddleware,

    allow_origins=ALLOWED_ORIGINS,

    allow_credentials=True,

    allow_methods=[
        "*",
    ],

    allow_headers=[
        "*",
    ],
)


# =========================================================
# ROUTERS
# =========================================================

routers = [

    # -----------------------------------------------------
    # Authentication
    # -----------------------------------------------------

    auth_router,

    # -----------------------------------------------------
    # AI Prediction Modules
    # -----------------------------------------------------

    sales_router,
    inventory_router,
    forecast_router,
    customer_router,

    # -----------------------------------------------------
    # Business Intelligence
    # -----------------------------------------------------

    dashboard_router,
    reports_router,

    # -----------------------------------------------------
    # Decision Intelligence
    # -----------------------------------------------------

    decision_router,
    recommendation_router,

    # -----------------------------------------------------
    # AI / Copilot
    # -----------------------------------------------------

    copilot_router,
    multi_agent_router,

    # -----------------------------------------------------
    # Alerts / Monitoring
    # -----------------------------------------------------

    alert_router,
    monitor_router,

    # -----------------------------------------------------
    # Tasks / Cache
    # -----------------------------------------------------

    task_router,
    cache_router,
]


# =========================================================
# REGISTER ROUTERS
# =========================================================

for router in routers:
    app.include_router(router)


# =========================================================
# ROOT ENDPOINT
# =========================================================

@app.get(
    "/",
    tags=["System"],
)
def home():
    """
    Basic API information.
    """

    return {
        "application": (
            "Enterprise AI Business "
            "Decision Intelligence Platform"
        ),

        "status": "Running",

        "version": "1.0.0",

        "backend": "FastAPI",

        "database": "PostgreSQL",

        "orm": "SQLAlchemy 2.x",

        "migration": "Alembic",

        "modules": {

            "sales_prediction": True,

            "inventory_prediction": True,

            "demand_forecasting": True,

            "customer_segmentation": True,

            "decision_engine": True,

            "recommendation_engine": True,

            "ai_copilot": True,

            "multi_agent": True,

            "alerts": True,

            "monitoring": True,

            "reports": True,

            "cache": True,

            "tasks": True,

            "authentication": True,

            "rag": True,
        },
    }


# =========================================================
# APPLICATION HEALTH CHECK
# =========================================================

@app.get(
    "/health",
    tags=["System"],
)
def health():
    """
    Application health endpoint.
    """

    return {
        "status": "Healthy",

        "application": (
            "Enterprise AI Business "
            "Decision Intelligence Platform"
        ),

        "backend": "FastAPI",

        "database": "PostgreSQL",

        "orm": "SQLAlchemy 2.x",

        "migration": "Alembic",

        "services": {

            "sales": "Available",

            "inventory": "Available",

            "forecast": "Available",

            "customer": "Available",

            "decision_engine": "Available",

            "recommendation_engine": "Available",

            "copilot": "Available",

            "multi_agent": "Available",

            "alerts": "Available",

            "monitoring": "Available",

            "reports": "Available",

            "cache": "Available",

            "tasks": "Available",

            "authentication": "Available",
        },
    }


# =========================================================
# API INFORMATION
# =========================================================

@app.get(
    "/api/info",
    tags=["System"],
)
def api_info():
    """
    Returns registered API modules.
    """

    return {
        "name": (
            "Enterprise AI Business "
            "Decision Intelligence Platform"
        ),

        "version": "1.0.0",

        "api": "FastAPI",

        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },

        "routers": [

            "authentication",

            "sales",

            "inventory",

            "forecast",

            "customer",

            "dashboard",

            "reports",

            "decision",

            "recommendation",

            "copilot",

            "multi_agent",

            "alerts",

            "monitoring",

            "tasks",

            "cache",
        ],
    }


# =========================================================
# ALERT SYSTEM HEALTH
# =========================================================
#
# This endpoint checks whether the AlertService can
# communicate with PostgreSQL and read the alerts table.
#
# GET /alerts/health
#
# This endpoint is already provided by alert_api.py.
#
# Therefore we intentionally DO NOT duplicate it here.
#
# =========================================================


# =========================================================
# APPLICATION ENTRY POINT
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.main:app",

        host="127.0.0.1",

        port=8000,

        reload=True,
    )
