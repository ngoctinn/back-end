"""Kiểm thử module quản lý khách hàng.

Bao gồm:
- Unit tests cho CRUD operations
- Unit tests cho service functions
- Integration tests cho API endpoints
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from src.modules.customers.models import Customer
from src.modules.customers import crud, service
from src.core.db import SessionLocal
from src.core.utils import normalize_phone_number, validate_phone_number


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def db():
	"""Tạo database session cho mỗi test."""
	session = SessionLocal()
	try:
		yield session
	finally:
		# Xóa tất cả customers được tạo trong test
		session.query(Customer).delete()
		session.commit()
		session.close()


# ============================================================================
# TESTS - UTILS
# ============================================================================


def test_normalize_phone_number_with_0():
	"""Test chuẩn hóa SĐT bắt đầu với 0."""
	assert normalize_phone_number("0912345678") == "0912345678"


def test_normalize_phone_number_with_84():
	"""Test chuẩn hóa SĐT bắt đầu với 84."""
	assert normalize_phone_number("84912345678") == "0912345678"


def test_normalize_phone_number_with_plus84():
	"""Test chuẩn hóa SĐT bắt đầu với +84."""
	assert normalize_phone_number("+84912345678") == "0912345678"


def test_normalize_phone_number_with_spaces():
	"""Test chuẩn hóa SĐT có khoảng trắng."""
	assert normalize_phone_number("  +84 912 345 678  ") == "0912345678"


def test_normalize_phone_number_invalid():
	"""Test chuẩn hóa SĐT không hợp lệ."""
	with pytest.raises(ValueError):
		normalize_phone_number("123456")  # Quá ngắn


def test_validate_phone_number_valid():
	"""Test kiểm tra SĐT hợp lệ."""
	assert validate_phone_number("0912345678") is True
	assert validate_phone_number("+84912345678") is True


def test_validate_phone_number_invalid():
	"""Test kiểm tra SĐT không hợp lệ."""
	assert validate_phone_number("123456") is False
	assert validate_phone_number("invalid") is False


# ============================================================================
# TESTS - CRUD
# ============================================================================


def test_create_customer_walk_in(db: Session):
	"""Test tạo khách hàng vãng lai."""
	customer = crud.create_customer(
		db,
		full_name="Nguyễn Văn A",
		phone_number="0912345678",
		user_id=None,
	)
	assert customer.id is not None
	assert customer.full_name == "Nguyễn Văn A"
	assert customer.phone_number == "0912345678"
	assert customer.user_id is None
	assert customer.deleted_at is None


def test_get_customer_by_id(db: Session):
	"""Test lấy khách hàng theo ID."""
	customer = crud.create_customer(
		db,
		full_name="Nguyễn Văn A",
		phone_number="0912345678",
	)
	retrieved = crud.get_customer_by_id(db, customer.id)
	assert retrieved.id == customer.id
	assert retrieved.full_name == "Nguyễn Văn A"


def test_get_customer_by_phone_number(db: Session):
	"""Test lấy khách hàng theo SĐT."""
	customer = crud.create_customer(
		db,
		full_name="Nguyễn Văn A",
		phone_number="0912345678",
	)
	retrieved = crud.get_customer_by_phone_number(db, "0912345678")
	assert retrieved.id == customer.id


def test_get_customer_by_user_id(db: Session):
	"""Test lấy khách hàng theo user_id."""
	customer = crud.create_customer(
		db,
		user_id=1,
		full_name="Nguyễn Văn A",
		phone_number="0912345678",
	)
	retrieved = crud.get_customer_by_user_id(db, 1)
	assert retrieved.id == customer.id
	assert retrieved.user_id == 1


def test_update_customer(db: Session):
	"""Test cập nhật thông tin khách hàng."""
	customer = crud.create_customer(
		db,
		full_name="Nguyễn Văn A",
		phone_number="0912345678",
	)
	updated = crud.update_customer(
		db,
		customer.id,
		{"full_name": "Nguyễn Văn B", "gender": "Nam"},
	)
	assert updated.full_name == "Nguyễn Văn B"
	assert updated.gender == "Nam"


def test_soft_delete_customer(db: Session):
	"""Test xóa mềm khách hàng."""
	customer = crud.create_customer(
		db,
		full_name="Nguyễn Văn A",
		phone_number="0912345678",
	)
	success = crud.soft_delete_customer(db, customer.id)
	assert success is True

	# Kiểm tra không lấy được khách hàng đã xóa (default)
	retrieved = crud.get_customer_by_id(db, customer.id, include_deleted=False)
	assert retrieved is None

	# Kiểm tra lấy được khách hàng đã xóa (include_deleted=True)
	retrieved_with_deleted = crud.get_customer_by_id(
		db, customer.id, include_deleted=True
	)
	assert retrieved_with_deleted is not None
	assert retrieved_with_deleted.deleted_at is not None


def test_restore_customer(db: Session):
	"""Test khôi phục khách hàng."""
	customer = crud.create_customer(
		db,
		full_name="Nguyễn Văn A",
		phone_number="0912345678",
	)
	crud.soft_delete_customer(db, customer.id)
	success = crud.restore_customer(db, customer.id)
	assert success is True

	# Kiểm tra lấy được khách hàng đã khôi phục
	retrieved = crud.get_customer_by_id(db, customer.id, include_deleted=False)
	assert retrieved is not None
	assert retrieved.deleted_at is None


def test_find_customer_by_query(db: Session):
	"""Test tìm kiếm khách hàng."""
	crud.create_customer(db, full_name="Nguyễn Văn A", phone_number="0912345678")
	crud.create_customer(db, full_name="Trần Thị B", phone_number="0987654321")

	# Tìm kiếm theo tên
	customers, total = crud.find_customer_by_query(db, search_query="Nguyễn")
	assert len(customers) == 1
	assert total == 1
	assert customers[0].full_name == "Nguyễn Văn A"

	# Tìm kiếm theo SĐT
	customers, total = crud.find_customer_by_query(db, search_query="0987654321")
	assert len(customers) == 1
	assert total == 1


# ============================================================================
# TESTS - SERVICE
# ============================================================================


def test_create_walk_in_customer(db: Session):
	"""Test tạo khách hàng vãng lai qua service."""
	customer = service.create_walk_in_customer(
		db,
		full_name="Nguyễn Văn A",
		phone_number="0912345678",
	)
	assert customer.user_id is None
	assert customer.full_name == "Nguyễn Văn A"


def test_create_walk_in_customer_duplicate_phone(db: Session):
	"""Test lỗi khi tạo khách hàng vãng lai với SĐT trùng."""
	service.create_walk_in_customer(db, "Nguyễn Văn A", "0912345678")

	with pytest.raises(service.PhoneNumberAlreadyExistsError):
		service.create_walk_in_customer(db, "Trần Thị B", "0912345678")


def test_create_online_customer_with_user(db: Session):
	"""Test tạo hồ sơ khách hàng online stub."""
	customer = service.create_online_customer_with_user(
		db,
		user_id=1,
		full_name=None,
		phone_number=None,
	)
	assert customer.user_id == 1
	assert customer.full_name is None
	assert customer.phone_number is None


def test_complete_customer_profile(db: Session):
	"""Test hoàn thành hồ sơ khách hàng."""
	customer = service.create_online_customer_with_user(db, user_id=1)
	updated = service.complete_customer_profile(
		db,
		customer.id,
		full_name="Nguyễn Văn A",
		phone_number="0912345678",
	)
	assert updated.full_name == "Nguyễn Văn A"
	assert updated.phone_number == "0912345678"


def test_search_customers(db: Session):
	"""Test tìm kiếm khách hàng qua service."""
	service.create_walk_in_customer(db, "Nguyễn Văn A", "0912345678")
	service.create_walk_in_customer(db, "Trần Thị B", "0987654321")

	customers, total, total_pages = service.search_customers(
		db, search_query="Nguyễn"
	)
	assert len(customers) == 1
	assert total == 1
	assert total_pages == 1


if __name__ == "__main__":
	pytest.main([__file__, "-v"])
