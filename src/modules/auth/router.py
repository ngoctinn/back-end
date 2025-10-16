"""API endpoints cho module auth theo kế hoạch 0002.

Cung cấp các path operations: đăng ký, xác minh email, đăng nhập,
gia hạn, đăng xuất, yêu cầu reset và đặt lại mật khẩu.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status, Cookie
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.db import get_session
from src.core.dependencies import get_current_user
from . import schemas
from . import auth_service, token_service
from .models import User


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.MessageResponse)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_session)):
	"""Đăng ký tài khoản mới, gửi email xác minh.

	Args:
		payload: Email và mật khẩu người dùng
		db: Session cơ sở dữ liệu

	Returns:
		MessageResponse với thông tin đăng ký thành công
	"""
	try:
		result = auth_service.register_user(db, payload.email, payload.password)
		return schemas.MessageResponse(
			message=result["message"],
			email=result["email"]
		)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-email", response_model=schemas.MessageResponse)
def verify_email(payload: schemas.VerifyEmailRequest, db: Session = Depends(get_session)):
	"""Xác minh email từ token gửi trong email.

	Args:
		payload: Token xác minh từ email link
		db: Session cơ sở dữ liệu

	Returns:
		MessageResponse thông báo xác minh thành công
	"""
	try:
		result = token_service.confirm_email(db, payload.token)
		return schemas.MessageResponse(
			message=result["message"],
			email=result.get("email")
		)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/resend-verification-email", response_model=schemas.MessageResponse)
def resend_verification_email(
	db: Session = Depends(get_session),
	current_user: User = Depends(get_current_user)
):
	"""Gửi lại email xác minh cho user hiện tại.

	Endpoint này yêu cầu xác thực với JWT Bearer token.

	Args:
		db: Session cơ sở dữ liệu
		current_user: User hiện tại từ JWT

	Returns:
		MessageResponse thông báo gửi lại email
	"""
	try:
		success = token_service.initiate_email_verification(db, current_user.id)
		if not success:
			raise HTTPException(status_code=500, detail="Lỗi khi gửi email")
		return schemas.MessageResponse(
			message="Email xác minh đã được gửi lại",
			email=current_user.email
		)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")


@router.post("/login", response_model=schemas.TokenResponse)
def login(
	payload: schemas.LoginRequest,
	response: Response,
	db: Session = Depends(get_session)
):
	"""Đăng nhập, trả Access Token và set Refresh Token vào HTTP-only cookie.

	Args:
		payload: Email và mật khẩu
		response: Response object để set cookie
		db: Session cơ sở dữ liệu

	Returns:
		TokenResponse chứa access token
	"""
	try:
		access_token, refresh_token, user = auth_service.login_user(
			db, payload.email, payload.password
		)
	except ValueError as e:
		raise HTTPException(status_code=401, detail=str(e))
	except PermissionError as e:
		raise HTTPException(status_code=403, detail=str(e))

	# Set cookie HTTP-only cho refresh token
	response.set_cookie(
		key=settings.REFRESH_TOKEN_COOKIE_NAME,
		value=refresh_token,
		httponly=True,
		samesite="lax",
		secure=False,
		max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
		path="/auth",
	)
	return schemas.TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=schemas.TokenResponse)
def refresh(
	response: Response,
	db: Session = Depends(get_session),
	refresh_token: str | None = Cookie(default=None, alias=settings.REFRESH_TOKEN_COOKIE_NAME),
):
	"""Gia hạn Access Token dựa trên Refresh Token từ cookie.

	Args:
		response: Response object
		db: Session cơ sở dữ liệu
		refresh_token: Refresh token từ cookie

	Returns:
		TokenResponse chứa access token mới
	"""
	if not refresh_token:
		raise HTTPException(status_code=401, detail="Thiếu refresh token")

	new_access = auth_service.refresh_access_token(db, refresh_token)
	if not new_access:
		raise HTTPException(status_code=401, detail="Refresh token không hợp lệ")
	return schemas.TokenResponse(access_token=new_access)


@router.post("/logout", response_model=schemas.MessageResponse)
def logout(
	response: Response,
	db: Session = Depends(get_session),
	refresh_token: str | None = Cookie(default=None, alias=settings.REFRESH_TOKEN_COOKIE_NAME),
):
	"""Đăng xuất: thu hồi refresh token và xóa cookie.

	Args:
		response: Response object để xóa cookie
		db: Session cơ sở dữ liệu
		refresh_token: Refresh token từ cookie

	Returns:
		MessageResponse thông báo đăng xuất thành công
	"""
	if refresh_token:
		auth_service.logout_user(db, refresh_token)
	# Xóa cookie trên trình duyệt
	response.delete_cookie(key=settings.REFRESH_TOKEN_COOKIE_NAME, path="/auth")
	return schemas.MessageResponse(message="Đã đăng xuất")


@router.post("/password-reset", response_model=schemas.MessageResponse)
def password_reset(
	payload: schemas.PasswordResetRequest,
	db: Session = Depends(get_session)
):
	"""Yêu cầu đặt lại mật khẩu (bước 1: gửi email).

	Không tiết lộ thông tin tồn tại tài khoản (luôn trả success).

	Args:
		payload: Email của tài khoản
		db: Session cơ sở dữ liệu

	Returns:
		MessageResponse thông báo email đã được gửi
	"""
	token_service.initiate_password_reset(db, payload.email)
	return schemas.MessageResponse(
		message="Nếu tài khoản tồn tại, email hướng dẫn đã được gửi"
	)


@router.post("/confirm-password-reset", response_model=schemas.MessageResponse)
def confirm_password_reset(
	payload: schemas.ConfirmPasswordResetRequest,
	db: Session = Depends(get_session)
):
	"""Xác nhận đặt lại mật khẩu (bước 2: verify token + password mới).

	Args:
		payload: Token từ email + mật khẩu mới
		db: Session cơ sở dữ liệu

	Returns:
		MessageResponse thông báo mật khẩu đã được đặt lại

	Raises:
		HTTPException 400: Nếu token invalid, hết hạn, hoặc password không hợp lệ
	"""
	try:
		result = token_service.confirm_password_reset(db, payload.token, payload.new_password)
		return schemas.MessageResponse(
			message=result["message"],
			email=result.get("email")
		)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))