"""Business logic cho đăng ký, đăng nhập, đăng xuất và refresh token.

Đã được tái cấu trúc để hỗ trợ transaction và RBAC.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import Session

from src.core.config import settings
from src.core.email import send_verification_email
from src.core.security import create_jwt_token
from src.core.security import hash_password as _hash_password
from src.core.security import verify_password as _verify_password
from src.core.utils import get_expiry_time
from . import crud
from .models import User
from .token_service import create_verification_token_value
from src.modules.customers import service as customer_service


def create_access_token_for_user(user: User) -> str:
    """Tạo access token JWT chứa user_id và danh sách roles."""
    # Lấy danh sách tên các role từ object User
    # Cần đảm bảo các role đã được eager load khi truy vấn user
    roles_list = [role.name for role in user.roles]
    subject = {"sub": str(user.id), "roles": roles_list}
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_jwt_token(subject, expires)


def register_user(db: Session, email: str, password: str) -> dict:
    """Đăng ký tài khoản mới với email verification trong một transaction."""
    # Kiểm tra email không trùng lặp
    if crud.get_user_by_email(db, email):
        raise ValueError("Email đã tồn tại")

    try:
        # 1. Tạo User
        pwd_hash = _hash_password(password)
        user = crud.create_user(db, email=email, password_hash=pwd_hash)
        db.flush() # Flush để user object có ID trước khi gán vào các object khác

        # 2. Gán vai trò 'user' mặc định
        user_role = crud.get_role_by_name(db, name="user")
        if not user_role:
            raise RuntimeError("Vai trò 'user' mặc định không tồn tại trong CSDL.")
        crud.assign_role_to_user(db, user=user, role=user_role)

        # 3. Tạo hồ sơ khách hàng "chờ"
        customer_service.create_online_customer_with_user(db, user_id=user.id)

        # 4. Tạo token xác minh email
        vtoken = create_verification_token_value()
        expires_at = get_expiry_time(settings.VERIFICATION_TOKEN_EXPIRE_HOURS)
        crud.create_verification_token(
            db, user_id=user.id, token=vtoken, expires_at=expires_at
        )

        # Commit tất cả thay đổi vào CSDL
        db.commit()

    except Exception as e:
        # Nếu có bất kỳ lỗi nào, rollback tất cả thay đổi
        db.rollback()
        raise e

    # 5. Gửi email xác minh (chỉ gửi sau khi đã commit thành công)
    send_verification_email(email, vtoken)

    return {
        "id": user.id,
        "email": user.email,
        "message": "Đăng ký thành công. Vui lòng xác minh email",
    }

def login_user(db: Session, email: str, password: str) -> tuple[str, str, User]:
    """Đăng nhập: trả về (access_token, refresh_token, user)."""
    user = crud.get_user_by_email(db, email)
    if not user or not _verify_password(password, user.password_hash):
        raise ValueError("Thông tin đăng nhập không hợp lệ")
    if not user.is_active:
        raise PermissionError("Tài khoản chưa được kích hoạt")

    access_token = create_access_token_for_user(user)
    refresh_token = secrets.token_urlsafe(48)
    crud.store_refresh_token(db, user_id=user.id, token=refresh_token)
    return access_token, refresh_token, user


def refresh_access_token(db: Session, refresh_token: str) -> Optional[str]:
    """Tạo access token mới từ refresh token hợp lệ."""
    rt = crud.is_refresh_token_valid(db, refresh_token)
    if not rt:
        return None

    user = db.get(User, rt.user_id)
    if not user or not user.is_active:
        return None
    return create_access_token_for_user(user)


def logout_user(db: Session, refresh_token: str) -> None:
    """Đăng xuất: thu hồi refresh token cụ thể."""
    crud.revoke_refresh_token(db, refresh_token)