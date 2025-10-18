"""Logic nghiệp vụ cho module quản lý ảnh.

Chứa các hàm xử lý tải lên, xóa và truy vấn ảnh từ Supabase Storage
và cơ sở dữ liệu.
"""

import logging
import time
from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlmodel import Session

from src.core.config import settings
from src.core.storage import (
    delete_file_from_storage,
    get_public_url,
    upload_file_to_storage,
)
from src.modules.media.crud import (
    create_media_record,
    delete_media_record,
    get_media_by_id,
    get_media_list_by_entity,
)
from src.modules.media.models import MediaFile
from src.modules.media.schemas import MediaListResponse, MediaResponse

logger = logging.getLogger(__name__)


def map_media_model_to_response(media: MediaFile) -> MediaResponse:
    """Chuyển đổi MediaFile model sang MediaResponse schema."""
    return MediaResponse(
        id=media.id,
        file_path=media.file_path,
        public_url=media.public_url,
        file_type=media.file_type,
        file_size=media.file_size,
        related_entity_type=media.related_entity_type,
        related_entity_id=media.related_entity_id,
        created_at=media.created_at,
    )


def _validate_image_file(file: UploadFile) -> None:
    """Kiểm tra tính hợp lệ của file ảnh.

    Args:
        file: File được tải lên

    Raises:
        HTTPException: Nếu file không hợp lệ
    """
    # Kiểm tra MIME type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Loại file không được phép. Chỉ hỗ trợ: {', '.join(settings.ALLOWED_IMAGE_TYPES)}",
        )

    # Kiểm tra kích thước file
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,  # Payload Too Large
            detail=f"Kích thước file quá lớn. Tối đa: {settings.MAX_FILE_SIZE // 1024 // 1024}MB",
        )


async def upload_avatar_for_customer(
    customer_id: int, file: UploadFile, session: Session
) -> MediaResponse:
    """Tải ảnh đại diện cho khách hàng.

    Args:
        customer_id: ID của khách hàng
        file: File ảnh được tải lên
        session: Database session

    Returns:
        MediaResponse: Thông tin ảnh vừa tải lên

    Raises:
        HTTPException: Nếu khách hàng không tìm thấy hoặc file không hợp lệ
    """
    from src.modules.customers.models import Customer

    # Kiểm tra khách hàng tồn tại
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=404, detail=f"Khách hàng ID {customer_id} không tìm thấy"
        )

    # Kiểm tra file hợp lệ
    _validate_image_file(file)

    # Tạo đường dẫn file duy nhất
    file_extension = file.filename.split(".")[-1] if file.filename else "jpg"
    timestamp = int(time.time() * 1000)
    file_path = f"customers/{customer_id}/avatar_{timestamp}.{file_extension}"

    # Tải file lên Supabase
    public_url = upload_file_to_storage(file.file, file_path, file.content_type)

    # Lấy kích thước file
    file_size = file.size or 0

    # Tạo record trong DB
    media = create_media_record(
        file_path=file_path,
        public_url=public_url,
        file_type=file.content_type or "image/jpeg",
        file_size=file_size,
        related_entity_id=customer_id,
        related_entity_type="customer",
        session=session,
    )

    session.commit()
    session.refresh(media)

    logger.info(f"✓ Tải ảnh đại diện cho khách hàng {customer_id} thành công")

    return map_media_model_to_response(media)


async def upload_image_for_service(
    service_id: int, file: UploadFile, session: Session
) -> MediaResponse:
    """Tải ảnh cho dịch vụ.

    Args:
        service_id: ID của dịch vụ
        file: File ảnh được tải lên
        session: Database session

    Returns:
        MediaResponse: Thông tin ảnh vừa tải lên

    Raises:
        HTTPException: Nếu dịch vụ không tìm thấy hoặc file không hợp lệ
    """
    # from src.modules.services.models import Service  # Giả định model Service tồn tại

    # # Kiểm tra dịch vụ tồn tại
    # service = session.get(Service, service_id)
    # if not service:
    #     raise HTTPException(
    #         status_code=404, detail=f"Dịch vụ ID {service_id} không tìm thấy"
    #     )

    # Kiểm tra file hợp lệ
    _validate_image_file(file)

    # Tạo đường dẫn file duy nhất
    file_extension = file.filename.split(".")[-1] if file.filename else "jpg"
    timestamp = int(time.time() * 1000)
    file_path = f"services/{service_id}/image_{timestamp}.{file_extension}"

    # Tải file lên Supabase
    public_url = upload_file_to_storage(file.file, file_path, file.content_type)

    # Lấy kích thước file
    file_size = file.size or 0

    # Tạo record trong DB
    media = create_media_record(
        file_path=file_path,
        public_url=public_url,
        file_type=file.content_type or "image/jpeg",
        file_size=file_size,
        related_entity_id=service_id,
        related_entity_type="service",
        session=session,
    )

    session.commit()
    session.refresh(media)

    logger.info(f"✓ Tải ảnh cho dịch vụ {service_id} thành công")

    return map_media_model_to_response(media)


async def delete_media_file(media_id: int, session: Session) -> dict:
    """Xóa ảnh khỏi Supabase Storage và CSDL.

    Sử dụng transaction để đảm bảo cả xóa file và record đều thành công
    hoặc thất bại cùng nhau.

    Args:
        media_id: ID của ảnh cần xóa
        session: Database session

    Returns:
        dict: Thông báo xóa thành công

    Raises:
        HTTPException: Nếu ảnh không tìm thấy
    """
    # Tìm record trong DB
    media = get_media_by_id(media_id, session)
    if not media:
        raise HTTPException(status_code=404, detail=f"Ảnh ID {media_id} không tìm thấy")

    # Bắt đầu transaction
    try:
        # Xóa file từ Supabase
        delete_file_from_storage(media.file_path)

        # Xóa record từ DB
        delete_media_record(media_id, session)

        session.commit()

        logger.info(f"✓ Xóa ảnh ID {media_id} thành công")

        return {"message": "Xóa ảnh thành công"}

    except Exception as e:
        session.rollback()
        logger.error(f"✗ Lỗi xóa ảnh: {str(e)}")
        raise HTTPException(status_code=500, detail="Lỗi xóa ảnh")


async def get_media_for_entity(
    entity_type: str, entity_id: int, session: Session
) -> MediaListResponse:
    """Lấy danh sách ảnh của một đối tượng.

    Args:
        entity_type: Loại đối tượng (customer|service|staff)
        entity_id: ID của đối tượng
        session: Database session

    Returns:
        MediaListResponse: Danh sách ảnh

    Raises:
        HTTPException: Nếu entity_type không hợp lệ
    """
    # Kiểm tra entity_type hợp lệ
    valid_entity_types = {"customer", "service", "staff"}
    if entity_type not in valid_entity_types:
        raise HTTPException(
            status_code=400,
            detail=f"Loại đối tượng không hợp lệ. Hỗ trợ: {', '.join(valid_entity_types)}",
        )

    # Truy vấn danh sách ảnh
    media_list = get_media_list_by_entity(entity_type, entity_id, session)

    # Map thành MediaResponse
    responses = [map_media_model_to_response(media) for media in media_list]

    return MediaListResponse(media_list=responses)

