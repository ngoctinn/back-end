"""API router cho module quản lý ảnh.

Định nghĩa các endpoint để tải lên, xóa và truy vấn ảnh.
"""

from fastapi import APIRouter, Depends, File, UploadFile
from sqlmodel import Session

from src.core.db import get_session
from src.core.dependencies import get_current_user
from src.modules.auth.models import User
from src.modules.media.schemas import (
    DeleteMessageResponse,
    MediaListResponse,
    MediaResponse,
)
from src.modules.media.service import (
    delete_media_file,
    get_media_for_entity,
    upload_avatar_for_customer,
    upload_image_for_service,
)

router = APIRouter(prefix="/media", tags=["media"])


@router.post(
    "/upload/customer-avatar/{customer_id}",
    response_model=MediaResponse,
    status_code=200,
    summary="Tải ảnh đại diện cho khách hàng",
)
async def upload_customer_avatar(
    customer_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> MediaResponse:
    """Tải ảnh đại diện cho khách hàng.

    **Yêu cầu:** JWT token (xác thực)

    Args:
        customer_id: ID của khách hàng
        file: File ảnh (multipart/form-data)
        current_user: Người dùng hiện tại
        session: Database session

    Returns:
        MediaResponse: Thông tin ảnh vừa tải lên

    Raises:
        404: Khách hàng không tìm thấy
        400: File không hợp lệ
        500: Lỗi server
    """
    return await upload_avatar_for_customer(customer_id, file, session)


@router.post(
    "/upload/service-image/{service_id}",
    response_model=MediaResponse,
    status_code=200,
    summary="Tải ảnh cho dịch vụ",
)
async def upload_service_image(
    service_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> MediaResponse:
    """Tải ảnh cho dịch vụ.

    **Yêu cầu:** JWT token (xác thực)

    Args:
        service_id: ID của dịch vụ
        file: File ảnh (multipart/form-data)
        current_user: Người dùng hiện tại
        session: Database session

    Returns:
        MediaResponse: Thông tin ảnh vừa tải lên

    Raises:
        400: File không hợp lệ
        500: Lỗi server
    """
    return await upload_image_for_service(service_id, file, session)


@router.delete(
    "/{media_id}",
    response_model=DeleteMessageResponse,
    status_code=200,
    summary="Xóa ảnh",
)
async def delete_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> DeleteMessageResponse:
    """Xóa ảnh khỏi Supabase Storage và CSDL.

    **Yêu cầu:** JWT token (xác thực)

    Args:
        media_id: ID của ảnh cần xóa
        current_user: Người dùng hiện tại
        session: Database session

    Returns:
        DeleteMessageResponse: Thông báo xóa thành công

    Raises:
        404: Ảnh không tìm thấy
        500: Lỗi server
    """
    result = await delete_media_file(media_id, session)
    return DeleteMessageResponse(message=result["message"])


@router.get(
    "/entity/{entity_type}/{entity_id}",
    response_model=MediaListResponse,
    status_code=200,
    summary="Lấy danh sách ảnh của đối tượng",
)
async def get_entity_media(
    entity_type: str,
    entity_id: int,
    session: Session = Depends(get_session),
) -> MediaListResponse:
    """Lấy danh sách ảnh của một đối tượng (khách hàng, dịch vụ, nhân viên).

    Args:
        entity_type: Loại đối tượng (customer|service|staff)
        entity_id: ID của đối tượng
        session: Database session

    Returns:
        MediaListResponse: Danh sách ảnh sắp xếp theo thời gian tạo (mới nhất trước)

    Raises:
        400: entity_type không hợp lệ
        404: Không tìm thấy ảnh
    """
    return await get_media_for_entity(entity_type, entity_id, session)
