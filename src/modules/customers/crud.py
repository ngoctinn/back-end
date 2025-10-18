"""CRUD operations cho module khách hàng.

Chỉ chứa các thao tác trực tiếp với database.
Không chứa logic nghiệp vụ phức tạp.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlmodel import Session, select

from src.core.utils import get_utc_now
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
    """Tạo mới khách hàng."""
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
    """Lấy khách hàng theo ID."""
    statement = select(Customer).where(Customer.id == customer_id)
    if not include_deleted:
        statement = statement.where(Customer.deleted_at.is_(None))
    return db.exec(statement).first()


def get_customer_by_user_id(
    db: Session,
    user_id: int,
    include_deleted: bool = False,
) -> Optional[Customer]:
    """Lấy khách hàng theo user_id."""
    statement = select(Customer).where(Customer.user_id == user_id)
    if not include_deleted:
        statement = statement.where(Customer.deleted_at.is_(None))
    return db.exec(statement).first()


def get_customer_by_phone_number(
    db: Session,
    phone_number: str,
    include_deleted: bool = False,
) -> Optional[Customer]:
    """Lấy khách hàng theo số điện thoại."""
    statement = select(Customer).where(Customer.phone_number == phone_number)
    if not include_deleted:
        statement = statement.where(Customer.deleted_at.is_(None))
    return db.exec(statement).first()


def get_customer_by_phone_and_no_user(
    db: Session,
    phone_number: str,
) -> Optional[Customer]:
    """Lấy khách hàng theo SĐT với điều kiện chưa có tài khoản."""
    statement = select(Customer).where(
        Customer.phone_number == phone_number,
        Customer.user_id.is_(None),
        Customer.deleted_at.is_(None),
    )
    return db.exec(statement).first()


def update_customer(
    db: Session,
    customer_id: int,
    update_data: dict,
) -> Optional[Customer]:
    """Cập nhật thông tin khách hàng."""
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
    """Xóa mềm khách hàng (đặt deleted_at)."""
    customer = get_customer_by_id(db, customer_id, include_deleted=False)
    if not customer:
        return False

    customer.deleted_at = get_utc_now()
    customer.updated_at = get_utc_now()
    db.commit()
    return True


def restore_customer(db: Session, customer_id: int) -> bool:
    """Khôi phục khách hàng (xóa deleted_at)."""
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
    """Tìm kiếm khách hàng theo tên hoặc SĐT (không bao gồm khách hàng bị xóa)."""
    # Câu lệnh để lấy dữ liệu
    statement = select(Customer).where(Customer.deleted_at.is_(None))
    # Câu lệnh để đếm
    count_statement = (
        select(func.count()).select_from(Customer).where(Customer.deleted_at.is_(None))
    )

    if search_query:
        search_term = f"%{search_query}%"
        search_filter = (Customer.full_name.ilike(search_term)) | (
            Customer.phone_number.ilike(search_term)
        )
        statement = statement.where(search_filter)
        count_statement = count_statement.where(search_filter)

    total = db.exec(count_statement).one()

    offset = (page - 1) * per_page
    customers = db.exec(statement.offset(offset).limit(per_page)).all()

    return customers, total


def link_customer_with_user(
    db: Session,
    customer_id: int,
    user_id: int,
) -> Optional[Customer]:
    """Liên kết khách hàng với tài khoản user."""
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
    """Hủy liên kết khách hàng với tài khoản user."""
    customer = get_customer_by_id(db, customer_id, include_deleted=False)
    if not customer:
        return None

    customer.user_id = None
    customer.updated_at = get_utc_now()
    db.commit()
    db.refresh(customer)
    return customer
