"""Các model CSDL cho module auth.

Đảm bảo dùng SQLModel với table=True để hỗ trợ Alembic autogenerate.
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
	"""Bảng người dùng phục vụ xác thực (tách biệt domain nghiệp vụ)."""

	id: Optional[int] = Field(default=None, primary_key=True)
	email: str = Field(index=True, unique=True, nullable=False)
	password_hash: str = Field(nullable=False)
	roles: str = Field(default="user", nullable=False)  # lưu chuỗi phân tách bằng dấu phẩy
	is_active: bool = Field(default=False, nullable=False)
	created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class RefreshToken(SQLModel, table=True):
	"""Lưu refresh token dạng opaque, có thể thu hồi theo user.

	- Token lưu dạng chuỗi ngẫu nhiên (UUID/ulid) và có TTL theo app quản lý.
	"""

	id: Optional[int] = Field(default=None, primary_key=True)
	user_id: int = Field(index=True, nullable=False)
	token: str = Field(index=True, unique=True, nullable=False)
	is_revoked: bool = Field(default=False, nullable=False)
	created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class VerificationToken(SQLModel, table=True):
	"""Token xác minh email một lần."""

	id: Optional[int] = Field(default=None, primary_key=True)
	user_id: int = Field(index=True, nullable=False)
	token: str = Field(index=True, unique=True, nullable=False)
	expires_at: datetime = Field(nullable=False)
	created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ResetPasswordToken(SQLModel, table=True):
	"""Token đặt lại mật khẩu một lần."""

	id: Optional[int] = Field(default=None, primary_key=True)
	user_id: int = Field(index=True, nullable=False)
	token: str = Field(index=True, unique=True, nullable=False)
	expires_at: datetime = Field(nullable=False)
	created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
	created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
