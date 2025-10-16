"""Business logic cho module auth.

Chứa các hàm độc lập để phục vụ router: đăng ký, đăng nhập, refresh,
đăng xuất, xác minh email, và reset mật khẩu.
"""

import secrets
import time
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.email import send_verification_email, send_password_reset_email
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


def create_verification_token_value() -> str:
	"""Tạo token xác minh email ngẫu nhiên."""

	return secrets.token_urlsafe(32)


def hash_password(plain_password: str) -> str:
	"""Wrapper: hash mật khẩu (ủy quyền cho core.security)."""

	return _hash_password(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	"""Wrapper: xác minh mật khẩu (ủy quyền cho core.security)."""

	return _verify_password(plain_password, hashed_password)


def register_user(db: Session, email: str, password: str) -> dict:
	"""Đăng ký tài khoản mới với email verification.

	Args:
		db: Session cơ sở dữ liệu
		email: Email người dùng
		password: Mật khẩu plain text

	Returns:
		Dict chứa thông tin người dùng và trạng thái

	Raises:
		ValueError: Nếu email đã tồn tại
	"""
	# Kiểm tra email không trùng lặp
	existing = crud.get_user_by_email(db, email)
	if existing:
		raise ValueError("Email đã tồn tại")

	# Hash password và tạo user
	pwd_hash = hash_password(password)
	user = crud.create_user(db, email=email, password_hash=pwd_hash, roles="user")

	# Tạo token xác minh email với hạn hết
	vtoken = create_verification_token_value()
	expires_at = datetime.utcnow() + timedelta(
		hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS
	)
	crud.create_verification_token(db, user_id=user.id, token=vtoken, expires_at=expires_at)

	# Gửi email xác minh
	send_verification_email(email, vtoken)

	return {
		"id": user.id,
		"email": user.email,
		"message": "Đăng ký thành công. Vui lòng xác minh email"
	}


def initiate_email_verification(db: Session, user_id: int) -> bool:
	"""Khởi tạo lại quá trình xác minh email (gửi lại email).

	Args:
		db: Session cơ sở dữ liệu
		user_id: ID người dùng cần xác minh lại

	Returns:
		True nếu gửi thành công
	"""
	user = db.get(User, user_id)
	if not user:
		return False

	# Xóa token cũ nếu tồn tại
	stmt = select(VerificationToken).where(VerificationToken.user_id == user_id)
	old_token = db.execute(stmt).scalars().first()
	if old_token:
		crud.delete_verification_token(db, old_token.token)

	# Tạo token mới
	vtoken = create_verification_token_value()
	expires_at = datetime.utcnow() + timedelta(
		hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS
	)
	crud.create_verification_token(db, user_id=user_id, token=vtoken, expires_at=expires_at)

	# Gửi email
	return send_verification_email(user.email, vtoken)


def confirm_email(db: Session, token: str) -> dict:
	"""Xác minh email từ token.

	Args:
		db: Session cơ sở dữ liệu
		token: Token xác minh từ email

	Returns:
		Dict chứa thông tin xác minh

	Raises:
		ValueError: Nếu token invalid, hết hạn, hoặc không tồn tại
	"""
	vt = crud.get_verification_token(db, token)
	if not vt:
		raise ValueError("Link không hợp lệ hoặc đã hết hạn")

	# Kiểm tra token chưa hết hạn
	if vt.expires_at < datetime.utcnow():
		crud.delete_verification_token(db, token)
		raise ValueError("Link không hợp lệ hoặc đã hết hạn")

	# Cập nhật user
	user = db.get(User, vt.user_id)
	if not user:
		raise ValueError("Người dùng không tồn tại")

	user.is_active = True
	db.add(user)
	db.commit()

	# Xóa token
	crud.delete_verification_token(db, token)

	return {
		"message": "Email xác minh thành công",
		"email": user.email
	}


def login_user(db: Session, email: str, password: str) -> tuple[str, str, User]:
	"""Đăng nhập: trả về (access_token, refresh_token, user).

	Args:
		db: Session cơ sở dữ liệu
		email: Email người dùng
		password: Mật khẩu plain text

	Returns:
		Tuple chứa (access_token, refresh_token, user_object)

	Raises:
		ValueError: Nếu email/password không hợp lệ
		PermissionError: Nếu tài khoản chưa được kích hoạt
	"""
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
	"""Tạo access token mới từ refresh token hợp lệ.

	Args:
		db: Session cơ sở dữ liệu
		refresh_token: Refresh token từ cookie

	Returns:
		Access token mới hoặc None nếu invalid
	"""
	rt = crud.is_refresh_token_valid(db, refresh_token)
	if not rt:
		return None

	# Lấy lại user và cấp token
	user = db.get(User, rt.user_id)
	if not user or not user.is_active:
		return None
	return create_access_token_for_user(user)


def logout_user(db: Session, refresh_token: str) -> None:
	"""Đăng xuất: thu hồi refresh token cụ thể.

	Args:
		db: Session cơ sở dữ liệu
		refresh_token: Refresh token cần thu hồi
	"""
	crud.revoke_refresh_token(db, refresh_token)


def initiate_password_reset(db: Session, email: str) -> bool:
	"""Tạo token đặt lại mật khẩu và gửi email.

	Delay ngẫu nhiên nếu email không tồn tại (chống enumeration attack).

	Args:
		db: Session cơ sở dữ liệu
		email: Email người dùng

	Returns:
		True (luôn trả True để chống enumeration)
	"""
	user = crud.get_user_by_email(db, email)
	if not user:
		# Delay ngẫu nhiên 1-2 giây để chống enumeration
		time.sleep(__import__('random').uniform(1, 2))
		return True

	# Xóa token cũ nếu tồn tại
	stmt = select(ResetPasswordToken).where(ResetPasswordToken.user_id == user.id)
	old_token = db.execute(stmt).scalars().first()
	if old_token:
		crud.delete_reset_token(db, old_token.token)

	# Tạo reset token mới
	reset_token = create_verification_token_value()
	expires_at = datetime.utcnow() + timedelta(
		hours=settings.RESET_TOKEN_EXPIRE_HOURS
	)
	crud.create_reset_token(db, user_id=user.id, token=reset_token, expires_at=expires_at)

	# Gửi email
	send_password_reset_email(user.email, reset_token)

	return True


def confirm_password_reset(db: Session, token: str, new_password: str) -> dict:
	"""Đặt lại mật khẩu từ token reset.

	Args:
		db: Session cơ sở dữ liệu
		token: Token đặt lại mật khẩu
		new_password: Mật khẩu mới plain text

	Returns:
		Dict chứa thông tin reset thành công

	Raises:
		ValueError: Nếu token invalid, hết hạn, hoặc password không hợp lệ
	"""
	rt = crud.get_reset_token(db, token)
	if not rt:
		raise ValueError("Link không hợp lệ hoặc đã hết hạn")

	# Kiểm tra token chưa hết hạn
	if rt.expires_at < datetime.utcnow():
		crud.delete_reset_token(db, token)
		raise ValueError("Link không hợp lệ hoặc đã hết hạn")

	user = db.get(User, rt.user_id)
	if not user:
		raise ValueError("Người dùng không tồn tại")

	# Validate password mới
	if len(new_password) < 8:
		raise ValueError("Mật khẩu phải có ít nhất 8 ký tự")

	# Hash password mới
	new_hash = hash_password(new_password)
	user.password_hash = new_hash
	db.add(user)
	db.commit()

	# Thu hồi tất cả refresh token cũ
	crud.revoke_refresh_tokens_of_user(db, user.id)

	# Xóa reset token
	crud.delete_reset_token(db, token)

	return {
		"message": "Mật khẩu đã được đặt lại thành công",
		"email": user.email
	}


# Import các model khi cần dùng trong hàm
from .models import VerificationToken, ResetPasswordToken
from sqlalchemy import select