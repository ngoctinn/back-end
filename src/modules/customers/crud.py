"""CRUD operations cho module khách hàng.

Chỉ chứa các thao tác trực tiếp với database.
Không chứa logic nghiệp vụ phức tạp.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import func

from src.core.utils import get_utc_now
from sqlalchemy.orm import Session

from src.modules.customers.models import Customer


def create_customer(
    db: Session,
    full_name: Optional[str] = None,
    phone_number: Optional[str] = None,
    user_id: Optional[int] = None,
    date_of_birth: Optional[datetime] = None,
    gender: Optional[str] = None,
    address: Optional[str] = None,
    notes: Optional[str] = None,
    skin_type: Optional[str] = None,
    health_conditions: Optional[str] = None,
    is_active: bool = True,
) -> Customer:
    """Tạo mới khách hàng.

    Args:
            db: Database session
            full_name: Họ tên khách hàng
            phone_number: Số điện thoại
            user_id: ID tài khoản (có thể NULL cho khách hàng vãng lai)
            date_of_birth: Ngày sinh
            gender: Giới tính
            address: Địa chỉ
            notes: Ghi chú
            skin_type: Loại da
            health_conditions: Tình trạng sức khỏe
            is_active: Trạng thái hoạt động

    Returns:
            Customer object được tạo
    """
    customer = Customer(
        user_id=user_id,
        full_name=full_name,
        phone_number=phone_number,
        date_of_birth=date_of_birth,
        gender=gender,
        address=address,
        notes=notes,
        skin_type=skin_type,
        health_conditions=health_conditions,
        is_active=is_active,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def get_customer_by_id(
    db: Session,
    customer_id: int,
    include_deleted: bool = False,
) -> Optional[Customer]:
    """Lấy khách hàng theo ID.

    Args:
            db: Database session
            customer_id: ID khách hàng
            include_deleted: True để bao gồm khách hàng bị xóa mềm

    Returns:
            Customer object hoặc None nếu không tìm thấy
    """
    query = db.query(Customer).filter(Customer.id == customer_id)
    if not include_deleted:
        query = query.filter(Customer.deleted_at.is_(None))
    return query.first()


def get_customer_by_user_id(
    db: Session,
    user_id: int,
    include_deleted: bool = False,
) -> Optional[Customer]:
    """Lấy khách hàng theo user_id.

    Args:
            db: Database session
            user_id: ID tài khoản
            include_deleted: True để bao gồm khách hàng bị xóa mềm

    Returns:
            Customer object hoặc None nếu không tìm thấy
    """
    query = db.query(Customer).filter(Customer.user_id == user_id)
    if not include_deleted:
        query = query.filter(Customer.deleted_at.is_(None))
    return query.first()


def get_customer_by_phone_number(
    db: Session,
    phone_number: str,
    include_deleted: bool = False,
) -> Optional[Customer]:
    """Lấy khách hàng theo số điện thoại.

    Args:
            db: Database session
            phone_number: Số điện thoại (sau normalize)
            include_deleted: True để bao gồm khách hàng bị xóa mềm

    Returns:
            Customer object hoặc None nếu không tìm thấy
    """
    query = db.query(Customer).filter(Customer.phone_number == phone_number)
    if not include_deleted:
        query = query.filter(Customer.deleted_at.is_(None))
    return query.first()


def get_customer_by_phone_and_no_user(
    db: Session,
    phone_number: str,
) -> Optional[Customer]:
    """Lấy khách hàng theo SĐT với điều kiện chưa có tài khoản.

    Dùng khi tìm hồ sơ khách hàng cũ để liên kết tài khoản.

    Args:
            db: Database session
            phone_number: Số điện thoại (sau normalize)

    Returns:
            Customer object hoặc None nếu không tìm thấy
    """
    return (
        db.query(Customer)
        .filter(
            Customer.phone_number == phone_number,
            Customer.user_id.is_(None),
            Customer.deleted_at.is_(None),
        )
        .first()
    )


def update_customer(
    db: Session,
    customer_id: int,
    update_data: dict,
) -> Optional[Customer]:
    """Cập nhật thông tin khách hàng.

    Args:
            db: Database session
            customer_id: ID khách hàng
            update_data: Dictionary chứa các fields cần cập nhật

    Returns:
            Customer object được cập nhật hoặc None nếu không tìm thấy
    """
    customer = get_customer_by_id(db, customer_id, include_deleted=False)
    if not customer:
        return None

    # Cập nhật updated_at
    update_data["updated_at"] = get_utc_now()

    for field, value in update_data.items():
        if value is not None:
            setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer


def soft_delete_customer(db: Session, customer_id: int) -> bool:
    """Xóa mềm khách hàng (đặt deleted_at).

    Args:
            db: Database session
            customer_id: ID khách hàng

    Returns:
            True nếu xóa thành công, False nếu khách hàng không tồn tại
    """
    customer = get_customer_by_id(db, customer_id, include_deleted=False)
    if not customer:
        return False

    customer.deleted_at = get_utc_now()
    customer.updated_at = get_utc_now()
    db.commit()
    return True


def restore_customer(db: Session, customer_id: int) -> bool:
    """Khôi phục khách hàng (xóa deleted_at).

    Args:
            db: Database session
            customer_id: ID khách hàng

    Returns:
            True nếu khôi phục thành công, False nếu khách hàng không bị xóa
    """
    customer = get_customer_by_id(db, customer_id, include_deleted=True)
    if not customer or customer.deleted_at is None:
        return False

    customer.deleted_at = None
    customer.updated_at = get_utc_now()
    db.commit()
    return True


def find_customer_by_query(
    db: Session,
    search_query: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Customer], int]:
    """Tìm kiếm khách hàng theo tên hoặc SĐT (không bao gồm khách hàng bị xóa).

    Args:
            db: Database session
            search_query: Chuỗi tìm kiếm (tên hoặc SĐT)
            page: Trang (1-based)
            per_page: Số item trên mỗi trang

    Returns:
            Tuple (danh sách Customer, tổng số)
    """
    query = db.query(Customer).filter(Customer.deleted_at.is_(None))

    if search_query:
        # Tìm kiếm theo tên hoặc SĐT
        search_term = f"%{search_query}%"
        query = query.filter(
            (Customer.full_name.ilike(search_term))
            | (Customer.phone_number.ilike(search_term))
        )

    total = query.count()

    # Pagination
    offset = (page - 1) * per_page
    customers = query.offset(offset).limit(per_page).all()

    return customers, total


def link_customer_with_user(
    db: Session,
    customer_id: int,
    user_id: int,
) -> Optional[Customer]:
    """Liên kết khách hàng với tài khoản user.

    Args:
            db: Database session
            customer_id: ID khách hàng
            user_id: ID tài khoản

    Returns:
            Customer object sau khi liên kết hoặc None nếu không tìm thấy
    """
    customer = get_customer_by_id(db, customer_id, include_deleted=False)
    if not customer:
        return None

    customer.user_id = user_id
    customer.updated_at = get_utc_now()
    db.commit()
    db.refresh(customer)
    return customer


def unlink_customer_from_user(
    db: Session,
    customer_id: int,
) -> Optional[Customer]:
    """Hủy liên kết khách hàng với tài khoản user.

    Args:
            db: Database session
            customer_id: ID khách hàng

    Returns:
            Customer object sau khi hủy liên kết hoặc None nếu không tìm thấy
    """
    customer = get_customer_by_id(db, customer_id, include_deleted=False)
    if not customer:
        return None

    customer.user_id = None
    customer.updated_at = get_utc_now()
    db.commit()
    db.refresh(customer)
    return customer
