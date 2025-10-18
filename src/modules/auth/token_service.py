"""Business logic cho quản lý token email verification và password reset.

Tách riêng logic token handling để cải thiện maintainability.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlmodel import Session

from src.core.config import settings
from src.core.email import send_verification_email, send_password_reset_email
from src.core.security import hash_password as _hash_password
from src.core.security import verify_password as _verify_password
from src.core.utils import get_utc_now, get_expiry_time, is_token_expired
from . import crud
from .models import User, VerificationToken, ResetPasswordToken


def create_verification_token_value() -> str:
    """Tạo token xác minh email ngẫu nhiên."""

    return secrets.token_urlsafe(32)


def create_reset_token_value() -> str:
    """Tạo token đặt lại mật khẩu ngẫu nhiên."""

    return secrets.token_urlsafe(32)


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
    old_token = db.exec(stmt).scalars().first()
    if old_token:
        crud.delete_verification_token(db, old_token.token)

    # Tạo token mới
    vtoken = create_verification_token_value()
    expires_at = get_expiry_time(settings.VERIFICATION_TOKEN_EXPIRE_HOURS)
    crud.create_verification_token(
        db, user_id=user_id, token=vtoken, expires_at=expires_at
    )

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
    if is_token_expired(vt.expires_at):
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

    return {"message": "Email xác minh thành công", "email": user.email}


def initiate_password_reset(db: Session, email: str) -> bool:
    """Tạo token đặt lại mật khẩu và gửi email.

    Delay ngẫu nhiên nếu email không tồn tại (chống enumeration attack).

    Args:
            db: Session cơ sở dữ liệu
            email: Email người dùng

    Returns:
            True (luôn trả True để chống enumeration)
    """
    import random
    import time

    user = crud.get_user_by_email(db, email)
    if not user:
        # Delay ngẫu nhiên 1-2 giây để chống enumeration
        time.sleep(random.uniform(1, 2))
        return True

    # Xóa token cũ nếu tồn tại
    stmt = select(ResetPasswordToken).where(ResetPasswordToken.user_id == user.id)
    old_token = db.exec(stmt).scalars().first()
    if old_token:
        crud.delete_reset_token(db, old_token.token)

    # Tạo reset token mới
    reset_token = create_reset_token_value()
    expires_at = get_expiry_time(settings.RESET_TOKEN_EXPIRE_HOURS)
    crud.create_reset_token(
        db, user_id=user.id, token=reset_token, expires_at=expires_at
    )

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
    if is_token_expired(rt.expires_at):
        crud.delete_reset_token(db, token)
        raise ValueError("Link không hợp lệ hoặc đã hết hạn")

    user = db.get(User, rt.user_id)
    if not user:
        raise ValueError("Người dùng không tồn tại")

    # Validate password mới
    if len(new_password) < 8:
        raise ValueError("Mật khẩu phải có ít nhất 8 ký tự")

    # Hash password mới
    new_hash = _hash_password(new_password)
    user.password_hash = new_hash
    db.add(user)
    db.commit()

    # Thu hồi tất cả refresh token cũ
    crud.revoke_refresh_tokens_of_user(db, user.id)

    # Xóa reset token
    crud.delete_reset_token(db, token)

    return {"message": "Mật khẩu đã được đặt lại thành công", "email": user.email}
