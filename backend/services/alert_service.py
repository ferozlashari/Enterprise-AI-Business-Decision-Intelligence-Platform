
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Alert Service

Responsible for:

- Generating real business alerts
- Reading active alerts
- Acknowledging alerts
- Resolving alerts
- Preventing duplicate active alerts
- Evaluating Sales / Inventory / Customer / Forecast /
  Decision risks
- Persisting alerts into PostgreSQL
- Protecting the dashboard from alert flooding
- Preventing duplicate business Decision alerts
- Providing Alert Service health information

Author : Feroz Ali
=========================================================
"""

from __future__ import annotations

import hashlib
import logging

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from backend.database.database import SessionLocal

from backend.database.models import (
    Alert,
    SalesPrediction,
    InventoryPrediction,
    CustomerSegment,
    DemandForecast,
    Decision,
)


logger = logging.getLogger("AlertService")


class AlertService:

    # =====================================================
    # CONFIGURATION
    # =====================================================

    SALES_DROP_THRESHOLD = 0.15

    CUSTOMER_CHURN_THRESHOLD = 0.70

    FORECAST_DECLINE_THRESHOLD = -0.15

    HIGH_RISK_SCORE = 70.0

    CRITICAL_RISK_SCORE = 90.0

    # Maximum alerts returned by dashboard.
    MAX_ACTIVE_ALERTS = 100

    # Maximum source records inspected by detectors.
    MAX_SALES_ROWS = 20
    MAX_INVENTORY_ROWS = 100
    MAX_CUSTOMER_ROWS = 100
    MAX_FORECAST_ROWS = 100
    MAX_DECISION_ROWS = 50

    # Maximum Decision alerts generated during one run.
    MAX_DECISION_ALERTS = 5

    # Maximum Decision alerts of the same business event.
    MAX_DUPLICATE_DECISION_ALERTS = 1

    # =====================================================
    # DATABASE SESSION
    # =====================================================

    @staticmethod
    def _get_db() -> Session:
        """
        Create a new SQLAlchemy database session.
        """

        return SessionLocal()

    # =====================================================
    # UTC TIME
    # =====================================================

    @staticmethod
    def _utc_now() -> datetime:
        """
        Return timezone-aware UTC datetime.
        """

        return datetime.now(timezone.utc)

    # =====================================================
    # SAFE FLOAT
    # =====================================================

    @staticmethod
    def _to_float(
        value: Any,
        default: float = 0.0,
    ) -> float:
        """
        Safely convert a value to float.
        """

        try:

            if value is None:
                return default

            if isinstance(value, bool):
                return float(value)

            if isinstance(value, str):

                cleaned = value.strip()

                if not cleaned:
                    return default

                is_percentage = cleaned.endswith("%")

                cleaned = (
                    cleaned
                    .replace(",", "")
                    .replace("$", "")
                    .replace("€", "")
                    .replace("£", "")
                    .strip()
                )

                if not cleaned:
                    return default

                result = float(cleaned)

                if is_percentage:
                    result = result / 100.0

                return result

            return float(value)

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):

            return default

    # =====================================================
    # SAFE INT
    # =====================================================

    @staticmethod
    def _to_int(
        value: Any,
        default: int = 0,
    ) -> int:
        """
        Safely convert a value to integer.
        """

        try:

            return int(
                AlertService._to_float(
                    value,
                    default,
                )
            )

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):

            return default

    # =====================================================
    # NORMALIZE PROBABILITY
    # =====================================================

    @staticmethod
    def _normalize_probability(
        value: Any,
        default: float = 0.0,
    ) -> float:
        """
        Normalize probability into range 0.0 - 1.0.
        """

        try:

            if value is None:
                return default

            if isinstance(value, str):

                raw = value.strip()

                if not raw:
                    return default

                if raw.endswith("%"):

                    numeric = AlertService._to_float(
                        raw[:-1],
                        default,
                    )

                    return max(
                        0.0,
                        min(
                            1.0,
                            numeric / 100.0,
                        ),
                    )

            numeric = AlertService._to_float(
                value,
                default,
            )

            if numeric > 1.0:
                numeric = numeric / 100.0

            return max(
                0.0,
                min(
                    1.0,
                    numeric,
                ),
            )

        except Exception:

            return default

    # =====================================================
    # SAFE STRING
    # =====================================================

    @staticmethod
    def _safe_string(
        value: Any,
        default: Optional[str] = None,
    ) -> Optional[str]:
        """
        Safely convert a value into a string.
        """

        if value is None:
            return default

        try:

            value = str(value).strip()

            if not value:
                return default

            return value

        except Exception:

            return default

    # =====================================================
    # SAFE ENTITY ID
    # =====================================================

    @staticmethod
    def _entity_id(
        *values: Any,
    ) -> Optional[str]:
        """
        Return the first usable entity identifier.
        """

        for value in values:

            if value is None:
                continue

            result = AlertService._safe_string(value)

            if result:
                return result

        return None

    # =====================================================
    # NORMALIZE SEVERITY
    # =====================================================

    @staticmethod
    def _severity(
        value: Any,
    ) -> str:
        """
        Normalize alert severity.
        """

        severity = str(
            value or "MEDIUM"
        ).strip().upper()

        allowed = {
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "LOW",
        }

        if severity not in allowed:
            return "MEDIUM"

        return severity

    # =====================================================
    # NORMALIZE BUSINESS TEXT
    # =====================================================

    @staticmethod
    def _normalize_text(
        value: Any,
    ) -> str:
        """
        Normalize text for business-level duplicate detection.
        """

        if value is None:
            return ""

        try:

            text = str(value).strip().lower()

            # Collapse whitespace.
            text = " ".join(text.split())

            return text

        except Exception:

            return ""

    # =====================================================
    # CREATE BUSINESS FINGERPRINT
    # =====================================================

    @staticmethod
    def _business_fingerprint(
        *,
        alert_type: str,
        module: Optional[str],
        title: str,
        message: str,
        severity: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Generate a deterministic fingerprint for a business alert.

        This is intentionally independent of the database row ID.

        Example:

            DECISION_RISK
            Decision
            Enterprise Business Decision
            HIGH
            risk_score=85
            risk_level=HIGH

        Multiple database rows representing the same business
        event therefore receive the same fingerprint.
        """

        metadata = (
            metadata
            if isinstance(metadata, dict)
            else {}
        )

        # Decision-specific fields.
        decision_type = AlertService._normalize_text(
            metadata.get("decision_type")
        )

        risk_level = AlertService._normalize_text(
            metadata.get("risk_level")
        )

        risk_score = AlertService._to_float(
            metadata.get("risk_score"),
            0.0,
        )

        # Round score to avoid tiny floating point differences.
        rounded_score = round(
            risk_score,
            2,
        )

        # For generic alerts use the normal message.
        normalized_message = (
            AlertService._normalize_text(message)
        )

        # For Decision alerts, do not depend on timestamps
        # or database IDs.
        if alert_type == "DECISION_RISK":

            identity = "|".join(
                [
                    "DECISION_RISK",
                    AlertService._normalize_text(module),
                    decision_type,
                    risk_level,
                    str(rounded_score),
                    AlertService._normalize_text(title),
                ]
            )

        else:

            identity = "|".join(
                [
                    AlertService._normalize_text(
                        alert_type
                    ),
                    AlertService._normalize_text(
                        module
                    ),
                    AlertService._normalize_text(
                        severity
                    ),
                    AlertService._normalize_text(
                        title
                    ),
                    normalized_message,
                ]
            )

        return hashlib.sha256(
            identity.encode(
                "utf-8"
            )
        ).hexdigest()

    # =====================================================
    # FIND DUPLICATE BUSINESS ALERT
    # =====================================================

    @staticmethod
    def _business_alert_exists(
        db: Session,
        *,
        alert_type: str,
        module: Optional[str],
        title: str,
        message: str,
        severity: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Check active alerts for a business-level duplicate.

        This supplements the normal alert_type/module/entity
        duplicate check.

        It is especially important for Decision alerts because
        several database Decision rows may represent the same
        business condition.
        """

        try:

            query = (
                db.query(Alert)
                .filter(
                    Alert.alert_type == alert_type,
                    Alert.is_resolved.is_(False),
                )
            )

            if module is not None:

                query = query.filter(
                    Alert.module == module
                )

            else:

                query = query.filter(
                    Alert.module.is_(None)
                )

            rows = query.all()

            if not rows:
                return False

            target_fingerprint = (
                AlertService._business_fingerprint(
                    alert_type=alert_type,
                    module=module,
                    title=title,
                    message=message,
                    severity=severity,
                    metadata=metadata,
                )
            )

            for existing in rows:

                existing_metadata = getattr(
                    existing,
                    "metadata_json",
                    None,
                )

                existing_fingerprint = (
                    AlertService._business_fingerprint(
                        alert_type=(
                            getattr(
                                existing,
                                "alert_type",
                                None,
                            )
                            or "SYSTEM"
                        ),
                        module=getattr(
                            existing,
                            "module",
                            None,
                        ),
                        title=(
                            getattr(
                                existing,
                                "title",
                                None,
                            )
                            or ""
                        ),
                        message=(
                            getattr(
                                existing,
                                "message",
                                None,
                            )
                            or ""
                        ),
                        severity=(
                            getattr(
                                existing,
                                "severity",
                                None,
                            )
                            or "MEDIUM"
                        ),
                        metadata=existing_metadata,
                    )
                )

                if (
                    existing_fingerprint
                    == target_fingerprint
                ):
                    return True

            return False

        except Exception:

            logger.exception(
                "Business alert duplicate check failed: "
                "type=%s module=%s",
                alert_type,
                module,
            )

            raise

    # =====================================================
    # DUPLICATE ACTIVE ALERT CHECK
    # =====================================================

    @staticmethod
    def _alert_exists(
        db: Session,
        alert_type: str,
        module: Optional[str] = None,
        entity_id: Optional[str] = None,
    ) -> bool:
        """
        Check whether an unresolved alert already exists.

        Duplicate identity:

            alert_type
            module
            entity_id
        """

        try:

            query = (
                db.query(Alert)
                .filter(
                    Alert.alert_type == alert_type,
                    Alert.is_resolved.is_(False),
                )
            )

            if module is not None:

                query = query.filter(
                    Alert.module == module
                )

            else:

                query = query.filter(
                    Alert.module.is_(None)
                )

            if entity_id is not None:

                query = query.filter(
                    Alert.entity_id == entity_id
                )

            else:

                query = query.filter(
                    Alert.entity_id.is_(None)
                )

            return query.first() is not None

        except Exception:

            logger.exception(
                "Alert duplicate check failed: "
                "type=%s module=%s entity=%s",
                alert_type,
                module,
                entity_id,
            )

            raise

    # =====================================================
    # CREATE ALERT
    # =====================================================

    @staticmethod
    def _create_alert(
        db: Session,
        *,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        module: Optional[str] = None,
        entity_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[Alert]:
        """
        Create an alert if an active duplicate does not exist.

        Two duplicate checks are performed:

        1. Exact identity:
           alert_type + module + entity_id

        2. Business identity:
           deterministic fingerprint

        The second check prevents duplicate business events
        when multiple database rows represent the same event.
        """

        severity = AlertService._severity(
            severity
        )

        alert_type = (
            AlertService._safe_string(
                alert_type,
                "SYSTEM",
            )
            or "SYSTEM"
        )

        title = (
            AlertService._safe_string(
                title,
                "Business Alert",
            )
            or "Business Alert"
        )

        message = (
            AlertService._safe_string(
                message,
                "",
            )
            or ""
        )

        module = AlertService._safe_string(
            module
        )

        entity_id = AlertService._safe_string(
            entity_id
        )

        safe_metadata = (
            metadata
            if isinstance(metadata, dict)
            else {}
        )

        try:

            # -------------------------------------------------
            # CHECK 1
            # -------------------------------------------------

            if AlertService._alert_exists(
                db=db,
                alert_type=alert_type,
                module=module,
                entity_id=entity_id,
            ):

                logger.debug(
                    "Duplicate active alert skipped: "
                    "type=%s module=%s entity=%s",
                    alert_type,
                    module,
                    entity_id,
                )

                return None

            # -------------------------------------------------
            # CHECK 2
            #
            # Business-level duplicate.
            # -------------------------------------------------

            if AlertService._business_alert_exists(
                db=db,
                alert_type=alert_type,
                module=module,
                title=title,
                message=message,
                severity=severity,
                metadata=safe_metadata,
            ):

                logger.debug(
                    "Duplicate business alert skipped: "
                    "type=%s module=%s title=%s",
                    alert_type,
                    module,
                    title,
                )

                return None

            # -------------------------------------------------
            # CREATE
            # -------------------------------------------------

            alert = Alert(
                alert_type=alert_type,
                severity=severity,
                title=title,
                message=message,
                module=module,
                entity_id=entity_id,
                is_read=False,
                is_resolved=False,
                metadata_json=safe_metadata,
                created_at=AlertService._utc_now(),
            )

            db.add(alert)

            db.flush()

            logger.info(
                "Business alert created: "
                "type=%s severity=%s id=%s",
                alert_type,
                severity,
                alert.id,
            )

            return alert

        except Exception:

            logger.exception(
                "Failed to create alert: "
                "type=%s module=%s entity=%s",
                alert_type,
                module,
                entity_id,
            )

            raise

    # =====================================================
    # SERIALIZE ALERT
    # =====================================================

    @staticmethod
    def _serialize_alert(
        alert: Alert,
    ) -> dict[str, Any]:
        """
        Convert Alert ORM object into JSON-safe dictionary.
        """

        created_at = getattr(
            alert,
            "created_at",
            None,
        )

        metadata = getattr(
            alert,
            "metadata_json",
            None,
        )

        if not isinstance(metadata, dict):
            metadata = {}

        alert_type = (
            getattr(
                alert,
                "alert_type",
                None,
            )
            or "SYSTEM"
        )

        module = getattr(
            alert,
            "module",
            None,
        )

        return {
            "id": getattr(
                alert,
                "id",
                None,
            ),

            "type": str(alert_type),

            "alert_type": str(alert_type),

            "severity": AlertService._severity(
                getattr(
                    alert,
                    "severity",
                    "MEDIUM",
                )
            ),

            "title": str(
                getattr(
                    alert,
                    "title",
                    None,
                )
                or "Business Alert"
            ),

            "message": str(
                getattr(
                    alert,
                    "message",
                    None,
                )
                or ""
            ),

            "category": str(
                module
                or alert_type
                or "System"
            ),

            "module": module,

            "entity_id": getattr(
                alert,
                "entity_id",
                None,
            ),

            "is_read": bool(
                getattr(
                    alert,
                    "is_read",
                    False,
                )
            ),

            "is_resolved": bool(
                getattr(
                    alert,
                    "is_resolved",
                    False,
                )
            ),

            "time": (
                created_at.isoformat()
                if created_at
                else None
            ),

            "created_at": (
                created_at.isoformat()
                if created_at
                else None
            ),

            "metadata": metadata,
        }

    # =====================================================
    # GET ACTIVE ALERTS
    # =====================================================

    @staticmethod
    def get_active_alerts() -> dict[str, Any]:
        """
        Return unresolved business alerts.

        Highest severity is displayed first.
        """

        db: Optional[Session] = None

        try:

            db = AlertService._get_db()

            rows = (
                db.query(Alert)
                .filter(
                    Alert.is_resolved.is_(False)
                )
                .order_by(
                    Alert.created_at.desc()
                )
                .limit(
                    AlertService.MAX_ACTIVE_ALERTS
                )
                .all()
            )

            severity_order = {
                "CRITICAL": 0,
                "HIGH": 1,
                "MEDIUM": 2,
                "LOW": 3,
            }

            serialized = [
                AlertService._serialize_alert(
                    alert
                )
                for alert in rows
            ]

            serialized.sort(
                key=lambda item: (
                    severity_order.get(
                        item.get(
                            "severity",
                            "MEDIUM",
                        ),
                        99,
                    ),
                    item.get(
                        "created_at"
                    )
                    or "",
                )
            )

            return {
                "status": "success",
                "count": len(serialized),
                "alerts": serialized,
            }

        except Exception as exc:

            logger.exception(
                "Unable to load active alerts"
            )

            return {
                "status": "error",
                "count": 0,
                "alerts": [],
                "message": str(exc),
            }

        finally:

            if db is not None:

                try:
                    db.close()

                except Exception:

                    logger.warning(
                        "Failed to close alert database session"
                    )

    # =====================================================
    # CLEAN DUPLICATE DECISION ALERTS
    # =====================================================

    @staticmethod
    def _cleanup_duplicate_decision_alerts(
        db: Session,
    ) -> int:
        """
        Remove duplicate active Decision alerts.

        IMPORTANT:

        This cleans the duplicates that already exist in the
        PostgreSQL Alert table.

        The newest alert for each business fingerprint is kept.

        Older duplicates are marked resolved rather than deleted.

        This is safer for audit/history because the records remain
        in the database.
        """

        try:

            rows = (
                db.query(Alert)
                .filter(
                    Alert.alert_type == "DECISION_RISK",
                    Alert.module == "Decision",
                    Alert.is_resolved.is_(False),
                )
                .order_by(
                    Alert.created_at.desc(),
                    Alert.id.desc(),
                )
                .all()
            )

            if not rows:
                return 0

            seen: set[str] = set()

            duplicate_count = 0

            for alert in rows:

                metadata = getattr(
                    alert,
                    "metadata_json",
                    None,
                )

                fingerprint = (
                    AlertService._business_fingerprint(
                        alert_type="DECISION_RISK",
                        module="Decision",
                        title=(
                            getattr(
                                alert,
                                "title",
                                None,
                            )
                            or ""
                        ),
                        message=(
                            getattr(
                                alert,
                                "message",
                                None,
                            )
                            or ""
                        ),
                        severity=(
                            getattr(
                                alert,
                                "severity",
                                None,
                            )
                            or "MEDIUM"
                        ),
                        metadata=metadata,
                    )
                )

                if fingerprint in seen:

                    alert.is_resolved = True
                    alert.is_read = True

                    duplicate_count += 1

                    logger.info(
                        "Resolved duplicate Decision alert: "
                        "id=%s",
                        getattr(
                            alert,
                            "id",
                            None,
                        ),
                    )

                    continue

                seen.add(fingerprint)

            if duplicate_count:

                db.flush()

            logger.info(
                "Decision alert cleanup completed. "
                "Duplicates resolved=%s",
                duplicate_count,
            )

            return duplicate_count

        except Exception:

            logger.exception(
                "Failed to cleanup duplicate Decision alerts"
            )

            raise

    # =====================================================
    # GENERATE BUSINESS ALERTS
    # =====================================================

    @staticmethod
    def generate_business_alerts() -> dict[str, Any]:
        """
        Run all business-risk detectors.

        Sources:

        - SalesPrediction
        - InventoryPrediction
        - CustomerSegment
        - DemandForecast
        - Decision

        Existing duplicate Decision alerts are cleaned first.
        """

        db: Optional[Session] = None

        generated_alerts: list[
            dict[str, Any]
        ] = []

        detector_status = {
            "sales": "pending",
            "inventory": "pending",
            "customer": "pending",
            "forecast": "pending",
            "decision": "pending",
        }

        detector_errors: dict[
            str,
            str,
        ] = {}

        duplicates_cleaned = 0

        try:

            logger.info(
                "Starting business alert generation..."
            )

            db = AlertService._get_db()

            # -------------------------------------------------
            # CLEAN EXISTING DECISION DUPLICATES
            # -------------------------------------------------

            try:

                duplicates_cleaned = (
                    AlertService
                    ._cleanup_duplicate_decision_alerts(
                        db
                    )
                )

            except Exception as exc:

                logger.exception(
                    "Decision alert cleanup failed"
                )

                detector_errors[
                    "decision_cleanup"
                ] = str(exc)

            # -------------------------------------------------
            # SALES
            # -------------------------------------------------

            try:

                AlertService._generate_sales_alerts(
                    db,
                    generated_alerts,
                )

                detector_status["sales"] = "success"

            except Exception as exc:

                detector_status["sales"] = "error"

                detector_errors["sales"] = str(exc)

                logger.exception(
                    "Sales alert detector failed"
                )

            # -------------------------------------------------
            # INVENTORY
            # -------------------------------------------------

            try:

                AlertService._generate_inventory_alerts(
                    db,
                    generated_alerts,
                )

                detector_status["inventory"] = "success"

            except Exception as exc:

                detector_status["inventory"] = "error"

                detector_errors["inventory"] = str(exc)

                logger.exception(
                    "Inventory alert detector failed"
                )

            # -------------------------------------------------
            # CUSTOMER
            # -------------------------------------------------

            try:

                AlertService._generate_customer_alerts(
                    db,
                    generated_alerts,
                )

                detector_status["customer"] = "success"

            except Exception as exc:

                detector_status["customer"] = "error"

                detector_errors["customer"] = str(exc)

                logger.exception(
                    "Customer alert detector failed"
                )

            # -------------------------------------------------
            # FORECAST
            # -------------------------------------------------

            try:

                AlertService._generate_forecast_alerts(
                    db,
                    generated_alerts,
                )

                detector_status["forecast"] = "success"

            except Exception as exc:

                detector_status["forecast"] = "error"

                detector_errors["forecast"] = str(exc)

                logger.exception(
                    "Forecast alert detector failed"
                )

            # -------------------------------------------------
            # DECISION
            # -------------------------------------------------

            try:

                AlertService._generate_decision_alerts(
                    db,
                    generated_alerts,
                )

                detector_status["decision"] = "success"

            except Exception as exc:

                detector_status["decision"] = "error"

                detector_errors["decision"] = str(exc)

                logger.exception(
                    "Decision alert detector failed"
                )

            # -------------------------------------------------
            # COMMIT
            # -------------------------------------------------

            db.commit()

            logger.info(
                "Business alert generation completed. "
                "Generated=%s duplicates_cleaned=%s",
                len(generated_alerts),
                duplicates_cleaned,
            )

            overall_status = (
                "success"
                if not detector_errors
                else "partial_success"
            )

            result = {
                "status": overall_status,
                "generated": len(
                    generated_alerts
                ),
                "duplicates_cleaned": (
                    duplicates_cleaned
                ),
                "alerts": generated_alerts,
                "detectors": detector_status,
            }

            if detector_errors:

                result[
                    "detector_errors"
                ] = detector_errors

            return result

        except Exception as exc:

            if db is not None:

                try:
                    db.rollback()

                except Exception:
                    pass

            logger.exception(
                "Business alert generation failed"
            )

            return {
                "status": "error",
                "generated": 0,
                "duplicates_cleaned": (
                    duplicates_cleaned
                ),
                "alerts": [],
                "detectors": detector_status,
                "detector_errors": detector_errors,
                "message": str(exc),
            }

        finally:

            if db is not None:

                try:
                    db.close()

                except Exception:

                    logger.warning(
                        "Failed to close alert "
                        "generation session"
                    )

    # =====================================================
    # SALES ALERT GENERATOR
    # =====================================================

    @staticmethod
    def _generate_sales_alerts(
        db: Session,
        output: list[dict[str, Any]],
    ) -> None:
        """
        Detect sales prediction risks.
        """

        rows = (
            db.query(SalesPrediction)
            .order_by(
                SalesPrediction.created_at.desc()
            )
            .limit(
                AlertService.MAX_SALES_ROWS
            )
            .all()
        )

        for row in rows:

            prediction = AlertService._to_float(
                getattr(
                    row,
                    "prediction_value",
                    None,
                )
            )

            input_data = getattr(
                row,
                "input_data",
                None,
            )

            if not isinstance(input_data, dict):
                input_data = {}

            growth = AlertService._to_float(
                input_data.get(
                    "growth",
                    input_data.get(
                        "growth_rate",
                        input_data.get(
                            "sales_growth",
                            0,
                        ),
                    ),
                )
            )

            entity_id = AlertService._entity_id(
                getattr(
                    row,
                    "store_id",
                    None,
                ),
                getattr(
                    row,
                    "id",
                    None,
                ),
            )

            # ---------------------------------------------
            # REVENUE DROP
            # ---------------------------------------------

            if (
                growth
                <= -AlertService.SALES_DROP_THRESHOLD
            ):

                severity = (
                    "CRITICAL"
                    if growth <= -0.30
                    else "HIGH"
                )

                alert = AlertService._create_alert(
                    db,
                    alert_type="REVENUE_DROP",
                    severity=severity,
                    title="Revenue Drop Detected",
                    message=(
                        "Sales growth has declined by "
                        f"{abs(growth) * 100:.1f}%."
                    ),
                    module="Sales",
                    entity_id=entity_id,
                    metadata={
                        "growth": growth,
                        "prediction": prediction,
                        "prediction_period": getattr(
                            row,
                            "prediction_period",
                            None,
                        ),
                        "model_version": getattr(
                            row,
                            "model_version",
                            None,
                        ),
                        "confidence_score": getattr(
                            row,
                            "confidence_score",
                            None,
                        ),
                    },
                )

                if alert:

                    output.append(
                        AlertService._serialize_alert(
                            alert
                        )
                    )

            # ---------------------------------------------
            # NEGATIVE SALES FORECAST
            # ---------------------------------------------

            if prediction < 0:

                alert = AlertService._create_alert(
                    db,
                    alert_type="NEGATIVE_SALES_FORECAST",
                    severity="HIGH",
                    title="Negative Sales Forecast",
                    message=(
                        "The sales prediction engine "
                        "returned a negative sales forecast."
                    ),
                    module="Sales",
                    entity_id=entity_id,
                    metadata={
                        "prediction": prediction,
                        "prediction_period": getattr(
                            row,
                            "prediction_period",
                            None,
                        ),
                        "model_version": getattr(
                            row,
                            "model_version",
                            None,
                        ),
                    },
                )

                if alert:

                    output.append(
                        AlertService._serialize_alert(
                            alert
                        )
                    )

    # =====================================================
    # INVENTORY ALERT GENERATOR
    # =====================================================

    @staticmethod
    def _generate_inventory_alerts(
        db: Session,
        output: list[dict[str, Any]],
    ) -> None:
        """
        Detect inventory shortages and reorder risks.
        """

        rows = (
            db.query(InventoryPrediction)
            .order_by(
                InventoryPrediction.created_at.desc()
            )
            .limit(
                AlertService.MAX_INVENTORY_ROWS
            )
            .all()
        )

        for row in rows:

            current_stock = AlertService._to_float(
                getattr(
                    row,
                    "current_stock",
                    0,
                )
            )

            predicted_demand = AlertService._to_float(
                getattr(
                    row,
                    "predicted_demand",
                    0,
                )
            )

            reorder_point = AlertService._to_float(
                getattr(
                    row,
                    "reorder_point",
                    0,
                )
            )

            safety_stock = AlertService._to_float(
                getattr(
                    row,
                    "safety_stock",
                    0,
                )
            )

            risk_level = str(
                getattr(
                    row,
                    "risk_level",
                    "",
                )
                or ""
            ).strip().upper()

            entity_id = AlertService._entity_id(
                getattr(
                    row,
                    "product_id",
                    None,
                ),
                getattr(
                    row,
                    "store_id",
                    None,
                ),
                getattr(
                    row,
                    "id",
                    None,
                ),
            )

            # ---------------------------------------------
            # HIGH / CRITICAL RISK
            # ---------------------------------------------

            if risk_level in {
                "CRITICAL",
                "HIGH",
            }:

                severity = (
                    "CRITICAL"
                    if risk_level == "CRITICAL"
                    else "HIGH"
                )

                alert = AlertService._create_alert(
                    db,
                    alert_type="INVENTORY_RISK",
                    severity=severity,
                    title="Inventory Risk Detected",
                    message=(
                        "Inventory risk is "
                        f"{risk_level}. "
                        f"Current stock: "
                        f"{current_stock:.0f}, "
                        f"predicted demand: "
                        f"{predicted_demand:.1f}."
                    ),
                    module="Inventory",
                    entity_id=entity_id,
                    metadata={
                        "risk_level": risk_level,
                        "current_stock": current_stock,
                        "predicted_demand": predicted_demand,
                        "reorder_point": reorder_point,
                        "safety_stock": safety_stock,
                        "store_id": getattr(
                            row,
                            "store_id",
                            None,
                        ),
                        "product_id": getattr(
                            row,
                            "product_id",
                            None,
                        ),
                        "model_version": getattr(
                            row,
                            "model_version",
                            None,
                        ),
                    },
                )

                if alert:

                    output.append(
                        AlertService._serialize_alert(
                            alert
                        )
                    )

                continue

            # ---------------------------------------------
            # STOCK BELOW DEMAND
            # ---------------------------------------------

            if (
                predicted_demand > 0
                and current_stock < predicted_demand
            ):

                shortage_percentage = (
                    (
                        predicted_demand
                        - current_stock
                    )
                    / predicted_demand
                )

                severity = (
                    "CRITICAL"
                    if shortage_percentage >= 0.50
                    else "HIGH"
                    if shortage_percentage >= 0.25
                    else "MEDIUM"
                )

                alert = AlertService._create_alert(
                    db,
                    alert_type="INVENTORY_SHORTAGE",
                    severity=severity,
                    title="Inventory Shortage",
                    message=(
                        f"Current stock "
                        f"({current_stock:.0f}) is below "
                        f"predicted demand "
                        f"({predicted_demand:.1f}) by "
                        f"{shortage_percentage * 100:.1f}%."
                    ),
                    module="Inventory",
                    entity_id=entity_id,
                    metadata={
                        "current_stock": current_stock,
                        "predicted_demand": predicted_demand,
                        "shortage_percentage":
                            shortage_percentage,
                        "reorder_point": reorder_point,
                        "store_id": getattr(
                            row,
                            "store_id",
                            None,
                        ),
                        "product_id": getattr(
                            row,
                            "product_id",
                            None,
                        ),
                    },
                )

                if alert:

                    output.append(
                        AlertService._serialize_alert(
                            alert
                        )
                    )

            # ---------------------------------------------
            # BELOW REORDER POINT
            # ---------------------------------------------

            if (
                reorder_point > 0
                and current_stock < reorder_point
            ):

                alert = AlertService._create_alert(
                    db,
                    alert_type="REORDER_POINT_REACHED",
                    severity="MEDIUM",
                    title="Inventory Reorder Required",
                    message=(
                        f"Current stock "
                        f"({current_stock:.0f}) is below "
                        f"the reorder point "
                        f"({reorder_point:.1f})."
                    ),
                    module="Inventory",
                    entity_id=entity_id,
                    metadata={
                        "current_stock": current_stock,
                        "reorder_point": reorder_point,
                        "predicted_demand": predicted_demand,
                        "safety_stock": safety_stock,
                        "product_id": getattr(
                            row,
                            "product_id",
                            None,
                        ),
                        "store_id": getattr(
                            row,
                            "store_id",
                            None,
                        ),
                    },
                )

                if alert:

                    output.append(
                        AlertService._serialize_alert(
                            alert
                        )
                    )

    # =====================================================
    # CUSTOMER ALERT GENERATOR
    # =====================================================

    @staticmethod
    def _generate_customer_alerts(
        db: Session,
        output: list[dict[str, Any]],
    ) -> None:
        """
        Detect customer churn risks.
        """

        rows = (
            db.query(CustomerSegment)
            .filter(
                CustomerSegment.churn_probability.is_not(
                    None
                )
            )
            .order_by(
                CustomerSegment.created_at.desc()
            )
            .limit(
                AlertService.MAX_CUSTOMER_ROWS
            )
            .all()
        )

        for row in rows:

            churn = AlertService._normalize_probability(
                getattr(
                    row,
                    "churn_probability",
                    0,
                )
            )

            if (
                churn
                < AlertService.CUSTOMER_CHURN_THRESHOLD
            ):
                continue

            entity_id = AlertService._entity_id(
                getattr(
                    row,
                    "customer_id",
                    None,
                ),
                getattr(
                    row,
                    "id",
                    None,
                ),
            )

            severity = (
                "CRITICAL"
                if churn >= 0.90
                else "HIGH"
                if churn >= 0.80
                else "MEDIUM"
            )

            alert = AlertService._create_alert(
                db,
                alert_type="CUSTOMER_CHURN_RISK",
                severity=severity,
                title="Customer Churn Risk",
                message=(
                    "Customer churn probability is "
                    f"{churn * 100:.1f}%."
                ),
                module="Customer",
                entity_id=entity_id,
                metadata={
                    "customer_id": getattr(
                        row,
                        "customer_id",
                        None,
                    ),
                    "churn_probability": churn,
                    "churn_probability_percent":
                        churn * 100,
                    "segment": getattr(
                        row,
                        "segment",
                        None,
                    ),
                    "customer_value":
                        AlertService._to_float(
                            getattr(
                                row,
                                "customer_value",
                                0,
                            )
                        ),
                    "monetary_value":
                        AlertService._to_float(
                            getattr(
                                row,
                                "monetary_value",
                                0,
                            )
                        ),
                    "model_version": getattr(
                        row,
                        "model_version",
                        None,
                    ),
                },
            )

            if alert:

                output.append(
                    AlertService._serialize_alert(
                        alert
                    )
                )

    # =====================================================
    # FORECAST ALERT GENERATOR
    # =====================================================

    @staticmethod
    def _generate_forecast_alerts(
        db: Session,
        output: list[dict[str, Any]],
    ) -> None:
        """
        Detect significant demand forecast declines.
        """

        rows = (
            db.query(DemandForecast)
            .order_by(
                DemandForecast.created_at.desc()
            )
            .limit(
                AlertService.MAX_FORECAST_ROWS
            )
            .all()
        )

        for row in rows:

            growth = AlertService._to_float(
                getattr(
                    row,
                    "forecast_growth",
                    0,
                )
            )

            if (
                growth
                > AlertService.FORECAST_DECLINE_THRESHOLD
            ):
                continue

            entity_id = AlertService._entity_id(
                getattr(
                    row,
                    "product_id",
                    None,
                ),
                getattr(
                    row,
                    "store_id",
                    None,
                ),
                getattr(
                    row,
                    "id",
                    None,
                ),
            )

            severity = (
                "CRITICAL"
                if growth <= -0.30
                else "HIGH"
                if growth <= -0.20
                else "MEDIUM"
            )

            alert = AlertService._create_alert(
                db,
                alert_type="FORECAST_DECLINE",
                severity=severity,
                title="Demand Forecast Decline",
                message=(
                    "Forecast demand is expected "
                    "to decline by "
                    f"{abs(growth) * 100:.1f}%."
                ),
                module="Forecast",
                entity_id=entity_id,
                metadata={
                    "forecast_growth": growth,
                    "forecast_growth_percent":
                        growth * 100,
                    "product_id": getattr(
                        row,
                        "product_id",
                        None,
                    ),
                    "store_id": getattr(
                        row,
                        "store_id",
                        None,
                    ),
                    "forecast_period": getattr(
                        row,
                        "forecast_period",
                        None,
                    ),
                    "predicted_demand":
                        AlertService._to_float(
                            getattr(
                                row,
                                "predicted_demand",
                                0,
                            )
                        ),
                    "lower_bound":
                        AlertService._to_float(
                            getattr(
                                row,
                                "lower_bound",
                                0,
                            )
                        ),
                    "upper_bound":
                        AlertService._to_float(
                            getattr(
                                row,
                                "upper_bound",
                                0,
                            )
                        ),
                    "model_version": getattr(
                        row,
                        "model_version",
                        None,
                    ),
                },
            )

            if alert:

                output.append(
                    AlertService._serialize_alert(
                        alert
                    )
                )

    # =====================================================
    # DECISION ALERT GENERATOR
    # =====================================================

    @staticmethod
    def _generate_decision_alerts(
        db: Session,
        output: list[dict[str, Any]],
    ) -> None:
        """
        Convert the highest-risk business decisions into
        dashboard alerts.

        IMPORTANT:

        Multiple Decision rows may describe the same business
        condition.

        Therefore this detector performs TWO levels of protection:

        1. Database identity protection.
        2. Business fingerprint protection.

        Only unique business Decision events become alerts.
        """

        rows = (
            db.query(Decision)
            .filter(
                Decision.status.in_(
                    [
                        "ACTIVE",
                        "OPEN",
                        "PENDING",
                    ]
                )
            )
            .order_by(
                Decision.risk_score.desc(),
                Decision.created_at.desc(),
            )
            .limit(
                AlertService.MAX_DECISION_ROWS
            )
            .all()
        )

        generated_count = 0

        seen_business_decisions: set[str] = set()

        for row in rows:

            if (
                generated_count
                >= AlertService.MAX_DECISION_ALERTS
            ):
                break

            risk_level = str(
                getattr(
                    row,
                    "risk_level",
                    "LOW",
                )
                or "LOW"
            ).strip().upper()

            risk_score = AlertService._to_float(
                getattr(
                    row,
                    "risk_score",
                    0,
                )
            )

            # ---------------------------------------------
            # IGNORE LOW-RISK DECISIONS
            # ---------------------------------------------

            if (
                risk_level not in {
                    "HIGH",
                    "CRITICAL",
                }
                and risk_score
                < AlertService.HIGH_RISK_SCORE
            ):
                continue

            # ---------------------------------------------
            # DETERMINE SEVERITY
            # ---------------------------------------------

            if (
                risk_level == "CRITICAL"
                or risk_score
                >= AlertService.CRITICAL_RISK_SCORE
            ):

                severity = "CRITICAL"

            else:

                severity = "HIGH"

            # ---------------------------------------------
            # TITLE
            # ---------------------------------------------

            title = (
                getattr(
                    row,
                    "title",
                    None,
                )
                or "Enterprise Business Decision"
            )

            title = str(title)

            # ---------------------------------------------
            # SUMMARY
            # ---------------------------------------------

            summary = (
                getattr(
                    row,
                    "summary",
                    None,
                )
                or getattr(
                    row,
                    "decision",
                    None,
                )
                or (
                    "Business conditions require "
                    "management attention."
                )
            )

            summary = str(summary)

            # ---------------------------------------------
            # DECISION TYPE
            # ---------------------------------------------

            decision_type = (
                AlertService._normalize_text(
                    getattr(
                        row,
                        "decision_type",
                        None,
                    )
                )
            )

            # ---------------------------------------------
            # BUSINESS DECISION FINGERPRINT
            # ---------------------------------------------

            business_key = "|".join(
                [
                    decision_type,
                    AlertService._normalize_text(
                        risk_level
                    ),
                    str(
                        round(
                            risk_score,
                            2,
                        )
                    ),
                    AlertService._normalize_text(
                        title
                    ),
                    AlertService._normalize_text(
                        summary
                    ),
                ]
            )

            fingerprint = hashlib.sha256(
                business_key.encode(
                    "utf-8"
                )
            ).hexdigest()

            # ---------------------------------------------
            # SKIP SAME BUSINESS EVENT IN SAME RUN
            # ---------------------------------------------

            if fingerprint in seen_business_decisions:

                logger.debug(
                    "Duplicate Decision business event "
                    "skipped in current run: %s",
                    fingerprint,
                )

                continue

            seen_business_decisions.add(
                fingerprint
            )

            # ---------------------------------------------
            # STABLE DECISION IDENTIFIER
            # ---------------------------------------------

            decision_id = AlertService._entity_id(
                getattr(
                    row,
                    "decision_id",
                    None,
                ),
                getattr(
                    row,
                    "id",
                    None,
                ),
            )

            # ---------------------------------------------
            # CREATE ALERT
            # ---------------------------------------------

            alert = AlertService._create_alert(
                db,
                alert_type="DECISION_RISK",
                severity=severity,
                title=title,
                message=(
                    "Decision risk level is "
                    f"{risk_level} with risk score "
                    f"{risk_score:.1f}. "
                    f"{summary[:500]}"
                ),
                module="Decision",

                # We keep decision_id for traceability,
                # while business fingerprint prevents duplicates.
                entity_id=decision_id,

                metadata={
                    "decision_id": getattr(
                        row,
                        "decision_id",
                        None,
                    ),
                    "decision_type": getattr(
                        row,
                        "decision_type",
                        None,
                    ),
                    "risk_level": risk_level,
                    "risk_score": risk_score,
                    "status": getattr(
                        row,
                        "status",
                        None,
                    ),
                    "title": title,
                    "summary": summary[:1000],
                    "business_fingerprint": fingerprint,
                },
            )

            if alert:

                output.append(
                    AlertService._serialize_alert(
                        alert
                    )
                )

                generated_count += 1

        logger.info(
            "Decision alert detector completed. "
            "Generated=%s max=%s",
            generated_count,
            AlertService.MAX_DECISION_ALERTS,
        )

    # =====================================================
    # ACKNOWLEDGE ALERT
    # =====================================================

    @staticmethod
    def acknowledge_alert(
        alert_id: int,
    ) -> dict[str, Any]:
        """
        Mark an alert as acknowledged/read.
        """

        db: Optional[Session] = None

        try:

            db = AlertService._get_db()

            alert = (
                db.query(Alert)
                .filter(
                    Alert.id == alert_id
                )
                .first()
            )

            if alert is None:

                return {
                    "status": "error",
                    "not_found": True,
                    "message": (
                        f"Alert {alert_id} "
                        "was not found."
                    ),
                }

            if bool(
                getattr(
                    alert,
                    "is_resolved",
                    False,
                )
            ):

                return {
                    "status": "error",
                    "message": (
                        f"Alert {alert_id} "
                        "has already been resolved."
                    ),
                }

            alert.is_read = True

            db.commit()

            db.refresh(alert)

            logger.info(
                "Alert acknowledged successfully: "
                "id=%s",
                alert_id,
            )

            return {
                "status": "success",
                "alert": AlertService._serialize_alert(
                    alert
                ),
            }

        except Exception as exc:

            if db is not None:

                try:
                    db.rollback()

                except Exception:
                    pass

            logger.exception(
                "Failed to acknowledge alert %s",
                alert_id,
            )

            return {
                "status": "error",
                "message": str(exc),
            }

        finally:

            if db is not None:

                try:
                    db.close()

                except Exception:
                    pass

    # =====================================================
    # RESOLVE ALERT
    # =====================================================

    @staticmethod
    def resolve_alert(
        alert_id: int,
    ) -> dict[str, Any]:
        """
        Mark an alert as resolved.

        Resolved alerts no longer appear in the active list.
        """

        db: Optional[Session] = None

        try:

            db = AlertService._get_db()

            alert = (
                db.query(Alert)
                .filter(
                    Alert.id == alert_id
                )
                .first()
            )

            if alert is None:

                return {
                    "status": "error",
                    "not_found": True,
                    "message": (
                        f"Alert {alert_id} "
                        "was not found."
                    ),
                }

            if bool(
                getattr(
                    alert,
                    "is_resolved",
                    False,
                )
            ):

                return {
                    "status": "success",
                    "already_resolved": True,
                    "alert": AlertService._serialize_alert(
                        alert
                    ),
                }

            alert.is_resolved = True

            # Resolved alerts are automatically acknowledged.
            alert.is_read = True

            db.commit()

            db.refresh(alert)

            logger.info(
                "Alert resolved successfully: "
                "id=%s",
                alert_id,
            )

            return {
                "status": "success",
                "alert": AlertService._serialize_alert(
                    alert
                ),
            }

        except Exception as exc:

            if db is not None:

                try:
                    db.rollback()

                except Exception:
                    pass

            logger.exception(
                "Failed to resolve alert %s",
                alert_id,
            )

            return {
                "status": "error",
                "message": str(exc),
            }

        finally:

            if db is not None:

                try:
                    db.close()

                except Exception:
                    pass

    # =====================================================
    # HEALTH
    # =====================================================

    @staticmethod
    def health() -> dict[str, Any]:
        """
        Verify that Alert Service can access PostgreSQL.

        Dashboard-safe response:

            System: healthy
        """

        db: Optional[Session] = None

        timestamp = (
            AlertService._utc_now().isoformat()
        )

        try:

            db = AlertService._get_db()

            total = (
                db.query(
                    Alert.id
                ).count()
            )

            active = (
                db.query(
                    Alert.id
                )
                .filter(
                    Alert.is_resolved.is_(False)
                )
                .count()
            )

            unread = (
                db.query(
                    Alert.id
                )
                .filter(
                    Alert.is_resolved.is_(False),
                    Alert.is_read.is_(False),
                )
                .count()
            )

            critical = (
                db.query(
                    Alert.id
                )
                .filter(
                    Alert.is_resolved.is_(False),
                    Alert.severity == "CRITICAL",
                )
                .count()
            )

            # Explicit query confirms that the database is
            # actually responding.
            db.execute(
                __import__(
                    "sqlalchemy"
                ).text(
                    "SELECT 1"
                )
            )

            return {
                "status": "healthy",
                "system": "healthy",
                "service": "Alert Service",
                "database": "healthy",
                "total_alerts": total,
                "active_alerts": active,
                "unread_alerts": unread,
                "critical_alerts": critical,
                "timestamp": timestamp,
            }

        except Exception as exc:

            logger.exception(
                "Alert service health check failed"
            )

            return {
                "status": "degraded",
                "system": "degraded",
                "service": "Alert Service",
                "database": "unavailable",
                "total_alerts": 0,
                "active_alerts": 0,
                "unread_alerts": 0,
                "critical_alerts": 0,
                "message": str(exc),
                "timestamp": timestamp,
            }

        finally:

            if db is not None:

                try:
                    db.close()

                except Exception:
                    pass


# =========================================================
# END OF ALERT SERVICE
# =========================================================

