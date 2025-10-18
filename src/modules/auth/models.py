"""Các model CSDL cho module auth.

Đã được tái cấu trúc để hỗ trợ RBAC đầy đủ.
"""

from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from src.core.utils import get_utc_now


# --- Bảng liên kết Nhiều-Nhiều ---

class UserRole(SQLModel, table=True):
    """Bảng trung gian liên kết User và Role."""
    user_id: Optional[int] = Field(
        default=None, foreign_key="user.id", primary_key=True
    )
    role_id: Optional[int] = Field(
        default=None, foreign_key="role.id", primary_key=True
    )


class RolePermission(SQLModel, table=True):
    """Bảng trung gian liên kết Role và Permission."""
    role_id: Optional[int] = Field(
        default=None, foreign_key="role.id", primary_key=True
    )
    permission_id: Optional[int] = Field(
        default=None, foreign_key="permission.id", primary_key=True
    )


# --- Bảng chính ---

class Permission(SQLModel, table=True):
    """Bảng Quyền hạn (ví dụ: create_product, delete_user)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True) # Tên quyền hạn
    description: str = Field(default="")

    roles: List["Role"] = Relationship(back_populates="permissions", link_model=RolePermission)


class Role(SQLModel, table=True):
    """Bảng Vai trò (ví dụ: admin, user, staff)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str = Field(default="")

    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole)
    permissions: List[Permission] = Relationship(back_populates="roles", link_model=RolePermission)


class User(SQLModel, table=True):
    """Bảng người dùng phục vụ xác thực."""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)
    is_active: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)

    roles: List[Role] = Relationship(back_populates="users", link_model=UserRole)


# --- Các bảng Token (không thay đổi) ---

class RefreshToken(SQLModel, table=True):
    """Lưu refresh token dạng opaque, có thể thu hồi."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, nullable=False)
    token: str = Field(index=True, unique=True, nullable=False)
    is_revoked: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)


class VerificationToken(SQLModel, table=True):
    """Token xác minh email (one-time use)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, nullable=False)
    token: str = Field(index=True, unique=True, nullable=False)
    expires_at: datetime = Field(nullable=False)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)


class ResetPasswordToken(SQLModel, table=True):
    """Token đặt lại mật khẩu (one-time use)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, nullable=False)
    token: str = Field(index=True, unique=True, nullable=False)
    expires_at: datetime = Field(nullable=False)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)