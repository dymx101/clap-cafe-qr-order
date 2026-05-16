# backend/app/api/v1/admin/auth.py
"""Admin authentication endpoints: login and initial seed."""
from datetime import datetime, timedelta, timezone

from app.core.auth_service import (
    create_access_token,
    get_current_admin,
    hash_password,
    verify_password,
)
from app.core.email_service import (
    generate_reset_token,
    get_reset_link,
    send_password_reset_email,
)
from app.database import get_db
from app.models.admin_user import AdminUser
from app.schemas.admin import (
    AdminLoginRequest,
    AdminTokenResponse,
    AdminUserResponse,
    ForgotPasswordRequest,
    PasswordChangeRequest,
    ResetPasswordRequest,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/login", response_model=AdminTokenResponse)
async def admin_login(
    data: AdminLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate an admin user and return a JWT token."""
    result = await db.execute(select(AdminUser).where(AdminUser.email == data.email))
    admin = result.scalar_one_or_none()

    if not admin or not verify_password(data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    token = create_access_token(
        user_id=str(admin.id),
        email=admin.email,
        role=admin.role,
    )

    return AdminTokenResponse(
        access_token=token,
        admin=AdminUserResponse(
            id=str(admin.id),
            email=admin.email,
            display_name=admin.display_name,
            role=admin.role,
            is_active=admin.is_active,
        ),
    )


@router.get("/me", response_model=AdminUserResponse)
async def admin_me(admin: AdminUser = Depends(get_current_admin)):
    """Return the currently authenticated admin user."""
    return AdminUserResponse(
        id=str(admin.id),
        email=admin.email,
        display_name=admin.display_name,
        role=admin.role,
        is_active=admin.is_active,
    )


@router.post("/change-password")
async def admin_change_password(
    data: PasswordChangeRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Change the current admin user's password."""
    if not verify_password(data.current_password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )
    admin.hashed_password = hash_password(data.new_password)
    await db.commit()
    return {"message": "Password updated successfully"}


_RESET_EXPIRY_HOURS = 1


@router.post("/forgot-password")
async def admin_forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Send a password reset link to the admin email (hardcoded to clapcafe001@gmail.com)."""
    target_email = "clapcafe001@gmail.com"
    if data.email.lower() != target_email:
        # Don't reveal whether the email exists
        return {"message": "If the email is registered, a reset link has been sent."}

    result = await db.execute(select(AdminUser).where(AdminUser.email == target_email))
    admin = result.scalar_one_or_none()
    if not admin or not admin.is_active:
        return {"message": "If the email is registered, a reset link has been sent."}

    token = generate_reset_token()
    admin.password_reset_token = token
    admin.password_reset_expires = datetime.now(timezone.utc) + timedelta(
        hours=_RESET_EXPIRY_HOURS
    )
    await db.commit()

    reset_link = get_reset_link(token, "https://clap-cafe-admin.netlify.app")
    await send_password_reset_email(target_email, reset_link)

    return {"message": "If the email is registered, a reset link has been sent."}


@router.post("/reset-password")
async def admin_reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reset the admin password using a valid reset token."""
    result = await db.execute(
        select(AdminUser).where(AdminUser.password_reset_token == data.token)
    )
    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    if not admin.password_reset_expires or admin.password_reset_expires < datetime.now(
        timezone.utc
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token has expired"
        )

    admin.hashed_password = hash_password(data.new_password)
    admin.password_reset_token = None
    admin.password_reset_expires = None
    await db.commit()

    return {"message": "Password reset successfully"}


@router.post("/debug-reset-password")
async def admin_debug_reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Debug: reset password for clapcafe001@gmail.com. Token not required."""
    result = await db.execute(
        select(AdminUser).where(AdminUser.email == "clapcafe001@gmail.com")
    )
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    admin.hashed_password = hash_password(data.new_password)
    admin.password_reset_token = None
    admin.password_reset_expires = None
    await db.commit()
    return {"message": "Password reset successfully"}


@router.post("/setup", response_model=AdminUserResponse, status_code=201)
async def admin_setup(
    data: AdminLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    One-time setup: create the first admin user.
    Only works when no admin users exist in the database.
    """
    count_result = await db.execute(select(func.count()).select_from(AdminUser))
    count = count_result.scalar()
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admin user already exists. Use /login instead.",
        )

    admin = AdminUser(
        email=data.email,
        hashed_password=hash_password(data.password),
        display_name="Admin",
        role="manager",
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)

    return AdminUserResponse(
        id=str(admin.id),
        email=admin.email,
        display_name=admin.display_name,
        role=admin.role,
        is_active=admin.is_active,
    )
