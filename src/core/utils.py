"""Utility functions dùng chung cho hệ thống.

Bao gồm: phone number normalize, formatters, validators, datetime utilities, v.v.
"""

import re
from datetime import datetime, timezone, timedelta
from typing import Optional


def normalize_phone_number(phone: str) -> str:
    """Chuẩn hóa số điện thoại Việt Nam.

    Xử lý các định dạng:
    - 0912345678 → 0912345678
    - +84912345678 → 0912345678
    - 84912345678 → 0912345678

    Args:
            phone: Chuỗi số điện thoại

    Returns:
            Số điện thoại đã chuẩn hóa (bắt đầu bằng 0)

    Raises:
            ValueError: Nếu số điện thoại không hợp lệ
    """
    # Loại bỏ khoảng trắng
    phone = phone.strip()

    # Xóa tất cả ký tự không phải số
    phone = re.sub(r"\D", "", phone)

    # Xử lý +84 → 0
    if phone.startswith("84"):
        phone = "0" + phone[2:]

    # Xử lý country code Việt Nam (84)
    if phone.startswith("884"):
        phone = "0" + phone[3:]

    # Kiểm tra độ dài hợp lệ (số di động VN: 10 chữ số, bắt đầu 0)
    if not phone.startswith("0") or len(phone) != 10:
        raise ValueError(f"Số điện thoại không hợp lệ: {phone}")

    # Kiểm tra định dạng (phải là 0 + 9 chữ số)
    if not re.match(r"^0\d{9}$", phone):
        raise ValueError(f"Số điện thoại không hợp lệ: {phone}")

    return phone


def validate_phone_number(phone: str) -> bool:
    """Kiểm tra số điện thoại có hợp lệ không.

    Args:
            phone: Chuỗi số điện thoại

    Returns:
            True nếu hợp lệ, False nếu không
    """
    try:
        normalize_phone_number(phone)
        return True
    except ValueError:
        return False


def validate_full_name(name: Optional[str]) -> bool:
    """Kiểm tra họ tên có hợp lệ không.

    Args:
            name: Họ tên

    Returns:
            True nếu hợp lệ, False nếu không
    """
    if not name:
        return False
    if len(name) < 1 or len(name) > 255:
        return False
    # Cho phép tiếng Việt, khoảng trắng, dấu câu cơ bản
    if not re.match(r"^[\w\s\-\'\`À-ỿ]+$", name, re.UNICODE):
        return False
    return True


# ============================================================================
# DATETIME UTILITIES
# ============================================================================


def get_utc_now() -> datetime:
    """Lấy thời gian hiện tại UTC (timezone-aware).

    Returns:
            Datetime object với timezone UTC
    """
    return datetime.now(timezone.utc)


def get_expiry_time(hours: int) -> datetime:
    """Tính thời gian hết hạn từ bây giờ.

    Args:
            hours: Số giờ tính từ bây giờ

    Returns:
            Datetime hết hạn
    """
    return get_utc_now() + timedelta(hours=hours)


def is_token_expired(expires_at: datetime) -> bool:
    """Kiểm tra token đã hết hạn hay chưa.

    Args:
            expires_at: Thời gian hết hạn của token

    Returns:
            True nếu token đã hết hạn
    """
    # Nếu expires_at là naive, giả định nó là UTC
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at < get_utc_now()
