"""Định nghĩa schema (Pydantic) cho module quản lý ảnh."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MediaResponse(BaseModel):
    """Phản hồi thông tin ảnh sau khi tải lên hoặc truy vấn.

    Attributes:
        id: ID ảnh
        file_path: Đường dẫn file trong Supabase Storage
        public_url: URL công khai để truy cập ảnh
        file_type: MIME type của file
        file_size: Kích thước file (byte)
        related_entity_type: Loại đối tượng liên quan
        related_entity_id: ID của đối tượng liên quan
        created_at: Thời điểm tạo
    """

    id: int
    file_path: str
    public_url: str
    file_type: str
    file_size: int
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    created_at: datetime


class MediaListResponse(BaseModel):
    """Phản hồi danh sách ảnh.

    Attributes:
        media_list: Danh sách các ảnh
    """

    media_list: list[MediaResponse]


class DeleteMessageResponse(BaseModel):
    """Phản hồi sau khi xóa ảnh.

    Attributes:
        message: Thông báo xóa thành công
    """

    message: str
