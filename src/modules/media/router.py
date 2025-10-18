"""API router cho module quản lý ảnh.

Định nghĩa các endpoint để tải lên, xóa và truy vấn ảnh.
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlmodel import Session

from src.core.db import get_session
from src.core.dependencies import get_current_user
from src.modules.auth.models import User
from src.modules.customers import crud as customer_crud # Thêm import
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
    "/customers/me/avatar",
    response_model=MediaResponse,
    status_code=200,
    summary="Tự tải lên ảnh đại diện của tôi",
)
async def upload_my_customer_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> MediaResponse:
    """Người dùng đã đăng nhập tự tải lên ảnh đại diện của chính mình."""
    # Tìm hồ sơ khách hàng từ user đang đăng nhập
    customer = customer_crud.get_customer_by_user_id(db=session, user_id=current_user.id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hồ sơ khách hàng của bạn không tồn tại."
        )
    
    # Tái sử dụng service đã có để tải ảnh lên
    return await upload_avatar_for_customer(customer.id, file, session)


@router.post(
    "/customers/{customer_id}/avatar",
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
    """
    return await upload_avatar_for_customer(customer_id, file, session)


@router.post(
    "/services/{service_id}/images",
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
    """
    return await upload_image_for_service(service_id, file, session)


@router.get(
    "/customers/{customer_id}",
    response_model=MediaListResponse,
    status_code=200,
    summary="Lấy danh sách ảnh của khách hàng",
)
async def get_customer_media(
    customer_id: int,
    session: Session = Depends(get_session),
) -> MediaListResponse:
    """Lấy tất cả media của một khách hàng cụ thể."""
    return await get_media_for_entity("customer", customer_id, session)


@router.get(
    "/services/{service_id}",
    response_model=MediaListResponse,
    status_code=200,
    summary="Lấy danh sách ảnh của dịch vụ",
)
async def get_service_media(
    service_id: int,
    session: Session = Depends(get_session),
) -> MediaListResponse:
    """Lấy tất cả media của một dịch vụ cụ thể."""
    return await get_media_for_entity("service", service_id, session)


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
    """
    result = await delete_media_file(media_id, session)
    return DeleteMessageResponse(message=result["message"])