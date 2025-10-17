"""Các schema Pydantic cho module khách hàng (DTO).

Định nghĩa request/response bodies cho tất cả endpoints.
"""

from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CustomerCreateRequest(BaseModel):
    """Request tạo khách hàng vãng lai."""

    full_name: str = Field(..., min_length=1, max_length=255)
    phone_number: str = Field(..., min_length=9, max_length=20)

    @field_validator("phone_number")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        """Normalize số điện thoại."""
        from src.core.utils import normalize_phone_number

        return normalize_phone_number(v)


class CustomerCompleteProfileRequest(BaseModel):
    """Request hoàn thành hồ sơ khách hàng (Luồng 2b).

    Yêu cầu full_name và phone_number bắt buộc.
    Cho phép cập nhật các fields khác.
    """

    full_name: str = Field(..., min_length=1, max_length=255)
    phone_number: str = Field(..., min_length=9, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=10)
    address: Optional[str] = None
    notes: Optional[str] = None
    skin_type: Optional[str] = Field(None, max_length=50)
    health_conditions: Optional[str] = None

    @field_validator("phone_number")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        """Normalize số điện thoại."""
        from src.core.utils import normalize_phone_number

        return normalize_phone_number(v)


class CustomerUpdateRequest(BaseModel):
    """Request cập nhật thông tin khách hàng."""

    full_name: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, min_length=9, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=10)
    address: Optional[str] = None
    notes: Optional[str] = None
    skin_type: Optional[str] = Field(None, max_length=50)
    health_conditions: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("phone_number")
    @classmethod
    def normalize_phone(cls, v: Optional[str]) -> Optional[str]:
        """Normalize số điện thoại nếu được cung cấp."""
        if v is None:
            return None
        from src.core.utils import normalize_phone_number

        return normalize_phone_number(v)


class CustomerLinkRequest(BaseModel):
    """Request bắt đầu quá trình liên kết tài khoản."""

    phone_number: str = Field(..., min_length=9, max_length=20)


class CustomerVerifyOTPRequest(BaseModel):
    """Request xác minh OTP và hoàn tất liên kết tài khoản."""

    phone_number: str = Field(..., min_length=9, max_length=20)
    otp_code: str = Field(..., min_length=6, max_length=6)


class CustomerResponse(BaseModel):
    """Response thông tin khách hàng."""

    id: int
    user_id: Optional[int]
    full_name: Optional[str]
    phone_number: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    address: Optional[str]
    notes: Optional[str]
    skin_type: Optional[str]
    health_conditions: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    """Response danh sách khách hàng."""

    customers: list[CustomerResponse]
    total: int
    page: int
    per_page: int
