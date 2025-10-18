"""API endpoints cho module auth theo kế hoạch 0002.

Cung cấp các path operations: đăng ký, xác minh email, đăng nhập,
gia hạn, đăng xuất, yêu cầu reset và đặt lại mật khẩu.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status, Cookie
from sqlmodel import Session
from typing import List

from src.core.config import settings
from src.core.db import get_session
from src.core.dependencies import get_current_user, get_admin_user
from . import schemas
from . import auth_service, token_service, crud
from .models import User, Role, Permission


router = APIRouter(prefix="/auth", tags=["Authentication"])
admin_router = APIRouter(
    prefix="/admin", tags=["Admin - RBAC"], dependencies=[Depends(get_admin_user)]
)


# === RBAC Management Endpoints ===


@admin_router.post("/roles", response_model=schemas.RoleRead, status_code=201)
def create_role(role_in: schemas.RoleCreate, db: Session = Depends(get_session)):
    return crud.create_role(db, role_in)


@admin_router.get("/roles", response_model=List[schemas.RoleRead])
def get_all_roles(db: Session = Depends(get_session)):
    return crud.get_all_roles(db)


@admin_router.post(
    "/users/{user_id}/roles/{role_id}", response_model=schemas.UserResponse
)
def assign_role_to_user(user_id: int, role_id: int, db: Session = Depends(get_session)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    role = crud.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Vai trò không tồn tại")
    crud.assign_role_to_user(db, user, role)
    db.commit()
    db.refresh(user)
    return user


@admin_router.delete(
    "/users/{user_id}/roles/{role_id}", response_model=schemas.UserResponse
)
def revoke_role_from_user(
    user_id: int, role_id: int, db: Session = Depends(get_session)
):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    role = crud.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Vai trò không tồn tại")
    crud.revoke_role_from_user(db, user, role)
    db.commit()
    db.refresh(user)
    return user


# (Các endpoint khác cho Permission và Role-Permission có thể thêm tương tự)


# === Endpoints for Permissions ===

@admin_router.post("/permissions", response_model=schemas.PermissionRead, status_code=201)
def create_permission(perm_in: schemas.PermissionCreate, db: Session = Depends(get_session)):
    """Tạo một quyền hạn mới."""
    # Optional: Check for duplicate name
    return crud.create_permission(db, perm_in)

@admin_router.get("/permissions", response_model=List[schemas.PermissionRead])
def get_all_permissions(db: Session = Depends(get_session)):
    """Lấy danh sách tất cả quyền hạn."""
    return crud.get_all_permissions(db)


# === Endpoints for Role-Permission Assignments ===

@admin_router.post("/roles/{role_id}/permissions/{permission_id}", response_model=schemas.RoleReadWithPermissions)
def add_permission_to_role(role_id: int, permission_id: int, db: Session = Depends(get_session)):
    """Gán một quyền cho một vai trò."""
    role = crud.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Vai trò không tồn tại")
    permission = crud.get_permission(db, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Quyền hạn không tồn tại")
    crud.add_permission_to_role(db, role, permission)
    db.refresh(role)
    return role

@admin_router.delete("/roles/{role_id}/permissions/{permission_id}", response_model=schemas.RoleReadWithPermissions)
def remove_permission_from_role(role_id: int, permission_id: int, db: Session = Depends(get_session)):
    """Thu hồi một quyền từ một vai trò."""
    role = crud.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Vai trò không tồn tại")
    permission = crud.get_permission(db, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Quyền hạn không tồn tại")
    crud.remove_permission_from_role(db, role, permission)
    db.refresh(role)
    return role


# === Standard Auth Endpoints ===


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.MessageResponse,
)
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
        return schemas.MessageResponse(message=result["message"], email=result["email"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-email", response_model=schemas.MessageResponse)
def verify_email(
    payload: schemas.VerifyEmailRequest, db: Session = Depends(get_session)
):
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
            message=result["message"], email=result.get("email")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/resend-verification-email", response_model=schemas.MessageResponse)
def resend_verification_email(
    payload: schemas.ResendVerificationEmailRequest, db: Session = Depends(get_session)
):
    """Gửi lại email xác minh cho user dựa trên email.

    Endpoint này không yêu cầu xác thực JWT - chỉ cần email của người dùng.
    Có thể gọi ngay sau khi đăng ký nếu user không nhận được email.

    Args:
            payload: Email của người dùng
            db: Session cơ sở dữ liệu

    Returns:
            MessageResponse thông báo gửi lại email
    """
    try:
        user = crud.get_user_by_email(db, payload.email)
        if not user:
            # Không tiết lộ email có tồn tại hay không vì lý do bảo mật
            return schemas.MessageResponse(
                message="Nếu email tồn tại, email xác minh sẽ được gửi lại",
                email=payload.email,
            )

        # Nếu user đã active, không cần gửi lại
        if user.is_active:
            return schemas.MessageResponse(
                message="Tài khoản của bạn đã được kích hoạt", email=user.email
            )

        # Gửi lại email
        success = token_service.initiate_email_verification(db, user.id)
        if not success:
            raise HTTPException(status_code=500, detail="Lỗi khi gửi email")
        return schemas.MessageResponse(
            message="Email xác minh đã được gửi lại", email=user.email
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")


@router.post("/login", response_model=schemas.TokenResponse)
def login(
    payload: schemas.LoginRequest,
    response: Response,
    db: Session = Depends(get_session),
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
        path="/",
    )
    return schemas.TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=schemas.TokenResponse)
def refresh(
    response: Response,
    db: Session = Depends(get_session),
    refresh_token: str | None = Cookie(
        default=None, alias=settings.REFRESH_TOKEN_COOKIE_NAME
    ),
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
    refresh_token: str | None = Cookie(
        default=None, alias=settings.REFRESH_TOKEN_COOKIE_NAME
    ),
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
    response.delete_cookie(key=settings.REFRESH_TOKEN_COOKIE_NAME, path="/")
    return schemas.MessageResponse(message="Đã đăng xuất")


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Lấy thông tin của người dùng đang đăng nhập.

    Yêu cầu JWT token hợp lệ.
    """
    return schemas.UserResponse(
        id=current_user.id,
        email=current_user.email,
        roles=current_user.roles,  # Trả về list object Role đã được eager load
        is_active=current_user.is_active,
    )


@router.post("/password-reset", response_model=schemas.MessageResponse)
def password_reset(
    payload: schemas.PasswordResetRequest, db: Session = Depends(get_session)
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
    payload: schemas.ConfirmPasswordResetRequest, db: Session = Depends(get_session)
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
        result = token_service.confirm_password_reset(
            db, payload.token, payload.new_password
        )
        return schemas.MessageResponse(
            message=result["message"], email=result.get("email")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
