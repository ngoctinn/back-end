"""Business logic cho đăng ký, đăng nhập, đăng xuất và refresh token.

Tách riêng logic xác thực để cải thiện maintainability.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.email import send_verification_email
from src.core.security import create_jwt_token
from src.core.security import hash_password as _hash_password
from src.core.security import verify_password as _verify_password
from src.core.utils import get_expiry_time
from . import crud
from .models import User
from .token_service import create_verification_token_value


def create_access_token_for_user(user: User) -> str:
    """Tạo access token JWT chứa user_id và roles."""

    subject = {"sub": str(user.id), "roles": user.roles}
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_jwt_token(subject, expires)


def create_refresh_token_value() -> str:
    """Tạo chuỗi refresh token ngẫu nhiên (opaque)."""

    return secrets.token_urlsafe(48)


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
    expires_at = get_expiry_time(settings.VERIFICATION_TOKEN_EXPIRE_HOURS)
    crud.create_verification_token(
        db, user_id=user.id, token=vtoken, expires_at=expires_at
    )

    # Gửi email xác minh
    send_verification_email(email, vtoken)

    return {
        "id": user.id,
        "email": user.email,
        "message": "Đăng ký thành công. Vui lòng xác minh email",
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
