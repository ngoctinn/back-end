"""Thao tác trực tiếp với cơ sở dữ liệu cho module quản lý ảnh.

Chứa các hàm CRUD (Create, Read, Update, Delete) cho bảng MediaFile.
"""

from typing import Optional

from sqlmodel import Session, select

from src.modules.media.models import MediaFile


def create_media_record(
    file_path: str,
    public_url: str,
    file_type: str,
    file_size: int,
    owner_id: Optional[int] = None,
    related_entity_id: Optional[int] = None,
    related_entity_type: Optional[str] = None,
    session: Optional[Session] = None,
) -> MediaFile:
    """Tạo record ảnh mới trong CSDL.

    Args:
        file_path: Đường dẫn file trong Supabase
        public_url: URL công khai của file
        file_type: MIME type của file
        file_size: Kích thước file (byte)
        owner_id: ID người tải lên (tùy chọn)
        related_entity_id: ID đối tượng liên quan
        related_entity_type: Loại đối tượng (customer|service|staff)
        session: Database session

    Returns:
        MediaFile: Record ảnh vừa tạo
    """
    media = MediaFile(
        file_path=file_path,
        public_url=public_url,
        file_type=file_type,
        file_size=file_size,
        owner_id=owner_id,
        related_entity_id=related_entity_id,
        related_entity_type=related_entity_type,
    )

    session.add(media)
    session.flush()
    session.refresh(media)

    return media


def get_media_by_id(media_id: int, session: Session) -> Optional[MediaFile]:
    """Lấy thông tin ảnh theo ID.

    Args:
        media_id: ID của ảnh
        session: Database session

    Returns:
        MediaFile: Thông tin ảnh hoặc None nếu không tìm thấy
    """
    statement = select(MediaFile).where(MediaFile.id == media_id)
    return session.exec(statement).first()


def get_media_list_by_entity(
    entity_type: str, entity_id: int, session: Session
) -> list[MediaFile]:
    """Lấy danh sách ảnh của một đối tượng.

    Args:
        entity_type: Loại đối tượng (customer|service|staff)
        entity_id: ID của đối tượng
        session: Database session

    Returns:
        list[MediaFile]: Danh sách ảnh sắp xếp theo thời gian tạo (mới nhất trước)
    """
    statement = (
        select(MediaFile)
        .where(
            (MediaFile.related_entity_type == entity_type)
            & (MediaFile.related_entity_id == entity_id)
        )
        .order_by(MediaFile.created_at.desc())
    )
    return session.exec(statement).all()


def delete_media_record(media_id: int, session: Session) -> bool:
    """Xóa record ảnh khỏi CSDL.

    Args:
        media_id: ID của ảnh
        session: Database session

    Returns:
        bool: True nếu xóa thành công
    """
    media = session.get(MediaFile, media_id)

    if media:
        session.delete(media)
        session.flush()  # Đảm bảo thay đổi được đưa vào DB trước khi service commit
        return True

    return False
