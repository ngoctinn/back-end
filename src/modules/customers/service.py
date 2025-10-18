"""Business logic cho module khách hàng.

Chứa logic nghiệp vụ phức tạp, gọi CRUD functions.
"""

import logging
from datetime import datetime
from typing import Optional

from sqlmodel import Session

from src.core.utils import get_utc_now

from src.modules.customers.models import Customer
from src.modules.customers import crud
from src.core.otp import verify_otp, clear_otp, generate_otp, send_otp_sms, store_otp
from src.core.utils import normalize_phone_number

logger = logging.getLogger(__name__)


class CustomerNotFoundError(Exception):
    """Khách hàng không tìm thấy."""

    pass


class PhoneNumberAlreadyExistsError(Exception):
    """Số điện thoại đã tồn tại."""

    pass


class InvalidOTPError(Exception):
    """OTP không hợp lệ hoặc hết hạn."""

    pass


class AccountLinkingError(Exception):
    """Lỗi khi liên kết tài khoản."""

    pass


def create_walk_in_customer(
    db: Session,
    full_name: str,
    phone_number: str,
    **kwargs,
) -> Customer:
    """Tạo khách hàng vãng lai (không có tài khoản).

    Args:
            db: Database session
            full_name: Họ tên khách hàng
            phone_number: Số điện thoại
            **kwargs: Các fields khác (address, notes, ...)

    Returns:
            Customer object được tạo

    Raises:
            PhoneNumberAlreadyExistsError: Nếu SĐT đã tồn tại
    """
    # Normalize SĐT
    normalized_phone = normalize_phone_number(phone_number)
    logger.debug(f"Tạo khách hàng vãng lai: {full_name} (SĐT: {normalized_phone})")

    # Kiểm tra SĐT đã tồn tại chưa
    existing = crud.get_customer_by_phone_number(
        db, normalized_phone, include_deleted=False
    )
    if existing:
        logger.warning(f"SĐT {normalized_phone} đã tồn tại khi tạo khách hàng vãng lai")
        raise PhoneNumberAlreadyExistsError(
            f"Số điện thoại {normalized_phone} đã tồn tại"
        )

    # Tạo khách hàng với user_id = NULL
    customer = crud.create_customer(
        db,
        full_name=full_name,
        phone_number=normalized_phone,
        user_id=None,
        **kwargs,
    )
    logger.info(f"✓ Tạo khách hàng vãng lai thành công: ID={customer.id}, {full_name}")
    return customer


def create_online_customer_with_user(
    db: Session,
    user_id: int,
    full_name: Optional[str] = None,
    phone_number: Optional[str] = None,
    **kwargs,
) -> Customer:
    """Tạo hồ sơ khách hàng stub khi user đăng ký online.

    Hồ sơ này có full_name=NULL và phone_number=NULL (chưa hoàn thành).

    Args:
            db: Database session
            user_id: ID tài khoản vừa tạo
            full_name: Họ tên (có thể None khi lazy registration)
            phone_number: Số điện thoại (có thể None khi lazy registration)
            **kwargs: Các fields khác

    Returns:
            Customer object được tạo
    """
    # Nếu có phone_number, normalize nó
    normalized_phone = None
    if phone_number:
        normalized_phone = normalize_phone_number(phone_number)
        # Kiểm tra không trùng lặp
        existing = crud.get_customer_by_phone_number(
            db, normalized_phone, include_deleted=False
        )
        if existing:
            raise PhoneNumberAlreadyExistsError(
                f"Số điện thoại {normalized_phone} đã tồn tại"
            )

    customer = crud.create_customer(
        db,
        full_name=full_name,
        phone_number=normalized_phone,
        user_id=user_id,
        **kwargs,
    )
    return customer


def complete_customer_profile(
    db: Session,
    customer_id: int,
    full_name: str,
    phone_number: str,
    **update_data,
) -> Customer:
    """Hoàn thành hồ sơ khách hàng (Luồng 2b).

    Cập nhật full_name và phone_number cho hồ sơ stub.

    Args:
            db: Database session
            customer_id: ID khách hàng
            full_name: Họ tên
            phone_number: Số điện thoại
            **update_data: Các fields khác

    Returns:
            Customer object được cập nhật

    Raises:
            CustomerNotFoundError: Khách hàng không tìm thấy
            PhoneNumberAlreadyExistsError: SĐT đã tồn tại
    """
    customer = crud.get_customer_by_id(db, customer_id, include_deleted=False)
    if not customer:
        raise CustomerNotFoundError(f"Khách hàng {customer_id} không tìm thấy")

    # Normalize SĐT
    normalized_phone = normalize_phone_number(phone_number)

    # Kiểm tra SĐT không trùng (trừ chính nó)
    existing = crud.get_customer_by_phone_number(
        db, normalized_phone, include_deleted=False
    )
    if existing and existing.id != customer_id:
        raise PhoneNumberAlreadyExistsError(
            f"Số điện thoại {normalized_phone} đã tồn tại"
        )

    # Cập nhật
    update_data["full_name"] = full_name
    update_data["phone_number"] = normalized_phone
    updated = crud.update_customer(db, customer_id, update_data)

    if not updated:
        raise CustomerNotFoundError(f"Khách hàng {customer_id} không tìm thấy")

    return updated


