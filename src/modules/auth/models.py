"""Các model CSDL cho module auth.

Đảm bảo dùng SQLModel với table=True để hỗ trợ Alembic autogenerate.
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
	"""Bảng người dùng phục vụ xác thực.

	Tách riêng từ domain nghiệp vụ (customers) để giữ tính độc lập
	của authentication system.

	Attributes:
		id: Primary key
		email: Email duy nhất, indexed (unique constraint)
		password_hash: Mật khẩu đã hash (bcrypt)
		roles: Roles ngăn cách bởi dấu phẩy (ví dụ: "user,admin")
		is_active: True nếu user đã verify email, False nếu chưa
		created_at: Timestamp tạo tài khoản (UTC)
	"""

	id: Optional[int] = Field(default=None, primary_key=True)
	email: str = Field(index=True, unique=True, nullable=False)
	password_hash: str = Field(nullable=False)
	roles: str = Field(default="user", nullable=False)
	is_active: bool = Field(default=False, nullable=False)
	created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class RefreshToken(SQLModel, table=True):
	"""Lưu refresh token dạng opaque, có thể thu hồi.

	Refresh token lưu dạng chuỗi ngẫu nhiên (UUID), không phải JWT.
	TTL quản lý bằng app (REFRESH_TOKEN_EXPIRE_DAYS), không lưu trong DB.

	Attributes:
		id: Primary key
		user_id: Foreign key tới User table
		token: Chuỗi token ngẫu nhiên (secrets.token_urlsafe(48))
		is_revoked: True nếu đã thu hồi (logout)
		created_at: Timestamp tạo token (UTC)
	"""

	id: Optional[int] = Field(default=None, primary_key=True)
	user_id: int = Field(index=True, nullable=False)
	token: str = Field(index=True, unique=True, nullable=False)
	is_revoked: bool = Field(default=False, nullable=False)
	created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class VerificationToken(SQLModel, table=True):
	"""Token xác minh email (one-time use).

	Khi user đăng ký, token này được tạo và gửi qua email.
	User click link trong email → backend kiểm tra token → active account.

	Attributes:
		id: Primary key
		user_id: Foreign key tới User table
		token: Chuỗi token ngẫu nhiên (secrets.token_urlsafe(32))
		expires_at: Thời điểm hết hạn (TTL 24 giờ)
		created_at: Timestamp tạo token (UTC)
	"""

	id: Optional[int] = Field(default=None, primary_key=True)
	user_id: int = Field(index=True, nullable=False)
	token: str = Field(index=True, unique=True, nullable=False)
	expires_at: datetime = Field(nullable=False)
	created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ResetPasswordToken(SQLModel, table=True):
	"""Token đặt lại mật khẩu (one-time use).

	Khi user quên mật khẩu, token này được tạo và gửi qua email.
	User click link → backend kiểm tra token → submit password mới.

	Attributes:
		id: Primary key
		user_id: Foreign key tới User table
		token: Chuỗi token ngẫu nhiên (secrets.token_urlsafe(32))
		expires_at: Thời điểm hết hạn (TTL 1 giờ)
		created_at: Timestamp tạo token (UTC)
	"""

	id: Optional[int] = Field(default=None, primary_key=True)
	user_id: int = Field(index=True, nullable=False)
	token: str = Field(index=True, unique=True, nullable=False)
	expires_at: datetime = Field(nullable=False)
	created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
