"""Các model CSDL cho module quản lý ảnh.

Định nghĩa bảng MediaFile để lưu trữ metadata ảnh được tải lên Supabase.
Cho phép liên kết ảnh với các đối tượng khác trong hệ thống.
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from src.core.utils import get_utc_now


class MediaFile(SQLModel, table=True):
    """Bảng quản lý metadata ảnh trên Supabase Storage.

    Lưu trữ thông tin về các file ảnh được tải lên, bao gồm đường dẫn,
    URL công khai, kích thước và thông tin về đối tượng liên quan.

    Attributes:
        id: Primary key
        file_path: Đường dẫn file trong Supabase Storage (unique)
        public_url: URL công khai để truy cập ảnh
        file_type: MIME type của file (ví dụ: image/jpeg)
        file_size: Kích thước file tính bằng byte
        owner_id: ID của người tải lên (nullable)
        related_entity_id: ID của đối tượng liên quan
        related_entity_type: Loại đối tượng (customer|service|staff)
        created_at: Thời điểm tạo record (UTC)
        updated_at: Thời điểm cập nhật cuối cùng (UTC)
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    file_path: str = Field(unique=True, index=True, max_length=500)
    public_url: str = Field(max_length=1000)
    file_type: str = Field(max_length=100)
    file_size: int = Field(default=0)
    owner_id: Optional[int] = Field(default=None)
    related_entity_id: Optional[int] = Field(default=None, index=True)
    related_entity_type: Optional[str] = Field(default=None, index=True, max_length=50)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)
