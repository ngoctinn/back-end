"""API endpoints cho module auth theo kế hoạch 0001.

Cung cấp các path operations: đăng ký, xác minh email, đăng nhập,
gia hạn, đăng xuất, yêu cầu reset và đặt lại mật khẩu.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status, Cookie
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.db import get_session
from . import schemas, service


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_session)):
	"""Đăng ký tài khoản mới, gửi email xác minh (giả lập)."""

	try:
		user = service.register_user(db, payload.email, payload.password)
		return {"message": "Đăng ký thành công. Vui lòng kiểm tra email để xác minh."}
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_session)):
	"""Xác minh email từ token trong liên kết."""

	ok = service.verify_email(db, token)
	if not ok:
		raise HTTPException(status_code=400, detail="Token không hợp lệ hoặc đã dùng")
	return {"message": "Tài khoản đã được kích hoạt"}


@router.post("/login", response_model=schemas.TokenResponse)
def login(
	payload: schemas.LoginRequest, response: Response, db: Session = Depends(get_session)
):
	"""Đăng nhập, trả Access Token và set Refresh Token vào HTTP-only cookie."""

	try:
		access_token, refresh_token, user = service.login_user(
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

	Lưu ý: FastAPI không tự động lấy cookie nếu không chỉ định. Ở đây
	dùng tham số `refresh_token` làm placeholder; trong thực tế có thể dùng
	`Cookie` dependency để lấy từ cookie. Để đơn giản, tạm lấy từ header hoặc body nếu FE gửi.
	"""

	if not refresh_token:
		raise HTTPException(status_code=401, detail="Thiếu refresh token")

	new_access = service.refresh_access_token(db, refresh_token)
	if not new_access:
		raise HTTPException(status_code=401, detail="Refresh token không hợp lệ")
	return schemas.TokenResponse(access_token=new_access)


@router.post("/logout")
def logout(
	response: Response,
	db: Session = Depends(get_session),
	refresh_token: str | None = Cookie(default=None, alias=settings.REFRESH_TOKEN_COOKIE_NAME),
):
	"""Đăng xuất: thu hồi refresh token và xóa cookie."""

	if refresh_token:
		service.logout_user(db, refresh_token)
	# Xóa cookie trên trình duyệt
	response.delete_cookie(key=settings.REFRESH_TOKEN_COOKIE_NAME, path="/auth")
	return {"message": "Đã đăng xuất"}


@router.post("/password-reset-request")
def password_reset_request(email: str, db: Session = Depends(get_session)):
	"""Yêu cầu đặt lại mật khẩu (không tiết lộ thông tin tồn tại tài khoản)."""

	service.request_password_reset(db, email)
	return {"message": "Nếu tài khoản tồn tại, email hướng dẫn đã được gửi."}


@router.post("/password-reset")
def password_reset(token: str, new_password: str, db: Session = Depends(get_session)):
	"""Đặt lại mật khẩu bằng token hợp lệ."""

	ok = service.reset_password(db, token, new_password)
	if not ok:
		raise HTTPException(status_code=400, detail="Token không hợp lệ")
	return {"message": "Mật khẩu đã được cập nhật"}