def initiate_account_linking(
    db: Session,
    phone_number: str,
) -> str:
    """Bắt đầu liên kết tài khoản - tìm hồ sơ cũ và gửi OTP (Luồng 3c).

    Args:
            db: Database session
            phone_number: Số điện thoại cần liên kết

    Returns:
            Message thông báo OTP đã gửi

    Raises:
            CustomerNotFoundError: Hồ sơ khách hàng cũ không tìm thấy
            Exception: Lỗi gửi SMS
    """
    # Normalize SĐT
    normalized_phone = normalize_phone_number(phone_number)

    # Tìm hồ sơ cũ (chưa có user_id)
    old_customer = crud.get_customer_by_phone_and_no_user(db, normalized_phone)
    if not old_customer:
        raise CustomerNotFoundError(
            f"Không tìm thấy hồ sơ khách hàng với SĐT {normalized_phone}"
        )

    # Generate + Send OTP
    otp_code = generate_otp()
    send_otp_sms(normalized_phone, otp_code)
    store_otp(normalized_phone, otp_code, expiry_seconds=5 * 60)  # 5 phút

    return f"OTP đã được gửi đến {normalized_phone}"


def verify_otp_and_link_account(
    db: Session,
    user_id: int,
    phone_number: str,
    otp_code: str,
) -> Customer:
    """Xác minh OTP và hoàn tất liên kết tài khoản (Luồng 3d).

    Transaction: Hợp nhất hồ sơ stub và hồ sơ cũ.

    Args:
            db: Database session
            user_id: ID tài khoản hiện tại
            phone_number: Số điện thoại
            otp_code: Mã OTP nhập từ user

    Returns:
            Customer object sau khi hợp nhất

    Raises:
            InvalidOTPError: OTP không hợp lệ hoặc hết hạn
            CustomerNotFoundError: Hồ sơ cũ hoặc stub không tìm thấy
            AccountLinkingError: Lỗi trong quá trình liên kết
    """
    # Normalize SĐT
    normalized_phone = normalize_phone_number(phone_number)

    # Verify OTP
    if not verify_otp(normalized_phone, otp_code):
        logger.warning(f"OTP xác minh thất bại cho SĐT: {normalized_phone}")
        raise InvalidOTPError("OTP không hợp lệ hoặc hết hạn")

    try:
        # Lấy stub customer (hồ sơ "chờ" có user_id)
        stub_customer = crud.get_customer_by_user_id(db, user_id, include_deleted=False)
        if not stub_customer:
            raise AccountLinkingError("Không tìm thấy hồ sơ user hiện tại")

        # Lấy old customer (hồ sơ cũ không có user_id)
        old_customer = crud.get_customer_by_phone_and_no_user(db, normalized_phone)
        if not old_customer:
            raise AccountLinkingError(
                f"Không tìm thấy hồ sơ khách hàng cũ với SĐT {normalized_phone}"
            )

        # Transaction: Update old_customer với user_id, xóa mềm stub_customer
        old_customer.user_id = user_id
        old_customer.updated_at = get_utc_now()

        stub_customer.deleted_at = get_utc_now()
        stub_customer.updated_at = get_utc_now()

        db.commit()

        # Clear OTP
        clear_otp(normalized_phone)
        logger.info(
            f"✓ Liên kết tài khoản thành công: user_id={user_id}, customer_id={old_customer.id}"
        )

        return old_customer

    except Exception as e:
        db.rollback()
        if isinstance(e, (InvalidOTPError, AccountLinkingError, CustomerNotFoundError)):
            raise
        raise AccountLinkingError(f"Lỗi liên kết tài khoản: {str(e)}")


def delete_customer(db: Session, customer_id: int) -> bool:
    """Xóa mềm khách hàng (Luồng 4).

    Args:
            db: Database session
            customer_id: ID khách hàng

    Returns:
            True nếu xóa thành công

    Raises:
            CustomerNotFoundError: Khách hàng không tìm thấy
    """
    success = crud.soft_delete_customer(db, customer_id)
    if not success:
        logger.warning(
            f"Xóa khách hàng thất bại: ID={customer_id} (không tìm thấy hoặc đã xóa)"
        )
        raise CustomerNotFoundError(
            f"Khách hàng {customer_id} không tìm thấy hoặc đã bị xóa"
        )
    logger.info(f"✓ Xóa mềm khách hàng thành công: ID={customer_id}")
    return success


def restore_customer(db: Session, customer_id: int) -> Customer:
    """Khôi phục khách hàng (Luồng 5).

    Args:
            db: Database session
            customer_id: ID khách hàng

    Returns:
            Customer object sau khi khôi phục

    Raises:
            CustomerNotFoundError: Khách hàng không tìm thấy hoặc chưa bị xóa
    """
    success = crud.restore_customer(db, customer_id)
    if not success:
        logger.warning(
            f"Khôi phục khách hàng thất bại: ID={customer_id} (không tìm thấy hoặc chưa xóa)"
        )
        raise CustomerNotFoundError(
            f"Khách hàng {customer_id} không tìm thấy hoặc chưa bị xóa"
        )
    customer = crud.get_customer_by_id(db, customer_id, include_deleted=False)
    logger.info(f"✓ Khôi phục khách hàng thành công: ID={customer_id}")
    return customer


def search_customers(
    db: Session,
    search_query: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Customer], int, int]:
    """Tìm kiếm khách hàng (không bao gồm khách hàng bị xóa).

    Args:
            db: Database session
            search_query: Chuỗi tìm kiếm
            page: Trang (1-based)
            per_page: Số item trên mỗi trang

    Returns:
            Tuple (danh sách Customer, tổng số, số trang)
    """
    customers, total = crud.find_customer_by_query(
        db, search_query=search_query, page=page, per_page=per_page
    )
    total_pages = (total + per_page - 1) // per_page
    return customers, total, total_pages
