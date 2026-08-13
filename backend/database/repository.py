
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

User Repository

Handles:
- User lookup
- User creation
- User deletion
- User role management
- User listing

Author : Feroz Ali
=========================================================
"""

from sqlalchemy.orm import Session

from backend.database.models import User


# =========================================================
# CONSTANTS
# =========================================================

DEFAULT_ROLE = "analyst"

ALLOWED_ROLES = {
    "admin",
    "executive",
    "manager",
    "analyst",
}


# =========================================================
# ROLE NORMALIZATION
# =========================================================

def normalize_role(role: str | None) -> str:
    """
    Normalize user roles before storing them.

    Supported roles:
        admin
        executive
        manager
        analyst

    Examples:

        "Admin"       -> "admin"
        " ADMIN "     -> "admin"
        "Executive"   -> "executive"
        None          -> "analyst"
    """

    normalized = str(
        role or DEFAULT_ROLE
    ).strip().lower()

    if normalized not in ALLOWED_ROLES:
        normalized = DEFAULT_ROLE

    return normalized


# =========================================================
# USER REPOSITORY
# =========================================================

class UserRepository:

    # =====================================================
    # GET USER BY USERNAME
    # =====================================================

    def get_user_by_username(
        self,
        db: Session,
        username: str,
    ):

        if not username:
            return None

        normalized_username = str(
            username
        ).strip()

        return (
            db.query(User)
            .filter(
                User.username == normalized_username
            )
            .first()
        )

    # =====================================================
    # GET USER BY EMAIL
    # =====================================================

    def get_user_by_email(
        self,
        db: Session,
        email: str,
    ):

        if not email:
            return None

        normalized_email = str(
            email
        ).strip()

        return (
            db.query(User)
            .filter(
                User.email == normalized_email
            )
            .first()
        )

    # =====================================================
    # CREATE USER
    # =====================================================

    def create_user(
        self,
        db: Session,
        username: str,
        email: str,
        password: str,
        role: str = DEFAULT_ROLE,
    ):

        normalized_username = str(
            username
        ).strip()

        normalized_email = str(
            email
        ).strip()

        normalized_role = normalize_role(
            role
        )

        # -------------------------------------------------
        # Basic validation
        # -------------------------------------------------

        if not normalized_username:

            raise ValueError(
                "Username cannot be empty."
            )

        if not normalized_email:

            raise ValueError(
                "Email cannot be empty."
            )

        if not password:

            raise ValueError(
                "Password cannot be empty."
            )

        # -------------------------------------------------
        # Create database user
        # -------------------------------------------------

        user = User(
            username=normalized_username,
            email=normalized_email,
            password=password,
            role=normalized_role,
        )

        try:

            db.add(user)

            db.commit()

            db.refresh(user)

            return user

        except Exception:

            db.rollback()

            raise

    # =====================================================
    # GET ALL USERS
    # =====================================================

    def get_all_users(
        self,
        db: Session,
    ):

        return (
            db.query(User)
            .order_by(User.id.asc())
            .all()
        )

    # =====================================================
    # DELETE USER
    # =====================================================

    def delete_user(
        self,
        db: Session,
        user_id: int,
    ):

        user = (
            db.query(User)
            .filter(
                User.id == user_id
            )
            .first()
        )

        if not user:
            return None

        try:

            db.delete(user)

            db.commit()

            return user

        except Exception:

            db.rollback()

            raise

    # =====================================================
    # UPDATE USER ROLE
    # =====================================================

    def update_user_role(
        self,
        db: Session,
        username: str,
        role: str,
    ):

        if not username:
            return None

        user = (
            db.query(User)
            .filter(
                User.username
                == str(username).strip()
            )
            .first()
        )

        if not user:
            return None

        normalized_role = normalize_role(
            role
        )

        user.role = normalized_role

        try:

            db.commit()

            db.refresh(user)

            return user

        except Exception:

            db.rollback()

            raise


# =========================================================
# SINGLETON REPOSITORY
# =========================================================

user_repository = UserRepository()

