
"""
add missing indexes and decision relationship

Revision ID: b21d02f86729
Revises: 61a6b1f5cc1e
Create Date: 2026-08-10 21:03:45.089830
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.

revision: str = "b21d02f86729"

down_revision: Union[str, Sequence[str], None] = "61a6b1f5cc1e"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # =========================================================
    # ALERTS
    # =========================================================

    op.create_index(
        op.f("ix_alerts_entity_id"),
        "alerts",
        ["entity_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_alerts_module"),
        "alerts",
        ["module"],
        unique=False,
    )

    # =========================================================
    # AUDIT LOGS
    # =========================================================

    op.create_index(
        op.f("ix_audit_logs_module"),
        "audit_logs",
        ["module"],
        unique=False,
    )

    # =========================================================
    # CACHE
    # =========================================================

    op.create_index(
        op.f("ix_cache_entries_created_at"),
        "cache_entries",
        ["created_at"],
        unique=False,
    )

    # =========================================================
    # COPILOT
    # =========================================================

    op.create_index(
        op.f("ix_copilot_conversations_created_at"),
        "copilot_conversations",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        op.f("ix_copilot_conversations_status"),
        "copilot_conversations",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_copilot_messages_role"),
        "copilot_messages",
        ["role"],
        unique=False,
    )

    # =========================================================
    # DECISION HISTORY
    # =========================================================
    #
    # IMPORTANT:
    # We intentionally DO NOT create:
    #
    # decision_history.decision_id
    #       ->
    # decisions.decision_id
    #
    # because the current DecisionService persists decisions
    # directly into decision_history.
    #
    # Existing decision_history contains 84 records that do not
    # have corresponding rows in decisions.
    #
    # Therefore adding the FK would fail and would also make
    # future DecisionService inserts fail unless a parent
    # decisions row is created first.
    #
    # =========================================================

    # =========================================================
    # DEMAND FORECASTS
    # =========================================================

    op.create_index(
        op.f("ix_demand_forecasts_forecast_period"),
        "demand_forecasts",
        ["forecast_period"],
        unique=False,
    )

    # =========================================================
    # KNOWLEDGE CHUNKS
    # =========================================================

    op.create_index(
        op.f("ix_knowledge_chunks_created_at"),
        "knowledge_chunks",
        ["created_at"],
        unique=False,
    )

    op.create_unique_constraint(
        "uq_knowledge_chunk_document_index",
        "knowledge_chunks",
        ["document_id", "chunk_index"],
    )

    # =========================================================
    # KNOWLEDGE DOCUMENTS
    # =========================================================

    op.create_index(
        op.f("ix_knowledge_documents_document_type"),
        "knowledge_documents",
        ["document_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_knowledge_documents_source"),
        "knowledge_documents",
        ["source"],
        unique=False,
    )

    # =========================================================
    # MODEL METRICS
    # =========================================================

    op.create_index(
        op.f("ix_model_metrics_dataset_name"),
        "model_metrics",
        ["dataset_name"],
        unique=False,
    )

    op.create_index(
        op.f("ix_model_metrics_metric_name"),
        "model_metrics",
        ["metric_name"],
        unique=False,
    )

    op.create_index(
        "ix_model_metrics_model_metric",
        "model_metrics",
        ["model_name", "metric_name"],
        unique=False,
    )

    op.create_index(
        op.f("ix_model_metrics_model_version"),
        "model_metrics",
        ["model_version"],
        unique=False,
    )

    # =========================================================
    # MODEL RUNS
    # =========================================================

    op.create_index(
        op.f("ix_model_runs_model_version"),
        "model_runs",
        ["model_version"],
        unique=False,
    )

    # =========================================================
    # RECOMMENDATIONS
    # =========================================================

    op.create_index(
        op.f("ix_recommendations_category"),
        "recommendations",
        ["category"],
        unique=False,
    )

    # =========================================================
    # REPORTS
    # =========================================================

    op.create_index(
        op.f("ix_reports_status"),
        "reports",
        ["status"],
        unique=False,
    )

    # =========================================================
    # SALES PREDICTIONS
    # =========================================================

    op.create_index(
        op.f("ix_sales_predictions_prediction_period"),
        "sales_predictions",
        ["prediction_period"],
        unique=False,
    )

    # =========================================================
    # SYSTEM SETTINGS
    # =========================================================

    op.create_index(
        op.f("ix_system_settings_created_at"),
        "system_settings",
        ["created_at"],
        unique=False,
    )

    # =========================================================
    # USERS
    # =========================================================

    op.create_index(
        op.f("ix_users_is_active"),
        "users",
        ["is_active"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    # =========================================================
    # USERS
    # =========================================================

    op.drop_index(
        op.f("ix_users_is_active"),
        table_name="users",
    )

    # =========================================================
    # SYSTEM SETTINGS
    # =========================================================

    op.drop_index(
        op.f("ix_system_settings_created_at"),
        table_name="system_settings",
    )

    # =========================================================
    # SALES PREDICTIONS
    # =========================================================

    op.drop_index(
        op.f("ix_sales_predictions_prediction_period"),
        table_name="sales_predictions",
    )

    # =========================================================
    # REPORTS
    # =========================================================

    op.drop_index(
        op.f("ix_reports_status"),
        table_name="reports",
    )

    # =========================================================
    # RECOMMENDATIONS
    # =========================================================

    op.drop_index(
        op.f("ix_recommendations_category"),
        table_name="recommendations",
    )

    # =========================================================
    # MODEL RUNS
    # =========================================================

    op.drop_index(
        op.f("ix_model_runs_model_version"),
        table_name="model_runs",
    )

    # =========================================================
    # MODEL METRICS
    # =========================================================

    op.drop_index(
        op.f("ix_model_metrics_model_version"),
        table_name="model_metrics",
    )

    op.drop_index(
        "ix_model_metrics_model_metric",
        table_name="model_metrics",
    )

    op.drop_index(
        op.f("ix_model_metrics_metric_name"),
        table_name="model_metrics",
    )

    op.drop_index(
        op.f("ix_model_metrics_dataset_name"),
        table_name="model_metrics",
    )

    # =========================================================
    # KNOWLEDGE DOCUMENTS
    # =========================================================

    op.drop_index(
        op.f("ix_knowledge_documents_source"),
        table_name="knowledge_documents",
    )

    op.drop_index(
        op.f("ix_knowledge_documents_document_type"),
        table_name="knowledge_documents",
    )

    # =========================================================
    # KNOWLEDGE CHUNKS
    # =========================================================

    op.drop_constraint(
        "uq_knowledge_chunk_document_index",
        "knowledge_chunks",
        type_="unique",
    )

    op.drop_index(
        op.f("ix_knowledge_chunks_created_at"),
        table_name="knowledge_chunks",
    )

    # =========================================================
    # DEMAND FORECASTS
    # =========================================================

    op.drop_index(
        op.f("ix_demand_forecasts_forecast_period"),
        table_name="demand_forecasts",
    )

    # =========================================================
    # COPILOT
    # =========================================================

    op.drop_index(
        op.f("ix_copilot_messages_role"),
        table_name="copilot_messages",
    )

    op.drop_index(
        op.f("ix_copilot_conversations_status"),
        table_name="copilot_conversations",
    )

    op.drop_index(
        op.f("ix_copilot_conversations_created_at"),
        table_name="copilot_conversations",
    )

    # =========================================================
    # CACHE
    # =========================================================

    op.drop_index(
        op.f("ix_cache_entries_created_at"),
        table_name="cache_entries",
    )

    # =========================================================
    # AUDIT LOGS
    # =========================================================

    op.drop_index(
        op.f("ix_audit_logs_module"),
        table_name="audit_logs",
    )

    # =========================================================
    # ALERTS
    # =========================================================

    op.drop_index(
        op.f("ix_alerts_module"),
        table_name="alerts",
    )

    op.drop_index(
        op.f("ix_alerts_entity_id"),
        table_name="alerts",
    )

