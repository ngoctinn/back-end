"""Định nghĩa schema (Pydantic) cho các luồng xác thực."""

from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# --- RBAC Schemas ---

class PermissionBase(BaseModel):
    name: str
    description: str = ""

class PermissionCreate(PermissionBase):
    pass

class PermissionRead(PermissionBase):
    id: int

class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class RoleBase(BaseModel):
    name: str
    description: str = ""

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class RoleRead(RoleBase):
    id: int

class RoleReadWithPermissions(RoleRead):
    permissions: List[PermissionRead] = []


# --- Auth Schemas ---

class RegisterRequest(BaseModel):
    """Yêu cầu đăng ký tài khoản mới."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Yêu cầu đăng nhập."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Phản hồi trả về Access Token khi đăng nhập/gia hạn."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Thông tin người dùng cơ bản để phản hồi."""

    id: int
    email: EmailStr
    roles: List[RoleRead] # Cập nhật để trả về object Role chi tiết
    is_active: bool

    class Config:
        from_attributes = True


class VerifyEmailRequest(BaseModel):
    """Yêu cầu xác minh email."""

    token: str = Field(min_length=32)


class ResendVerificationEmailRequest(BaseModel):
    """Yêu cầu gửi lại email xác minh."""

    email: EmailStr


class PasswordResetRequest(BaseModel):
    """Yêu cầu đặt lại mật khẩu (bước 1: gửi email)."""

    email: EmailStr


class ConfirmPasswordResetRequest(BaseModel):
    """Yêu cầu xác nhận đặt lại mật khẩu (bước 2: confirm + password mới)."""

    token: str = Field(min_length=32)
    new_password: str = Field(min_length=8, max_length=128)


class MessageResponse(BaseModel):
    """Phản hồi tin nhắn chung."""

    message: str
    email: Optional[EmailStr] = None
