"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Authentication Router

Handles:
- User Registration
- User Login
- Current User Profile
- Forgot Password
- Reset Password

Author : Feroz Ali
=========================================================
"""

import secrets

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.orm import Session

from backend.database.schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
)

from backend.auth.password import (
    hash_password,
    verify_password,
)

from backend.auth.jwt import create_access_token

from backend.auth.dependencies import get_current_user

from backend.database.database import get_db

from backend.database.repository import user_repository


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# =========================================================
# PASSWORD RESET CONFIGURATION
# =========================================================

PASSWORD_RESET_TOKENS = {}

RESET_TOKEN_EXPIRE_MINUTES = 30


# =========================================================
# REGISTER
# =========================================================

@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):

    username = user.username.strip()

    email = str(user.email).strip().lower()

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username is required",
        )

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Email is required",
        )

    if not user.password:
        raise HTTPException(
            status_code=400,
            detail="Password is required",
        )

    if len(user.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 6 characters",
        )

    existing_user = (
        user_repository.get_user_by_username(
            db,
            username,
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists",
        )

    existing_email = (
        user_repository.get_user_by_email(
            db,
            email,
        )
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    role = str(
        user.role or "Analyst"
    ).strip()

    if not role:
        role = "Analyst"

    hashed_password = hash_password(
        user.password
    )

    try:

        new_user = user_repository.create_user(
            db=db,
            username=username,
            email=email,
            password=hashed_password,
            role=role,
        )

        return new_user

    except Exception as error:

        db.rollback()

        print(
            "REGISTRATION DATABASE ERROR:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to create user account",
        )


# =========================================================
# LOGIN
# =========================================================

@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db),
):

    username = user.username.strip()

    if not username or not user.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    db_user = (
        user_repository.get_user_by_username(
            db,
            username,
        )
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    if not verify_password(
        user.password,
        db_user.password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    role = str(
        db_user.role or "Analyst"
    ).strip()

    if not role:
        role = "Analyst"

    token = create_access_token(
        {
            "sub": db_user.username,
            "role": role,
            "email": db_user.email,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": db_user.username,
            "email": db_user.email,
            "role": role,
        },
    }


# =========================================================
# CURRENT USER
# =========================================================

@router.get("/me")
def profile(
    user: dict = Depends(get_current_user),
):

    return {
        "authenticated": True,
        "user": user,
    }


# =========================================================
# CHANGE PASSWORD
# (authenticated user changing their own password — requires
# the current password as proof, unlike the forgot/reset flow
# which is for users who are locked out)
# =========================================================

@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    current_password = request.current_password
    new_password = request.new_password

    # -----------------------------------------------------
    # Validate new password
    # -----------------------------------------------------

    if not new_password:

        raise HTTPException(
            status_code=400,
            detail="New password is required",
        )

    if len(new_password) < 6:

        raise HTTPException(
            status_code=400,
            detail="New password must contain at least 6 characters",
        )

    # -----------------------------------------------------
    # Load the user record
    # -----------------------------------------------------

    db_user = (
        user_repository.get_user_by_username(
            db,
            current_user.get("username"),
        )
    )

    if not db_user:

        raise HTTPException(
            status_code=404,
            detail="User account not found",
        )

    # -----------------------------------------------------
    # Verify current password
    # -----------------------------------------------------

    if not verify_password(
        current_password,
        db_user.password,
    ):

        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect",
        )

    if current_password == new_password:

        raise HTTPException(
            status_code=400,
            detail="New password must be different from the current password",
        )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    db_user.password = hash_password(new_password)

    try:

        db.commit()

        db.refresh(db_user)

    except Exception as error:

        db.rollback()

        print(
            "CHANGE PASSWORD DATABASE ERROR:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to update password",
        )

    return {
        "success": True,
        "message": "Password changed successfully.",
    }


# =========================================================
# FORGOT PASSWORD
# =========================================================

@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):

    clean_email = (
        str(request.email)
        .strip()
        .lower()
    )

    db_user = (
        user_repository.get_user_by_email(
            db,
            clean_email,
        )
    )

    # Do not reveal whether account exists.

    if not db_user:

        return {
            "message": (
                "If an account exists with this email, "
                "password reset instructions have been sent."
            )
        }

    # -----------------------------------------------------
    # Generate token
    # -----------------------------------------------------

    reset_token = secrets.token_urlsafe(32)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=RESET_TOKEN_EXPIRE_MINUTES
        )
    )

    PASSWORD_RESET_TOKENS[reset_token] = {
        "username": db_user.username,
        "expires_at": expires_at,
    }

    # -----------------------------------------------------
    # CORRECT RESET URL
    # -----------------------------------------------------

    reset_url = (
        "http://localhost:5173/reset-password"
        f"?token={reset_token}"
    )

    # -----------------------------------------------------
    # Development logging
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("PASSWORD RESET REQUEST")
    print("=" * 70)
    print("Email:", clean_email)
    print("Username:", db_user.username)
    print("Reset URL:", reset_url)
    print(
        "Expires in:",
        RESET_TOKEN_EXPIRE_MINUTES,
        "minutes",
    )
    print("=" * 70)
    print()

    return {
        "message": (
            "Password reset instructions generated successfully."
        ),
        "reset_url": reset_url,
        "expires_in_minutes": (
            RESET_TOKEN_EXPIRE_MINUTES
        ),
    }


# =========================================================
# RESET PASSWORD
# =========================================================

@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):

    clean_token = (
        str(request.token or "")
        .strip()
    )

    password = request.password

    # -----------------------------------------------------
    # Validate token
    # -----------------------------------------------------

    if not clean_token:

        raise HTTPException(
            status_code=400,
            detail="Reset token is required",
        )

    # -----------------------------------------------------
    # Validate password
    # -----------------------------------------------------

    if not password:

        raise HTTPException(
            status_code=400,
            detail="New password is required",
        )

    if len(password) < 6:

        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 6 characters",
        )

    # -----------------------------------------------------
    # Find token
    # -----------------------------------------------------

    token_data = PASSWORD_RESET_TOKENS.get(
        clean_token
    )

    if not token_data:

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token",
        )

    # -----------------------------------------------------
    # Check expiration
    # -----------------------------------------------------

    expires_at = token_data.get(
        "expires_at"
    )

    now = datetime.now(timezone.utc)

    if (
        not expires_at
        or now > expires_at
    ):

        PASSWORD_RESET_TOKENS.pop(
            clean_token,
            None,
        )

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token",
        )

    # -----------------------------------------------------
    # Find user
    # -----------------------------------------------------

    username = token_data.get(
        "username"
    )

    if not username:

        PASSWORD_RESET_TOKENS.pop(
            clean_token,
            None,
        )

        raise HTTPException(
            status_code=400,
            detail="Invalid password reset token",
        )

    db_user = (
        user_repository.get_user_by_username(
            db,
            username,
        )
    )

    if not db_user:

        PASSWORD_RESET_TOKENS.pop(
            clean_token,
            None,
        )

        raise HTTPException(
            status_code=404,
            detail="User account not found",
        )

    # -----------------------------------------------------
    # Hash password
    # -----------------------------------------------------

    hashed_password = hash_password(
        password
    )

    db_user.password = hashed_password

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    try:

        db.commit()

        db.refresh(db_user)

    except Exception as error:

        db.rollback()

        print(
            "PASSWORD RESET DATABASE ERROR:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to update password",
        )

    # -----------------------------------------------------
    # Delete token
    # -----------------------------------------------------

    PASSWORD_RESET_TOKENS.pop(
        clean_token,
        None,
    )

    return {
        "message": (
            "Password has been reset successfully."
        )
    }

