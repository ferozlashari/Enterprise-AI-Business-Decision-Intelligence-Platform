
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Database Schemas

Author : Feroz Ali
=========================================================
"""

from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, EmailStr


# =========================================================
# USER SCHEMAS
# =========================================================


class UserCreate(BaseModel):

    username: str
    email: EmailStr
    password: str
    role: str = "Analyst"


class UserLogin(BaseModel):

    username: str
    password: str


class UserResponse(BaseModel):

    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# =========================================================
# PASSWORD RESET SCHEMAS
# =========================================================


class ForgotPasswordRequest(BaseModel):
    """
    Frontend sends:

    {
        "email": "user@example.com"
    }
    """

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """
    Frontend sends:

    {
        "token": "...",
        "password": "..."
    }
    """

    token: str
    password: str


class ChangePasswordRequest(BaseModel):
    """
    Frontend sends (authenticated user changing their own
    password — requires proof of the current password):

    {
        "current_password": "...",
        "new_password": "..."
    }
    """

    current_password: str
    new_password: str


# =========================================================
# SALES PREDICTION SCHEMAS
# =========================================================


class SalesPredictionCreate(BaseModel):

    store_id: str
    prediction_value: float
    model_version: str


class SalesPredictionResponse(BaseModel):

    id: int
    store_id: str
    prediction_value: float
    model_version: str
    created_at: datetime

    class Config:
        from_attributes = True


# =========================================================
# INVENTORY PREDICTION SCHEMAS
# =========================================================


class InventoryPredictionCreate(BaseModel):

    product_id: str
    current_stock: int
    recommended_stock: int
    risk_level: str


class InventoryPredictionResponse(BaseModel):

    id: int
    product_id: str
    current_stock: int
    recommended_stock: int
    risk_level: str
    created_at: datetime

    class Config:
        from_attributes = True


# =========================================================
# REPORT SCHEMAS
# =========================================================


class ReportCreate(BaseModel):

    report_type: str
    title: str
    content: str

    metadata: Optional[
        Dict[str, Any]
    ] = None


class ReportResponse(BaseModel):

    id: int
    report_type: str
    title: str
    content: str
    report_metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

