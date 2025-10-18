"""Router cho module khách hàng.

Định nghĩa tất cả API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from src.core.db import get_session
from src.core.dependencies import get_current_user
from src.core.utils import normalize_phone_number
from src.modules.auth.models import User
from src.modules.customers import schemas, service, crud
from src.modules.customers.models import Customer

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/walk-in", response_model=schemas.CustomerResponse)
def create_walk_in_customer(
    request: schemas.CustomerCreateRequest,
    db: Session = Depends(get_session),
):
    """Tạo khách hàng vãng lai (Luồng 1).

    Không yêu cầu tài khoản, chỉ cần tên và SĐT.
    """
    try:
        customer = service.create_walk_in_customer(
            db, request.full_name, request.phone_number
        )
        return customer
    except service.PhoneNumberAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Số điện thoại đã tồn tại",
        )


@router.post("/profile", response_model=schemas.CustomerResponse)
def complete_profile(
    request: schemas.CustomerCompleteProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Hoàn thiện hồ sơ khi user đã có tài khoản (Luồng 2b).

    Cập nhật full_name và phone_number cho hồ sơ stub.
    Yêu cầu JWT token.
    """
    # Lấy customer liên kết với user
    customer = crud.get_customer_by_user_id(db, current_user.id, include_deleted=False)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hồ sơ khách hàng không tìm thấy",
        )

    try:
        updated_customer = service.complete_customer_profile(
            db, customer.id, request.full_name, request.phone_number
        )
        return updated_customer
    except service.CustomerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hồ sơ khách hàng không tìm thấy",
        )
    except service.PhoneNumberAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Số điện thoại đã tồn tại",
        )


@router.get("/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_session),
):
    """Lấy thông tin khách hàng theo ID.

    Không bao gồm khách hàng bị xóa mềm.
    """
    customer = crud.get_customer_by_id(db, customer_id, include_deleted=False)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khách hàng không tìm thấy",
        )
    return customer


@router.put("/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(
    customer_id: int,
    request: schemas.CustomerUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Cập nhật thông tin khách hàng.

    Yêu cầu JWT token (authentication).
    User chỉ có thể cập nhật hồ sơ của chính mình.
    """
    customer = crud.get_customer_by_id(db, customer_id, include_deleted=False)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khách hàng không tìm thấy",
        )

    # ✅ Kiểm tra ownership - user chỉ có thể cập nhật hồ sơ của chính mình
    if customer.user_id and customer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền cập nhật hồ sơ khách hàng này",
        )

    # Chuẩn hóa SĐT nếu có (nhưng schema đã normalize rồi)
    update_data = request.model_dump(exclude_unset=True)

    try:
        updated = crud.update_customer(db, customer_id, update_data)
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cập nhật: {str(e)}",
        )


@router.delete("/{customer_id}")
def delete_customer_endpoint(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Xóa mềm khách hàng (Luồng 4).

    Yêu cầu JWT token (authentication).
    """
    try:
        service.delete_customer(db, customer_id)
        return {
            "message": "Khách hàng đã bị xóa",
            "can_restore": True,
        }
    except service.CustomerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khách hàng không tìm thấy hoặc đã bị xóa",
        )


@router.post("/{customer_id}/restore", response_model=schemas.CustomerResponse)
def restore_customer_endpoint(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Khôi phục khách hàng (Luồng 5).

    Yêu cầu JWT token (authentication).
    """
    try:
        customer = service.restore_customer(db, customer_id)
        return customer
    except service.CustomerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khách hàng không tìm thấy hoặc chưa bị xóa",
        )


@router.get("", response_model=schemas.CustomerListResponse)
def search_customers(
    search_query: str | None = Query(None, min_length=1, max_length=255),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_session),
):
    """Tìm kiếm khách hàng (không bao gồm khách hàng bị xóa).

    Tìm kiếm theo tên hoặc SĐT.

    Args:
            search_query: Chuỗi tìm kiếm (max 255 ký tự)
            page: Số trang (bắt đầu từ 1)
            per_page: Số items trên mỗi trang (max 100)
    """
    customers, total, total_pages = service.search_customers(
        db, search_query=search_query, page=page, per_page=per_page
    )
    return schemas.CustomerListResponse(
        customers=customers,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.post("/link-account/initiate")
def initiate_account_linking(
    request: schemas.CustomerLinkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Bắt đầu liên kết tài khoản - gửi OTP (Luồng 3c).

    Yêu cầu JWT token.
    """
    try:
        message = service.initiate_account_linking(db, request.phone_number)
        return {"message": message}
    except service.CustomerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ khách hàng cũ với SĐT này",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi gửi OTP: {str(e)}",
        )


@router.post("/link-account/verify", response_model=schemas.CustomerResponse)
def verify_otp_and_link(
    request: schemas.CustomerVerifyOTPRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Xác minh OTP và hoàn tất liên kết tài khoản (Luồng 3d).

    Yêu cầu JWT token.
    """
    try:
        customer = service.verify_otp_and_link_account(
            db, current_user.id, request.phone_number, request.otp_code
        )
        return customer
    except service.InvalidOTPError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OTP không hợp lệ hoặc hết hạn",
        )
    except service.CustomerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hồ sơ khách hàng không tìm thấy",
        )
    except service.AccountLinkingError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/me/profile", response_model=schemas.CustomerResponse)
def get_my_customer_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Lấy hồ sơ khách hàng của user hiện tại (Luồng 3b).

    Yêu cầu JWT token.
    """
    customer = crud.get_customer_by_user_id(db, current_user.id, include_deleted=False)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hồ sơ khách hàng không tìm thấy",
        )
    return customer
