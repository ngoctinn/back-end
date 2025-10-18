"""Lớp truy cập dữ liệu (CRUD) cho module auth.

Đã được tái cấu trúc để hỗ trợ RBAC.
"""

from typing import Optional, List
from datetime import datetime, timedelta

from sqlmodel import Session, select, update, delete

from . import schemas # Thêm import này
from src.core.utils import get_utc_now
from .models import (
    User,
    Role,
    Permission, # Thêm Permission
    RefreshToken,
    VerificationToken,
    ResetPasswordToken,
)


# --- User CRUD ---

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Lấy người dùng theo ID."""
    return db.get(User, user_id)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Lấy người dùng theo email."""
    statement = select(User).where(User.email == email)
    return db.exec(statement).first()

def create_user(db: Session, email: str, password_hash: str) -> User:
    """Tạo người dùng mới (không gán vai trò và không commit)."""
    user = User(email=email, password_hash=password_hash)
    db.add(user)
    return user

def update_user_active(db: Session, user_id: int, is_active: bool) -> None:
    """Cập nhật trạng thái hoạt động của người dùng."""
    stmt = update(User).where(User.id == user_id).values(is_active=is_active)
    db.exec(stmt)
    db.commit()


# --- Role & Permission CRUD ---

def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    """Lấy vai trò theo tên."""
    statement = select(Role).where(Role.name == name)
    return db.exec(statement).first()


def assign_role_to_user(db: Session, user: User, role: Role):
    """Gán một vai trò cho người dùng (không commit)."""
    # Tránh gán trùng lặp
    if role not in user.roles:
        user.roles.append(role)
        db.add(user)

def revoke_role_from_user(db: Session, user: User, role: Role):
    """Thu hồi vai trò từ người dùng (không commit)."""
    if role in user.roles:
        user.roles.remove(role)
        db.add(user)

def create_role(db: Session, role_in: schemas.RoleCreate) -> Role:
    """Tạo vai trò mới."""
    db_role = Role.model_validate(role_in)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def get_role(db: Session, role_id: int) -> Optional[Role]:
    """Lấy vai trò theo ID."""
    return db.get(Role, role_id)

def get_all_roles(db: Session) -> List[Role]:
    """Lấy tất cả vai trò."""
    return db.exec(select(Role)).all()

def update_role(db: Session, db_role: Role, role_in: schemas.RoleUpdate) -> Role:
    """Cập nhật vai trò."""
    update_data = role_in.model_dump(exclude_unset=True)
    db_role.sqlmodel_update(update_data)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: int):
    """Xóa vai trò."""
    role = db.get(Role, role_id)
    if role:
        db.delete(role)
        db.commit()

def add_permission_to_role(db: Session, role: Role, permission: Permission):
    """Gán quyền cho vai trò."""
    if permission not in role.permissions:
        role.permissions.append(permission)
        db.add(role)
        db.commit()

def remove_permission_from_role(db: Session, role: Role, permission: Permission):
    """Thu hồi quyền từ vai trò."""
    if permission in role.permissions:
        role.permissions.remove(permission)
        db.add(role)
        db.commit()


# --- Permission CRUD ---

def create_permission(db: Session, perm_in: schemas.PermissionCreate) -> Permission:
    """Tạo quyền hạn mới."""
    db_perm = Permission.model_validate(perm_in)
    db.add(db_perm)
    db.commit()
    db.refresh(db_perm)
    return db_perm

def get_permission(db: Session, permission_id: int) -> Optional[Permission]:
    """Lấy quyền hạn theo ID."""
    return db.get(Permission, permission_id)

def get_all_permissions(db: Session) -> List[Permission]:
    """Lấy tất cả quyền hạn."""
    return db.exec(select(Permission)).all()

def update_permission(db: Session, db_perm: Permission, perm_in: schemas.PermissionUpdate) -> Permission:
    """Cập nhật quyền hạn."""
    update_data = perm_in.model_dump(exclude_unset=True)
    db_perm.sqlmodel_update(update_data)
    db.add(db_perm)
    db.commit()
    db.refresh(db_perm)
    return db_perm

def delete_permission(db: Session, permission_id: int):
    """Xóa quyền hạn."""
    permission = db.get(Permission, permission_id)
    if permission:
        db.delete(permission)
        db.commit()


# --- Token CRUD ---

def store_refresh_token(db: Session, user_id: int, token: str) -> RefreshToken:
    """Lưu refresh token cho user."""
    rt = RefreshToken(user_id=user_id, token=token)
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt

def is_refresh_token_valid(db: Session, token: str) -> Optional[RefreshToken]:
    """Kiểm tra refresh token còn hợp lệ."""
    stmt = select(RefreshToken).where(
        (RefreshToken.token == token) & (RefreshToken.is_revoked.is_(False))
    )
    return db.exec(stmt).first()

def revoke_refresh_token(db: Session, token: str) -> None:
    """Thu hồi một refresh token cụ thể."""
    stmt = update(RefreshToken).where(RefreshToken.token == token).values(is_revoked=True)
    db.exec(stmt)
    db.commit()

def revoke_refresh_tokens_of_user(db: Session, user_id: int) -> None:
    """Thu hồi tất cả refresh token của một người dùng."""
    stmt = update(RefreshToken).where(RefreshToken.user_id == user_id).values(is_revoked=True)
    db.exec(stmt)
    db.commit()


def create_verification_token(
    db: Session, user_id: int, token: str, expires_at: datetime
) -> VerificationToken:
    """Tạo và lưu token xác minh email (không commit)."""
    vt = VerificationToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(vt)
    return vt

def get_verification_token(db: Session, token: str) -> Optional[VerificationToken]:
    """Lấy token xác minh từ DB."""
    stmt = select(VerificationToken).where(VerificationToken.token == token)
    return db.exec(stmt).first()

def delete_verification_token(db: Session, token: str) -> None:
    """Xóa token xác minh sau khi xác thực thành công."""
    stmt = delete(VerificationToken).where(VerificationToken.token == token)
    db.exec(stmt)
    db.commit()


def create_reset_token(
    db: Session, user_id: int, token: str, expires_at: datetime
) -> ResetPasswordToken:
    """Tạo và lưu token đặt lại mật khẩu."""
    rt = ResetPasswordToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt

def get_reset_token(db: Session, token: str) -> Optional[ResetPasswordToken]:
    """Lấy token đặt lại mật khẩu từ DB."""
    stmt = select(ResetPasswordToken).where(ResetPasswordToken.token == token)
    return db.exec(stmt).first()

def delete_reset_token(db: Session, token: str) -> None:
    """Xóa token đặt lại mật khẩu sau khi sử dụng thành công."""
    stmt = delete(ResetPasswordToken).where(ResetPasswordToken.token == token)
    db.exec(stmt)
    db.commit()