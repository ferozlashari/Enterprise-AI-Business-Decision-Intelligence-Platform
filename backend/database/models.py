
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Database Models

Author : Feroz Ali

Database Tables
---------------
1.  users
2.  sales_predictions
3.  inventory_predictions
4.  customer_segments
5.  demand_forecasts
6.  decisions
7.  decision_history
8.  recommendations
9.  alerts
10. reports
11. copilot_conversations
12. copilot_messages
13. ai_tasks
14. cache_entries
15. model_runs
16. model_metrics
17. audit_logs
18. knowledge_documents
19. knowledge_chunks
20. system_settings

Design
------
- SQLAlchemy 2.x typed ORM
- PostgreSQL compatible
- Alembic compatible
- Explicit relationships
- Proper foreign-key ownership
- Safe cascade behavior
- UTC timestamps
- PostgreSQL JSON support
- Decision -> History -> Recommendation architecture
=========================================================
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.database.database import Base


# =========================================================
# COMMON TIMESTAMP HELPER
# =========================================================

def utc_now() -> datetime:
    """
    Return a timezone-aware UTC datetime.

    PostgreSQL stores this correctly when used with:

        DateTime(timezone=True)
    """
    return datetime.now(timezone.utc)


# =========================================================
# USER
# =========================================================

class User(Base):
    """
    Application user.

    Used for:
    - Authentication
    - Authorization
    - Copilot ownership
    - Audit logging
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        default="analyst",
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # -----------------------------------------------------
    # Relationships
    # -----------------------------------------------------

    copilot_conversations: Mapped[list["CopilotConversation"]] = relationship(
        "CopilotConversation",
        back_populates="user",
        passive_deletes=True,
    )

    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            "<User("
            f"id={self.id}, "
            f"username='{self.username}', "
            f"role='{self.role}', "
            f"is_active={self.is_active}"
            ")>"
        )


# =========================================================
# SALES PREDICTIONS
# =========================================================

class SalesPrediction(Base):
    """
    Stores sales prediction results.
    """

    __tablename__ = "sales_predictions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    store_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    prediction_value: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    prediction_period: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    model_version: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    confidence_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    input_data: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            "<SalesPrediction("
            f"id={self.id}, "
            f"store_id='{self.store_id}', "
            f"prediction_value={self.prediction_value}"
            ")>"
        )


# =========================================================
# INVENTORY PREDICTIONS
# =========================================================

class InventoryPrediction(Base):
    """
    Stores inventory demand and stock recommendations.
    """

    __tablename__ = "inventory_predictions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    product_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    store_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    current_stock: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    predicted_demand: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    recommended_stock: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    safety_stock: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    reorder_point: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    economic_order_quantity: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    risk_level: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    model_version: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            "<InventoryPrediction("
            f"id={self.id}, "
            f"product_id='{self.product_id}', "
            f"store_id='{self.store_id}', "
            f"risk_level='{self.risk_level}'"
            ")>"
        )


# =========================================================
# CUSTOMER SEGMENTS
# =========================================================

class CustomerSegment(Base):
    """
    Stores customer segmentation and customer-value results.
    """

    __tablename__ = "customer_segments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    customer_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    segment: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    recency: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    frequency: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    monetary_value: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    churn_probability: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    customer_value: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    model_version: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            "<CustomerSegment("
            f"id={self.id}, "
            f"customer_id='{self.customer_id}', "
            f"segment='{self.segment}'"
            ")>"
        )


# =========================================================
# DEMAND FORECASTS
# =========================================================

class DemandForecast(Base):
    """
    Stores product/store demand forecasts.
    """

    __tablename__ = "demand_forecasts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    product_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    store_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    forecast_period: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    predicted_demand: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    forecast_growth: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    lower_bound: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    upper_bound: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    model_version: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            "<DemandForecast("
            f"id={self.id}, "
            f"product_id='{self.product_id}', "
            f"store_id='{self.store_id}', "
            f"forecast_period='{self.forecast_period}'"
            ")>"
        )


# =========================================================
# DECISIONS
# =========================================================

class Decision(Base):
    """
    Central business decision entity.

    Architecture:

        Decision
           |
           +---- DecisionHistory
           |
           +---- Recommendation

    decision_id is a public/business identifier and is
    intentionally UNIQUE because child records reference it.
    """

    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    decision_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    decision_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="BUSINESS",
        index=True,
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="ACTIVE",
        index=True,
    )

    risk_level: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="LOW",
        index=True,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    decision: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    identified_risks: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    recommendations: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    insights: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    input_data: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    output_data: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    # -----------------------------------------------------
    # Relationships
    # -----------------------------------------------------

    history: Mapped[list["DecisionHistory"]] = relationship(
        "DecisionHistory",
        back_populates="decision",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="DecisionHistory.created_at.desc()",
    )

    recommendation_items: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="decision",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Recommendation.created_at.desc()",
    )

    def __repr__(self) -> str:
        return (
            "<Decision("
            f"id={self.id}, "
            f"decision_id='{self.decision_id}', "
            f"risk_level='{self.risk_level}', "
            f"risk_score={self.risk_score}"
            ")>"
        )


# =========================================================
# DECISION HISTORY
# =========================================================

class DecisionHistory(Base):
    """
    Historical snapshot of a business decision.

    IMPORTANT:
    decision_id references decisions.decision_id.

    It does NOT reference another decision_history row.

    This allows multiple history records to exist for the
    same decision.
    """

    __tablename__ = "decision_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    decision_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey(
            "decisions.decision_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    risk_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="LOW",
        index=True,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    risk_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    predicted_sales: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    inventory: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    forecast_growth: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    customer_churn: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    revenue: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    profit: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    profit_margin: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    customers: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    identified_risks: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    recommendations: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    insights: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    health_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Healthy",
    )

    business_health: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    # -----------------------------------------------------
    # Relationship
    # -----------------------------------------------------

    decision: Mapped["Decision"] = relationship(
        "Decision",
        back_populates="history",
    )

    def __repr__(self) -> str:
        return (
            "<DecisionHistory("
            f"id={self.id}, "
            f"decision_id='{self.decision_id}', "
            f"risk_level='{self.risk_level}', "
            f"risk_score={self.risk_score}"
            ")>"
        )


# =========================================================
# RECOMMENDATIONS
# =========================================================

class Recommendation(Base):
    """
    Business recommendation belonging to a Decision.

    IMPORTANT:
    Recommendation references Decision directly.

    It does NOT reference DecisionHistory because history is
    a time-series/audit structure.
    """

    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    decision_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey(
            "decisions.decision_id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    recommendation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="MEDIUM",
        index=True,
    )

    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    expected_impact: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    # -----------------------------------------------------
    # Relationship
    # -----------------------------------------------------

    decision: Mapped[Optional["Decision"]] = relationship(
        "Decision",
        back_populates="recommendation_items",
    )

    def __repr__(self) -> str:
        return (
            "<Recommendation("
            f"id={self.id}, "
            f"decision_id='{self.decision_id}', "
            f"priority='{self.priority}', "
            f"status='{self.status}'"
            ")>"
        )


# =========================================================
# ALERTS
# =========================================================

class Alert(Base):
    """
    Enterprise alert.

    The database column remains named "metadata", while the
    Python attribute is metadata_json because SQLAlchemy's
    declarative Base already uses the metadata attribute.
    """

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    alert_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    severity: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="MEDIUM",
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    module: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    entity_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    is_resolved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            "<Alert("
            f"id={self.id}, "
            f"alert_type='{self.alert_type}', "
            f"severity='{self.severity}', "
            f"is_resolved={self.is_resolved}"
            ")>"
        )


# =========================================================
# REPORTS
# =========================================================

class Report(Base):
    """
    Generated enterprise reports.
    """

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    report_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    report_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    generated_by: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="COMPLETED",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            "<Report("
            f"id={self.id}, "
            f"report_type='{self.report_type}', "
            f"status='{self.status}'"
            ")>"
        )


# =========================================================
# COPILOT CONVERSATIONS
# =========================================================

class CopilotConversation(Base):
    """
    AI Copilot conversation owned by a user.
    """

    __tablename__ = "copilot_conversations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="ACTIVE",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    # -----------------------------------------------------
    # Relationships
    # -----------------------------------------------------

    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="copilot_conversations",
    )

    messages: Mapped[list["CopilotMessage"]] = relationship(
        "CopilotMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="CopilotMessage.created_at.asc()",
    )

    def __repr__(self) -> str:
        return (
            "<CopilotConversation("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"status='{self.status}'"
            ")>"
        )


# =========================================================
# COPILOT MESSAGES
# =========================================================

class CopilotMessage(Base):
    """
    Individual message inside an AI Copilot conversation.
    """

    __tablename__ = "copilot_messages"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    conversation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "copilot_conversations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    model: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    conversation: Mapped["CopilotConversation"] = relationship(
        "CopilotConversation",
        back_populates="messages",
    )

    def __repr__(self) -> str:
        return (
            "<CopilotMessage("
            f"id={self.id}, "
            f"conversation_id={self.conversation_id}, "
            f"role='{self.role}'"
            ")>"
        )


# =========================================================
# AI TASKS / CELERY TASKS
# =========================================================

class AITask(Base):
    """
    Tracks background AI/Celery tasks.
    """

    __tablename__ = "ai_tasks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    task_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    task_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",
        index=True,
    )

    input_data: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    result: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            "<AITask("
            f"id={self.id}, "
            f"task_id='{self.task_id}', "
            f"status='{self.status}'"
            ")>"
        )


# =========================================================
# CACHE
# =========================================================

class CacheEntry(Base):
    """
    Database-backed cache entry.

    Redis remains the preferred high-performance cache.
    This table can be used for persistent/application-level
    cache records.
    """

    __tablename__ = "cache_entries"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    cache_key: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
        index=True,
    )

    value: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            "<CacheEntry("
            f"id={self.id}, "
            f"cache_key='{self.cache_key}', "
            f"expires_at={self.expires_at}"
            ")>"
        )


# =========================================================
# MODEL RUNS
# =========================================================

class ModelRun(Base):
    """
    Tracks execution of ML/AI models.
    """

    __tablename__ = "model_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    model_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    model_version: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="SUCCESS",
        index=True,
    )

    execution_time: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    input_records: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    output_records: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    result_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            "<ModelRun("
            f"id={self.id}, "
            f"model_name='{self.model_name}', "
            f"model_version='{self.model_version}', "
            f"status='{self.status}'"
            ")>"
        )


# =========================================================
# MODEL METRICS
# =========================================================

class ModelMetric(Base):
    """
    Stores ML model evaluation metrics.

    Examples:
    - MAE
    - MSE
    - RMSE
    - R2
    - Accuracy
    - Precision
    - Recall
    - F1
    """

    __tablename__ = "model_metrics"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    model_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    model_version: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    metric_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    metric_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    dataset_name: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    __table_args__ = (
        Index(
            "ix_model_metrics_model_metric",
            "model_name",
            "metric_name",
        ),
    )

    def __repr__(self) -> str:
        return (
            "<ModelMetric("
            f"id={self.id}, "
            f"model_name='{self.model_name}', "
            f"metric_name='{self.metric_name}', "
            f"metric_value={self.metric_value}"
            ")>"
        )


# =========================================================
# AUDIT LOGS
# =========================================================

class AuditLog(Base):
    """
    Security and application audit log.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    module: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    endpoint: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    method: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    status_code: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    details: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="audit_logs",
    )

    def __repr__(self) -> str:
        return (
            "<AuditLog("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"action='{self.action}', "
            f"module='{self.module}'"
            ")>"
        )


