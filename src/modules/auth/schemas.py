"""Định nghĩa schema (Pydantic) cho các luồng xác thực."""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


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
    roles: list[str]
    is_active: bool


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
