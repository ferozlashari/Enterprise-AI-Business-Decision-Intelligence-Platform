
"""
sync enterprise database schema

Revision ID: 61a6b1f5cc1e
Revises: fb3dbe0a2e85
Create Date: 2026-08-10 20:27:36.296559

Enterprise AI Business Decision Intelligence Platform
Database Schema Synchronization

IMPORTANT:
This migration is written to safely upgrade an existing database
containing data.

New NOT NULL columns are added as nullable first, existing rows
are backfilled, and only then are the columns changed to NOT NULL.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# ============================================================
# REVISION IDENTIFIERS
# ============================================================

revision: str = "61a6b1f5cc1e"

down_revision: Union[str, Sequence[str], None] = "fb3dbe0a2e85"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


# ============================================================
# UPGRADE
# ============================================================

def upgrade() -> None:
    """
    Upgrade database schema.

    This migration is intentionally written to be safe against
    existing rows in tables being modified.
    """

    # ========================================================
    # AI TASKS
    # ========================================================

    op.create_table(
        "ai_tasks",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "task_id",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "task_type",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "input_data",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "result",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_ai_tasks_created_at"),
        "ai_tasks",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_ai_tasks_id"),
        "ai_tasks",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_ai_tasks_status"),
        "ai_tasks",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_ai_tasks_task_id"),
        "ai_tasks",
        ["task_id"],
        unique=True,
    )

    op.create_index(
        op.f("ix_ai_tasks_task_type"),
        "ai_tasks",
        ["task_type"],
        unique=False,
    )

    # ========================================================
    # ALERTS
    # ========================================================

    op.create_table(
        "alerts",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "alert_type",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "severity",
            sa.String(length=30),
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "message",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "module",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "entity_id",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=False,
        ),

        sa.Column(
            "is_resolved",
            sa.Boolean(),
            nullable=False,
        ),

        sa.Column(
            "metadata",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_alerts_alert_type"),
        "alerts",
        ["alert_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_alerts_created_at"),
        "alerts",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_alerts_id"),
        "alerts",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_alerts_is_read"),
        "alerts",
        ["is_read"],
        unique=False,
    )

    op.create_index(
        op.f("ix_alerts_is_resolved"),
        "alerts",
        ["is_resolved"],
        unique=False,
    )

    op.create_index(
        op.f("ix_alerts_severity"),
        "alerts",
        ["severity"],
        unique=False,
    )

    # ========================================================
    # CACHE ENTRIES
    # ========================================================

    op.create_table(
        "cache_entries",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "cache_key",
            sa.String(length=500),
            nullable=False,
        ),

        sa.Column(
            "value",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_cache_entries_cache_key"),
        "cache_entries",
        ["cache_key"],
        unique=True,
    )

    op.create_index(
        op.f("ix_cache_entries_expires_at"),
        "cache_entries",
        ["expires_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_cache_entries_id"),
        "cache_entries",
        ["id"],
        unique=False,
    )

    # ========================================================
    # CUSTOMER SEGMENTS
    # ========================================================

    op.create_table(
        "customer_segments",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "customer_id",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "segment",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "recency",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "frequency",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "monetary_value",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "churn_probability",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "customer_value",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "model_version",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_customer_segments_created_at"),
        "customer_segments",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_customer_segments_customer_id"),
        "customer_segments",
        ["customer_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_customer_segments_id"),
        "customer_segments",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_customer_segments_segment"),
        "customer_segments",
        ["segment"],
        unique=False,
    )

    # ========================================================
    # DECISIONS
    # ========================================================

    op.create_table(
        "decisions",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "decision_id",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "decision_type",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "risk_level",
            sa.String(length=30),
            nullable=False,
        ),

        sa.Column(
            "risk_score",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "summary",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "decision",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "identified_risks",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "recommendations",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "insights",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "input_data",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "output_data",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_decisions_created_at"),
        "decisions",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_decisions_decision_id"),
        "decisions",
        ["decision_id"],
        unique=True,
    )

    op.create_index(
        op.f("ix_decisions_decision_type"),
        "decisions",
        ["decision_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_decisions_id"),
        "decisions",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_decisions_risk_level"),
        "decisions",
        ["risk_level"],
        unique=False,
    )

    op.create_index(
        op.f("ix_decisions_status"),
        "decisions",
        ["status"],
        unique=False,
    )

    # ========================================================
    # DEMAND FORECASTS
    # ========================================================

    op.create_table(
        "demand_forecasts",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "product_id",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "store_id",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "forecast_period",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "predicted_demand",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "forecast_growth",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "lower_bound",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "upper_bound",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "model_version",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_demand_forecasts_created_at"),
        "demand_forecasts",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_demand_forecasts_id"),
        "demand_forecasts",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_demand_forecasts_product_id"),
        "demand_forecasts",
        ["product_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_demand_forecasts_store_id"),
        "demand_forecasts",
        ["store_id"],
        unique=False,
    )

    # ========================================================
    # KNOWLEDGE DOCUMENTS
    # ========================================================

    op.create_table(
        "knowledge_documents",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "document_id",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "filename",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "source",
            sa.String(length=500),
            nullable=True,
        ),

        sa.Column(
            "document_type",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "content",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "metadata",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "chunk_count",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_knowledge_documents_created_at"),
        "knowledge_documents",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_knowledge_documents_document_id"),
        "knowledge_documents",
        ["document_id"],
        unique=True,
    )

    op.create_index(
        op.f("ix_knowledge_documents_id"),
        "knowledge_documents",
        ["id"],
        unique=False,
    )

    # ========================================================
    # MODEL METRICS
    # ========================================================

    op.create_table(
        "model_metrics",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "model_name",
            sa.String(length=150),
            nullable=False,
        ),

        sa.Column(
            "model_version",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "metric_name",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "metric_value",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "dataset_name",
            sa.String(length=150),
            nullable=True,
        ),

        sa.Column(
            "metadata",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_model_metrics_created_at"),
        "model_metrics",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_model_metrics_id"),
        "model_metrics",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_model_metrics_model_name"),
        "model_metrics",
        ["model_name"],
        unique=False,
    )

    # ========================================================
    # MODEL RUNS
    # ========================================================

    op.create_table(
        "model_runs",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "model_name",
            sa.String(length=150),
            nullable=False,
        ),

        sa.Column(
            "model_version",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "execution_time",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "input_records",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "output_records",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "result_metadata",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_model_runs_created_at"),
        "model_runs",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_model_runs_id"),
        "model_runs",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_model_runs_model_name"),
        "model_runs",
        ["model_name"],
        unique=False,
    )

    op.create_index(
        op.f("ix_model_runs_status"),
        "model_runs",
        ["status"],
        unique=False,
    )

    # ========================================================
    # SYSTEM SETTINGS
    # ========================================================

    op.create_table(
        "system_settings",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "setting_key",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "setting_value",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "is_secret",
            sa.Boolean(),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_system_settings_id"),
        "system_settings",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_system_settings_setting_key"),
        "system_settings",
        ["setting_key"],
        unique=True,
    )

    # ========================================================
    # AUDIT LOGS
    # ========================================================

    op.create_table(
        "audit_logs",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "action",
            sa.String(length=150),
            nullable=False,
        ),

        sa.Column(
            "module",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "endpoint",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "method",
            sa.String(length=20),
            nullable=True,
        ),

        sa.Column(
            "status_code",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "details",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "ip_address",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_audit_logs_action"),
        "audit_logs",
        ["action"],
        unique=False,
    )

    op.create_index(
        op.f("ix_audit_logs_created_at"),
        "audit_logs",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_audit_logs_id"),
        "audit_logs",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_audit_logs_user_id"),
        "audit_logs",
        ["user_id"],
        unique=False,
    )

    # ========================================================
    # COPILOT CONVERSATIONS
    # ========================================================

    op.create_table(
        "copilot_conversations",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "title",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_copilot_conversations_id"),
        "copilot_conversations",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_copilot_conversations_user_id"),
        "copilot_conversations",
        ["user_id"],
        unique=False,
    )

    # ========================================================
    # KNOWLEDGE CHUNKS
    # ========================================================

    op.create_table(
        "knowledge_chunks",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "document_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "chunk_index",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "metadata",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "vector_id",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["document_id"],
            ["knowledge_documents.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_knowledge_chunks_document_id"),
        "knowledge_chunks",
        ["document_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_knowledge_chunks_id"),
        "knowledge_chunks",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_knowledge_chunks_vector_id"),
        "knowledge_chunks",
        ["vector_id"],
        unique=False,
    )

    # ========================================================
    # RECOMMENDATIONS
    #
    # IMPORTANT:
    # decision_id now references decisions.decision_id.
    # decisions.decision_id has a UNIQUE index above.
    # ========================================================

    op.create_table(
        "recommendations",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "decision_id",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "title",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "recommendation",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "priority",
            sa.String(length=30),
            nullable=False,
        ),

        sa.Column(
            "category",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "expected_impact",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["decisions.decision_id"],
            ondelete="SET NULL",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_recommendations_created_at"),
        "recommendations",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_recommendations_decision_id"),
        "recommendations",
        ["decision_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_recommendations_id"),
        "recommendations",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_recommendations_priority"),
        "recommendations",
        ["priority"],
        unique=False,
    )

    op.create_index(
        op.f("ix_recommendations_status"),
        "recommendations",
        ["status"],
        unique=False,
    )

    # ========================================================
    # COPILOT MESSAGES
    # ========================================================

    op.create_table(
        "copilot_messages",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "conversation_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "role",
            sa.String(length=30),
            nullable=False,
        ),

        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "model",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "metadata",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["copilot_conversations.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_copilot_messages_conversation_id"),
        "copilot_messages",
        ["conversation_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_copilot_messages_created_at"),
        "copilot_messages",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_copilot_messages_id"),
        "copilot_messages",
        ["id"],
        unique=False,
    )

    # ========================================================
    # DECISION HISTORY
    #
    # EXISTING TABLE
    #
    # Do NOT directly add NOT NULL columns.
    # ========================================================

    op.add_column(
        "decision_history",
        sa.Column(
            "summary",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "decision_history",
        sa.Column(
            "health_status",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.add_column(
        "decision_history",
        sa.Column(
            "business_health",
            sa.JSON(),
            nullable=True,
        ),
    )

    # --------------------------------------------------------
    # Backfill existing decision history rows
    # --------------------------------------------------------

    op.execute(
        """
        UPDATE decision_history
        SET summary = ''
        WHERE summary IS NULL
        """
    )

    op.execute(
        """
        UPDATE decision_history
        SET health_status = 'unknown'
        WHERE health_status IS NULL
        """
    )

    # --------------------------------------------------------
    # Make required fields NOT NULL
    # --------------------------------------------------------

    op.alter_column(
        "decision_history",
        "summary",
        existing_type=sa.Text(),
        nullable=False,
    )

    op.alter_column(
        "decision_history",
        "health_status",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    # --------------------------------------------------------
    # decision_id length
    # --------------------------------------------------------

    op.alter_column(
        "decision_history",
        "decision_id",
        existing_type=sa.VARCHAR(length=50),
        type_=sa.String(length=100),
        existing_nullable=False,
    )

    op.drop_index(
        op.f("ix_decision_history_decision_id"),
        table_name="decision_history",
    )

    op.create_index(
        op.f("ix_decision_history_decision_id"),
        "decision_history",
        ["decision_id"],
        unique=False,
    )

    # ========================================================
    # INVENTORY PREDICTIONS
    # ========================================================

    op.add_column(
        "inventory_predictions",
        sa.Column(
            "store_id",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "inventory_predictions",
        sa.Column(
            "predicted_demand",
            sa.Float(),
            nullable=True,
        ),
    )

    op.add_column(
        "inventory_predictions",
        sa.Column(
            "safety_stock",
            sa.Float(),
            nullable=True,
        ),
    )

    op.add_column(
        "inventory_predictions",
        sa.Column(
            "reorder_point",
            sa.Float(),
            nullable=True,
        ),
    )

    op.add_column(
        "inventory_predictions",
        sa.Column(
            "economic_order_quantity",
            sa.Float(),
            nullable=True,
        ),
    )

    op.add_column(
        "inventory_predictions",
        sa.Column(
            "model_version",
            sa.String(length=100),
            nullable=True,
        ),
    )

    # --------------------------------------------------------
    # Backfill existing created_at values
    # --------------------------------------------------------

    op.execute(
        """
        UPDATE inventory_predictions
        SET created_at = CURRENT_TIMESTAMP
        WHERE created_at IS NULL
        """
    )

    op.alter_column(
        "inventory_predictions",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        nullable=False,
    )

    op.create_index(
        op.f("ix_inventory_predictions_created_at"),
        "inventory_predictions",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_inventory_predictions_id"),
        "inventory_predictions",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_inventory_predictions_product_id"),
        "inventory_predictions",
        ["product_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_inventory_predictions_risk_level"),
        "inventory_predictions",
        ["risk_level"],
        unique=False,
    )

    op.create_index(
        op.f("ix_inventory_predictions_store_id"),
        "inventory_predictions",
        ["store_id"],
        unique=False,
    )

    # ========================================================
    # REPORTS
    # ========================================================

    op.add_column(
        "reports",
        sa.Column(
            "generated_by",
            sa.String(length=100),
            nullable=True,
        ),
    )

    # Existing rows require a safe default.
    op.add_column(
        "reports",
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE reports
        SET status = 'completed'
        WHERE status IS NULL
        """
    )

    op.alter_column(
        "reports",
        "status",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    op.execute(
        """
        UPDATE reports
        SET created_at = CURRENT_TIMESTAMP
        WHERE created_at IS NULL
        """
    )

    op.alter_column(
        "reports",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        nullable=False,
    )

    op.create_index(
        op.f("ix_reports_created_at"),
        "reports",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_reports_id"),
        "reports",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_reports_report_type"),
        "reports",
        ["report_type"],
        unique=False,
    )

    # ========================================================
    # SALES PREDICTIONS
    # ========================================================

    op.add_column(
        "sales_predictions",
        sa.Column(
            "prediction_period",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "sales_predictions",
        sa.Column(
            "confidence_score",
            sa.Float(),
            nullable=True,
        ),
    )

    op.add_column(
        "sales_predictions",
        sa.Column(
            "input_data",
            sa.JSON(),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE sales_predictions
        SET created_at = CURRENT_TIMESTAMP
        WHERE created_at IS NULL
        """
    )

    op.alter_column(
        "sales_predictions",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        nullable=False,
    )

    op.create_index(
        op.f("ix_sales_predictions_created_at"),
        "sales_predictions",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_sales_predictions_id"),
        "sales_predictions",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_sales_predictions_store_id"),
        "sales_predictions",
        ["store_id"],
        unique=False,
    )

    # ========================================================
    # USERS
    #
    # EXISTING TABLE
    #
    # New NOT NULL columns are added nullable first.
    # ========================================================

    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "last_login",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # --------------------------------------------------------
    # Backfill existing users
    # --------------------------------------------------------

    op.execute(
        """
        UPDATE users
        SET is_active = TRUE
        WHERE is_active IS NULL
        """
    )

    # Prefer created_at for updated_at.
    op.execute(
        """
        UPDATE users
        SET updated_at = created_at
        WHERE updated_at IS NULL
          AND created_at IS NOT NULL
        """
    )

    # Final fallback.
    op.execute(
        """
        UPDATE users
        SET updated_at = CURRENT_TIMESTAMP
        WHERE updated_at IS NULL
        """
    )

    # --------------------------------------------------------
    # Make required fields NOT NULL
    # --------------------------------------------------------

    op.alter_column(
        "users",
        "is_active",
        existing_type=sa.Boolean(),
        nullable=False,
    )

    op.alter_column(
        "users",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )

    op.alter_column(
        "users",
        "role",
        existing_type=sa.VARCHAR(),
        nullable=False,
    )

    op.execute(
        """
        UPDATE users
        SET created_at = CURRENT_TIMESTAMP
        WHERE created_at IS NULL
        """
    )

    op.alter_column(
        "users",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        nullable=False,
    )

    op.create_index(
        op.f("ix_users_created_at"),
        "users",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_users_role"),
        "users",
        ["role"],
        unique=False,
    )


# ============================================================
# DOWNGRADE
# ============================================================

def downgrade() -> None:
    """
    Downgrade database schema to fb3dbe0a2e85.
    """

    # ========================================================
    # USERS
    # ========================================================

    op.drop_index(
        op.f("ix_users_role"),
        table_name="users",
    )

    op.drop_index(
        op.f("ix_users_created_at"),
        table_name="users",
    )

    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        nullable=True,
    )

    op.alter_column(
        "users",
        "role",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )

    op.drop_column(
        "users",
        "last_login",
    )

    op.drop_column(
        "users",
        "updated_at",
    )

    op.drop_column(
        "users",
        "is_active",
    )

    # ========================================================
    # SALES PREDICTIONS
    # ========================================================

    op.drop_index(
        op.f("ix_sales_predictions_store_id"),
        table_name="sales_predictions",
    )

    op.drop_index(
        op.f("ix_sales_predictions_id"),
        table_name="sales_predictions",
    )

    op.drop_index(
        op.f("ix_sales_predictions_created_at"),
        table_name="sales_predictions",
    )

    op.alter_column(
        "sales_predictions",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        nullable=True,
    )

    op.drop_column(
        "sales_predictions",
        "input_data",
    )

    op.drop_column(
        "sales_predictions",
        "confidence_score",
    )

    op.drop_column(
        "sales_predictions",
        "prediction_period",
    )

    # ========================================================
    # REPORTS
    # ========================================================

    op.drop_index(
        op.f("ix_reports_report_type"),
        table_name="reports",
    )

    op.drop_index(
        op.f("ix_reports_id"),
        table_name="reports",
    )

    op.drop_index(
        op.f("ix_reports_created_at"),
        table_name="reports",
    )

    op.alter_column(
        "reports",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        nullable=True,
    )

    op.drop_column(
        "reports",
        "status",
    )

    op.drop_column(
        "reports",
        "generated_by",
    )

    # ========================================================
    # INVENTORY PREDICTIONS
    # ========================================================

    op.drop_index(
        op.f("ix_inventory_predictions_store_id"),
        table_name="inventory_predictions",
    )

    op.drop_index(
        op.f("ix_inventory_predictions_risk_level"),
        table_name="inventory_predictions",
    )

    op.drop_index(
        op.f("ix_inventory_predictions_product_id"),
        table_name="inventory_predictions",
    )

    op.drop_index(
        op.f("ix_inventory_predictions_id"),
        table_name="inventory_predictions",
    )

    op.drop_index(
        op.f("ix_inventory_predictions_created_at"),
        table_name="inventory_predictions",
    )

    op.alter_column(
        "inventory_predictions",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        nullable=True,
    )

    op.drop_column(
        "inventory_predictions",
        "model_version",
    )

    op.drop_column(
        "inventory_predictions",
        "economic_order_quantity",
    )

    op.drop_column(
        "inventory_predictions",
        "reorder_point",
    )

    op.drop_column(
        "inventory_predictions",
        "safety_stock",
    )

    op.drop_column(
        "inventory_predictions",
        "predicted_demand",
    )

    op.drop_column(
        "inventory_predictions",
        "store_id",
    )

    # ========================================================
    # DECISION HISTORY
    # ========================================================

    op.drop_index(
        op.f("ix_decision_history_decision_id"),
        table_name="decision_history",
    )

    op.create_index(
        op.f("ix_decision_history_decision_id"),
        "decision_history",
        ["decision_id"],
        unique=True,
    )

    op.alter_column(
        "decision_history",
        "decision_id",
        existing_type=sa.String(length=100),
        type_=sa.VARCHAR(length=50),
        existing_nullable=False,
    )

    op.drop_column(
        "decision_history",
        "business_health",
    )

    op.drop_column(
        "decision_history",
        "health_status",
    )

    op.drop_column(
        "decision_history",
        "summary",
    )

    # ========================================================
    # COPILOT MESSAGES
    # ========================================================

    op.drop_index(
        op.f("ix_copilot_messages_id"),
        table_name="copilot_messages",
    )

    op.drop_index(
        op.f("ix_copilot_messages_created_at"),
        table_name="copilot_messages",
    )

    op.drop_index(
        op.f("ix_copilot_messages_conversation_id"),
        table_name="copilot_messages",
    )

    op.drop_table(
        "copilot_messages",
    )

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    op.drop_index(
        op.f("ix_recommendations_status"),
        table_name="recommendations",
    )

    op.drop_index(
        op.f("ix_recommendations_priority"),
        table_name="recommendations",
    )

    op.drop_index(
        op.f("ix_recommendations_id"),
        table_name="recommendations",
    )

    op.drop_index(
        op.f("ix_recommendations_decision_id"),
        table_name="recommendations",
    )

    op.drop_index(
        op.f("ix_recommendations_created_at"),
        table_name="recommendations",
    )

    op.drop_table(
        "recommendations",
    )

    # ========================================================
    # KNOWLEDGE CHUNKS
    # ========================================================

    op.drop_index(
        op.f("ix_knowledge_chunks_vector_id"),
        table_name="knowledge_chunks",
    )

    op.drop_index(
        op.f("ix_knowledge_chunks_id"),
        table_name="knowledge_chunks",
    )

    op.drop_index(
        op.f("ix_knowledge_chunks_document_id"),
        table_name="knowledge_chunks",
    )

    op.drop_table(
        "knowledge_chunks",
    )

    # ========================================================
    # COPILOT CONVERSATIONS
    # ========================================================

    op.drop_index(
        op.f("ix_copilot_conversations_user_id"),
        table_name="copilot_conversations",
    )

    op.drop_index(
        op.f("ix_copilot_conversations_id"),
        table_name="copilot_conversations",
    )

    op.drop_table(
        "copilot_conversations",
    )

    # ========================================================
    # AUDIT LOGS
    # ========================================================

    op.drop_index(
        op.f("ix_audit_logs_user_id"),
        table_name="audit_logs",
    )

    op.drop_index(
        op.f("ix_audit_logs_id"),
        table_name="audit_logs",
    )

    op.drop_index(
        op.f("ix_audit_logs_created_at"),
        table_name="audit_logs",
    )

    op.drop_index(
        op.f("ix_audit_logs_action"),
        table_name="audit_logs",
    )

    op.drop_table(
        "audit_logs",
    )

    # ========================================================
    # SYSTEM SETTINGS
    # ========================================================

    op.drop_index(
        op.f("ix_system_settings_setting_key"),
        table_name="system_settings",
    )

    op.drop_index(
        op.f("ix_system_settings_id"),
        table_name="system_settings",
    )

    op.drop_table(
        "system_settings",
    )

    # ========================================================
    # MODEL RUNS
    # ========================================================

    op.drop_index(
        op.f("ix_model_runs_status"),
        table_name="model_runs",
    )

    op.drop_index(
        op.f("ix_model_runs_model_name"),
        table_name="model_runs",
    )

    op.drop_index(
        op.f("ix_model_runs_id"),
        table_name="model_runs",
    )

    op.drop_index(
        op.f("ix_model_runs_created_at"),
        table_name="model_runs",
    )

    op.drop_table(
        "model_runs",
    )

    # ========================================================
    # MODEL METRICS
    # ========================================================

    op.drop_index(
        op.f("ix_model_metrics_model_name"),
        table_name="model_metrics",
    )

    op.drop_index(
        op.f("ix_model_metrics_id"),
        table_name="model_metrics",
    )

    op.drop_index(
        op.f("ix_model_metrics_created_at"),
        table_name="model_metrics",
    )

    op.drop_table(
        "model_metrics",
    )

    # ========================================================
    # KNOWLEDGE DOCUMENTS
    # ========================================================

    op.drop_index(
        op.f("ix_knowledge_documents_id"),
        table_name="knowledge_documents",
    )

    op.drop_index(
        op.f("ix_knowledge_documents_document_id"),
        table_name="knowledge_documents",
    )

    op.drop_index(
        op.f("ix_knowledge_documents_created_at"),
        table_name="knowledge_documents",
    )

    op.drop_table(
        "knowledge_documents",
    )

    # ========================================================
    # DEMAND FORECASTS
    # ========================================================

    op.drop_index(
        op.f("ix_demand_forecasts_store_id"),
        table_name="demand_forecasts",
    )

    op.drop_index(
        op.f("ix_demand_forecasts_product_id"),
        table_name="demand_forecasts",
    )

    op.drop_index(
        op.f("ix_demand_forecasts_id"),
        table_name="demand_forecasts",
    )

    op.drop_index(
        op.f("ix_demand_forecasts_created_at"),
        table_name="demand_forecasts",
    )

    op.drop_table(
        "demand_forecasts",
    )

    # ========================================================
    # DECISIONS
    # ========================================================

    op.drop_index(
        op.f("ix_decisions_status"),
        table_name="decisions",
    )

    op.drop_index(
        op.f("ix_decisions_risk_level"),
        table_name="decisions",
    )

    op.drop_index(
        op.f("ix_decisions_id"),
        table_name="decisions",
    )

    op.drop_index(
        op.f("ix_decisions_decision_type"),
        table_name="decisions",
    )

    op.drop_index(
        op.f("ix_decisions_decision_id"),
        table_name="decisions",
    )

    op.drop_index(
        op.f("ix_decisions_created_at"),
        table_name="decisions",
    )

    op.drop_table(
        "decisions",
    )

    # ========================================================
    # CUSTOMER SEGMENTS
    # ========================================================

    op.drop_index(
        op.f("ix_customer_segments_segment"),
        table_name="customer_segments",
    )

    op.drop_index(
        op.f("ix_customer_segments_id"),
        table_name="customer_segments",
    )

    op.drop_index(
        op.f("ix_customer_segments_customer_id"),
        table_name="customer_segments",
    )

    op.drop_index(
        op.f("ix_customer_segments_created_at"),
        table_name="customer_segments",
    )

    op.drop_table(
        "customer_segments",
    )

    # ========================================================
    # CACHE ENTRIES
    # ========================================================

    op.drop_index(
        op.f("ix_cache_entries_id"),
        table_name="cache_entries",
    )

    op.drop_index(
        op.f("ix_cache_entries_expires_at"),
        table_name="cache_entries",
    )

    op.drop_index(
        op.f("ix_cache_entries_cache_key"),
        table_name="cache_entries",
    )

    op.drop_table(
        "cache_entries",
    )

    # ========================================================
    # ALERTS
    # ========================================================

    op.drop_index(
        op.f("ix_alerts_severity"),
        table_name="alerts",
    )

    op.drop_index(
        op.f("ix_alerts_is_resolved"),
        table_name="alerts",
    )

    op.drop_index(
        op.f("ix_alerts_is_read"),
        table_name="alerts",
    )

    op.drop_index(
        op.f("ix_alerts_id"),
        table_name="alerts",
    )

    op.drop_index(
        op.f("ix_alerts_created_at"),
        table_name="alerts",
    )

    op.drop_index(
        op.f("ix_alerts_alert_type"),
        table_name="alerts",
    )

    op.drop_table(
        "alerts",
    )

    # ========================================================
    # AI TASKS
    # ========================================================

    op.drop_index(
        op.f("ix_ai_tasks_task_type"),
        table_name="ai_tasks",
    )

    op.drop_index(
        op.f("ix_ai_tasks_task_id"),
        table_name="ai_tasks",
    )

    op.drop_index(
        op.f("ix_ai_tasks_status"),
        table_name="ai_tasks",
    )

    op.drop_index(
        op.f("ix_ai_tasks_id"),
        table_name="ai_tasks",
    )

    op.drop_index(
        op.f("ix_ai_tasks_created_at"),
        table_name="ai_tasks",
    )

    op.drop_table(
        "ai_tasks",
    )