# =========================================================
# KNOWLEDGE DOCUMENTS
# =========================================================

class KnowledgeDocument(Base):
    """
    RAG knowledge-base document.

    One document can contain many chunks.
    """

    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    document_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    filename: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    source: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        index=True,
    )

    document_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )

    chunk_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    # -----------------------------------------------------
    # Relationship
    # -----------------------------------------------------

    chunks: Mapped[list["KnowledgeChunk"]] = relationship(
        "KnowledgeChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="KnowledgeChunk.chunk_index.asc()",
    )

    def __repr__(self) -> str:
        return (
            "<KnowledgeDocument("
            f"id={self.id}, "
            f"document_id='{self.document_id}', "
            f"filename='{self.filename}'"
            ")>"
        )


# =========================================================
# KNOWLEDGE CHUNKS
# =========================================================

class KnowledgeChunk(Base):
    """
    Individual RAG document chunk.

    Each document cannot have two chunks with the same
    chunk_index.
    """

    __tablename__ = "knowledge_chunks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "knowledge_documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )

    vector_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    document: Mapped["KnowledgeDocument"] = relationship(
        "KnowledgeDocument",
        back_populates="chunks",
    )

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_knowledge_chunk_document_index",
        ),
    )

    def __repr__(self) -> str:
        return (
            "<KnowledgeChunk("
            f"id={self.id}, "
            f"document_id={self.document_id}, "
            f"chunk_index={self.chunk_index}"
            ")>"
        )


# =========================================================
# SYSTEM SETTINGS
# =========================================================

class SystemSetting(Base):
    """
    Application/system configuration.

    Secrets should preferably remain in environment variables
    or a dedicated secret manager. is_secret is only a marker
    for application behavior.
    """

    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    setting_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    setting_value: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    is_secret: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            "<SystemSetting("
            f"id={self.id}, "
            f"setting_key='{self.setting_key}', "
            f"is_secret={self.is_secret}"
            ")>"
        )


# =========================================================
# CENTRAL EXPORTS
# =========================================================

__all__ = [
    "User",
    "SalesPrediction",
    "InventoryPrediction",
    "CustomerSegment",
    "DemandForecast",
    "Decision",
    "DecisionHistory",
    "Recommendation",
    "Alert",
    "Report",
    "CopilotConversation",
    "CopilotMessage",
    "AITask",
    "CacheEntry",
    "ModelRun",
    "ModelMetric",
    "AuditLog",
    "KnowledgeDocument",
    "KnowledgeChunk",
    "SystemSetting",
]

