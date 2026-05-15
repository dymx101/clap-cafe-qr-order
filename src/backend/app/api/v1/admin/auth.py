# backend/app/api/v1/admin/auth.py
"""Admin authentication endpoints: login and initial seed."""
from app.core.auth_service import (
    create_access_token,
    get_current_admin,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models.admin_user import AdminUser
from app.schemas.admin import AdminLoginRequest, AdminTokenResponse, AdminUserResponse
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
