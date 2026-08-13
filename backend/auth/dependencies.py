"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Authentication & Authorization Dependencies

Handles:
- JWT authentication
- Current user extraction
- Role normalization
- Single-role authorization
- Multi-role authorization
- Admin/super-admin handling

Author : Feroz Ali
=========================================================
"""

from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.auth.jwt import verify_access_token


# =========================================================
# HTTP BEARER SECURITY
# =========================================================

security = HTTPBearer(
    auto_error=True
)


# =========================================================
# ROLE NORMALIZATION
# =========================================================

def normalize_role(role) -> str:
    """
    Normalize role values so authorization is
    case-insensitive and whitespace-safe.

    Examples:

        Admin       -> admin
        ADMIN       -> admin
        admin       -> admin
        Analyst     -> analyst
        Manager     -> manager
    """

    if role is None:
        return ""

    return str(role).strip().lower()


# =========================================================
# CURRENT USER
# =========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Validate JWT and return authenticated user.

    Returns:

    {
        "username": "...",
        "role": "...",
        "email": "..."
    }
    """

    # -----------------------------------------------------
    # Extract token
    # -----------------------------------------------------

    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # -----------------------------------------------------
    # Verify JWT
    # -----------------------------------------------------

    payload = verify_access_token(token)

    if not payload:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # -----------------------------------------------------
    # Extract JWT data
    # -----------------------------------------------------

    username = payload.get("sub")
    role = payload.get("role")
    email = payload.get("email")

    # -----------------------------------------------------
    # Validate username
    # -----------------------------------------------------

    if not username:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token data",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # -----------------------------------------------------
    # Normalize role
    # -----------------------------------------------------

    normalized_role = normalize_role(role)

    # -----------------------------------------------------
    # Backward compatibility
    #
    # If old tokens don't contain a role, default to
    # analyst rather than crashing the application.
    # -----------------------------------------------------

    if not normalized_role:
        normalized_role = "analyst"

    # -----------------------------------------------------
    # Return authenticated user
    # -----------------------------------------------------

    return {
        "username": username,
        "role": normalized_role,
        "email": email
    }


# =========================================================
# REQUIRE SINGLE ROLE
# =========================================================

def require_role(required_role: str) -> Callable:
    """
    Require a specific role.

    Example:

        @router.get("/admin")
        def admin_page(
            user=Depends(require_role("admin"))
        ):
            return user

    Role comparison is case-insensitive.
    """

    required = normalize_role(required_role)

    def role_checker(
        user: dict = Depends(get_current_user)
    ):

        user_role = normalize_role(
            user.get("role")
        )

        # -------------------------------------------------
        # Validate configuration
        # -------------------------------------------------

        if not required:

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authorization role is not configured"
            )

        # -------------------------------------------------
        # Admin bypass
        #
        # Admin can access protected enterprise resources.
        # -------------------------------------------------

        if user_role in {
            "admin",
            "superadmin",
            "super_admin"
        }:
            return user

        # -------------------------------------------------
        # Required role check
        # -------------------------------------------------

        if user_role != required:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return user

    return role_checker


# =========================================================
# REQUIRE MULTIPLE ROLES
# =========================================================

def require_roles(
    allowed_roles: list
) -> Callable:
    """
    Allow one of several roles.

    Example:

        @router.get("/dashboard")
        def dashboard(
            user=Depends(
                require_roles(
                    ["admin", "manager", "analyst"]
                )
            )
        ):
            return user
    """

    normalized_roles = {
        normalize_role(role)
        for role in allowed_roles
        if role is not None
    }

    def role_checker(
        user: dict = Depends(get_current_user)
    ):

        user_role = normalize_role(
            user.get("role")
        )

        # -------------------------------------------------
        # Validate authorization configuration
        # -------------------------------------------------

        if not normalized_roles:

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authorization roles are not configured"
            )

        # -------------------------------------------------
        # Admin bypass
        # -------------------------------------------------

        if user_role in {
            "admin",
            "superadmin",
            "super_admin"
        }:
            return user

        # -------------------------------------------------
        # Multi-role check
        # -------------------------------------------------

        if user_role not in normalized_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return user

    return role_checker


# =========================================================
# REQUIRE AUTHENTICATED USER
# =========================================================

def require_authenticated_user(
    user: dict = Depends(get_current_user)
):
    """
    Convenience dependency for endpoints that require
    authentication but don't require a specific role.
    """

    return user


# =========================================================
# REQUIRE ADMIN
# =========================================================

def require_admin(
    user: dict = Depends(get_current_user)
):
    """
    Require administrator privileges.
    """

    user_role = normalize_role(
        user.get("role")
    )

    if user_role not in {
        "admin",
        "superadmin",
        "super_admin"
    }:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator permissions required"
        )

    return user