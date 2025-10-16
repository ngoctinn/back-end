"""Business logic cho module auth.

Chứa các hàm độc lập để phục vụ router: đăng ký, đăng nhập, refresh,
đăng xuất, xác minh email, và reset mật khẩu.
"""

import secrets
from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.security import create_jwt_token
from src.core.security import hash_password as _hash_password
from src.core.security import verify_password as _verify_password
from . import crud
from .models import User


def create_access_token_for_user(user: User) -> str:
	"""Tạo access token JWT chứa user_id và roles."""

	subject = {"sub": str(user.id), "roles": user.roles}
	expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	return create_jwt_token(subject, expires)


def create_refresh_token_value() -> str:
	"""Tạo chuỗi refresh token ngẫu nhiên (opaque)."""

	return secrets.token_urlsafe(48)


def register_user(db: Session, email: str, password: str) -> User:
	"""Đăng ký tài khoản mới và tạo token xác minh email."""

	existing = crud.get_user_by_email(db, email)
	if existing:
		raise ValueError("Email đã tồn tại")

	pwd_hash = hash_password(password)
	user = crud.create_user(db, email=email, password_hash=pwd_hash, roles="user")

	# Tạo token xác minh email (opaque) và lưu
	vtoken = create_refresh_token_value()
	crud.create_verification_token(db, user_id=user.id, token=vtoken)
	# Gửi email xác minh: triển khai tích hợp SMTP sau (placeholder)
	return user


def verify_email(db: Session, token: str) -> bool:
	"""Xác minh email nếu token hợp lệ."""

	vt = crud.get_verification_token(db, token)
	if not vt:
		return False
	crud.update_user_active(db, vt.user_id, True)
	crud.delete_verification_token(db, token)
	return True


def login_user(db: Session, email: str, password: str) -> tuple[str, str, User]:
	"""Đăng nhập: trả về (access_token, refresh_token, user)."""

	user = crud.get_user_by_email(db, email)
	if not user or not verify_password(password, user.password_hash):
		raise ValueError("Thông tin đăng nhập không hợp lệ")
	if not user.is_active:
		raise PermissionError("Tài khoản chưa được kích hoạt")

	access_token = create_access_token_for_user(user)
	refresh_token = create_refresh_token_value()
	crud.store_refresh_token(db, user_id=user.id, token=refresh_token)
	return access_token, refresh_token, user


def refresh_access_token(db: Session, refresh_token: str) -> Optional[str]:
	"""Tạo access token mới từ refresh token hợp lệ."""

	rt = crud.is_refresh_token_valid(db, refresh_token)
	if not rt:
		return None

	# Lấy lại user và cấp token
	user = db.get(User, rt.user_id)
	if not user or not user.is_active:
		return None
	return create_access_token_for_user(user)


def logout_user(db: Session, refresh_token: str) -> None:
	"""Đăng xuất: thu hồi refresh token cụ thể."""

	crud.revoke_refresh_token(db, refresh_token)


def request_password_reset(db: Session, email: str) -> None:
	"""Tạo token đặt lại mật khẩu và giả lập gửi email (không lộ thông tin)."""

	user = crud.get_user_by_email(db, email)
	if not user:
		return
	token = create_refresh_token_value()
	crud.create_reset_token(db, user_id=user.id, token=token)
	# TODO: gửi email chứa đường dẫn đặt lại mật khẩu


def reset_password(db: Session, token: str, new_password: str) -> bool:
	"""Đặt lại mật khẩu nếu token hợp lệ và thu hồi mọi refresh token của user."""

	rt = crud.get_reset_token(db, token)
	if not rt:
		return False
	user = db.get(User, rt.user_id)
	if not user:
		return False

	new_hash = hash_password(new_password)
	user.password_hash = new_hash
	db.add(user)
	db.commit()
	crud.revoke_refresh_tokens_of_user(db, user.id)
	crud.delete_reset_token(db, token)
	return True


def hash_password(plain_password: str) -> str:
	"""Wrapper: hash mật khẩu (ủy quyền cho core.security)."""

	return _hash_password(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	"""Wrapper: xác minh mật khẩu (ủy quyền cho core.security)."""

	return _verify_password(plain_password, hashed_password)


def send_verification_email(email: str, token: str) -> None:
	"""Gửi email xác minh (placeholder).

	Thực tế sẽ tích hợp SMTP theo settings. Ở đây chỉ là stub để đáp ứng kế hoạch.
	"""

	# TODO: Tích hợp SMTP để gửi email xác minh
	return None


def send_reset_email(email: str, token: str) -> None:
	"""Gửi email đặt lại mật khẩu (placeholder)."""

	# TODO: Tích hợp SMTP để gửi email đặt lại mật khẩu
	return None
