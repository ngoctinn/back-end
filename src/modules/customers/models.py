"""Các model CSDL cho module khách hàng.

Định nghĩa bảng Customer (hồ sơ CRM) độc lập với User (xác thực).
Cho phép khách hàng tồn tại mà không cần tài khoản online (user_id = NULL).
"""

from datetime import datetime, date
from typing import Optional

from sqlmodel import Field, SQLModel

from src.core.utils import get_utc_now


class Customer(SQLModel, table=True):
    """Bảng khách hàng - Hồ sơ CRM.

    Phân tách từ User (xác thực) để cho phép khách hàng vãng lai
    hoặc khách hàng chưa đăng ký tài khoản.

    Attributes:
            id: Primary key
            user_id: Foreign key tới User, nullable cho khách hàng vãng lai
            full_name: Họ tên khách hàng
            phone_number: Số điện thoại (dùng làm định danh chính)
            date_of_birth: Ngày sinh
            gender: Giới tính (nam/nữ/khác)
            address: Địa chỉ
            notes: Ghi chú CSKH (service history, preferences)
            skin_type: Loại da (khô/dầu/hỗn hợp/nhạy cảm)
            health_conditions: Tình trạng sức khỏe/dị ứng
            is_active: True nếu khách hàng hoạt động
            created_at: Timestamp tạo hồ sơ (UTC)
            updated_at: Timestamp cập nhật cuối cùng (UTC)
            deleted_at: Timestamp xóa mềm (NULL nếu chưa xóa)
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, index=True, foreign_key="user.id")
    full_name: Optional[str] = Field(default=None, max_length=255)
    phone_number: Optional[str] = Field(
        default=None, index=True, unique=True, max_length=20
    )
    date_of_birth: Optional[date] = Field(default=None)
    gender: Optional[str] = Field(default=None, max_length=10)
    address: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    skin_type: Optional[str] = Field(default=None, max_length=50)
    health_conditions: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=get_utc_now, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, index=True)
