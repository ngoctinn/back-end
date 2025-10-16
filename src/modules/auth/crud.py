"""Lớp truy cập dữ liệu (CRUD) cho module auth."""

from typing import Optional

from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from .models import (
	User,
	RefreshToken,
	VerificationToken,
	ResetPasswordToken,
)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
	"""Lấy người dùng theo email."""

	stmt = select(User).where(User.email == email)
	return db.execute(stmt).scalars().first()


def create_user(db: Session, email: str, password_hash: str, roles: str = "user") -> User:
	"""Tạo người dùng mới."""

	user = User(email=email, password_hash=password_hash, roles=roles)
	db.add(user)
	db.commit()
	db.refresh(user)
	return user


def update_user_active(db: Session, user_id: int, is_active: bool) -> None:
	"""Cập nhật trạng thái hoạt động của người dùng."""

	stmt = update(User).where(User.id == user_id).values(is_active=is_active)
	db.execute(stmt)
	db.commit()


def store_refresh_token(db: Session, user_id: int, token: str) -> RefreshToken:
	"""Lưu refresh token cho user."""

	rt = RefreshToken(user_id=user_id, token=token)
	db.add(rt)
	db.commit()
	db.refresh(rt)
	return rt


def is_refresh_token_valid(db: Session, token: str) -> Optional[RefreshToken]:
	"""Kiểm tra refresh token còn hợp lệ (tồn tại và chưa bị revoke)."""

	stmt = select(RefreshToken).where(
		(RefreshToken.token == token) & (RefreshToken.is_revoked.is_(False))
	)
	return db.execute(stmt).scalars().first()


def revoke_refresh_token(db: Session, token: str) -> None:
	"""Thu hồi một refresh token cụ thể."""

	stmt = update(RefreshToken).where(RefreshToken.token == token).values(is_revoked=True)
	db.execute(stmt)
	db.commit()


def revoke_refresh_tokens_of_user(db: Session, user_id: int) -> None:
	"""Thu hồi tất cả refresh token của một người dùng."""

	stmt = update(RefreshToken).where(RefreshToken.user_id == user_id).values(
		is_revoked=True
	)
	db.execute(stmt)
	db.commit()


def create_verification_token(db: Session, user_id: int, token: str) -> VerificationToken:
	vt = VerificationToken(user_id=user_id, token=token)
	db.add(vt)
	db.commit()
	db.refresh(vt)
	return vt


def get_verification_token(db: Session, token: str) -> Optional[VerificationToken]:
	stmt = select(VerificationToken).where(VerificationToken.token == token)
	return db.execute(stmt).scalars().first()


def delete_verification_token(db: Session, token: str) -> None:
	stmt = delete(VerificationToken).where(VerificationToken.token == token)
	db.execute(stmt)
	db.commit()


def create_reset_token(db: Session, user_id: int, token: str) -> ResetPasswordToken:
	rt = ResetPasswordToken(user_id=user_id, token=token)
	db.add(rt)
	db.commit()
	db.refresh(rt)
	return rt


def get_reset_token(db: Session, token: str) -> Optional[ResetPasswordToken]:
	stmt = select(ResetPasswordToken).where(ResetPasswordToken.token == token)
	return db.execute(stmt).scalars().first()


def delete_reset_token(db: Session, token: str) -> None:
	stmt = delete(ResetPasswordToken).where(ResetPasswordToken.token == token)
	db.execute(stmt)
	db.commit()
