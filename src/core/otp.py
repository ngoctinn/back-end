"""OTP (One-Time Password) management cho account linking.

Sử dụng in-memory cache (có thể nâng cấp lên Redis).
OTP được gửi qua SMS hoặc email fallback.
"""

import secrets
import string
from datetime import timedelta
from typing import Optional

from src.core.utils import get_utc_now

# In-memory cache cho OTP (trong production, dùng Redis)
_otp_cache: dict[str, dict] = {}


def generate_otp(length: int = 6) -> str:
    """Tạo mã OTP ngẫu nhiên.

    Args:
            length: Độ dài OTP (default 6 ký tự)

    Returns:
            Chuỗi OTP chỉ chứa chữ số
    """
    digits = string.digits
    return "".join(secrets.choice(digits) for _ in range(length))


def send_otp_sms(phone_number: str, otp_code: str) -> bool:
    """Gửi OTP qua SMS.

    Args:
            phone_number: Số điện thoại đích
            otp_code: Mã OTP

    Returns:
            True nếu gửi thành công

    Note:
            Dev mode: In OTP ra console.
            Để triển khai thực, tích hợp SMS provider (Twilio, AWS SNS, v.v.).
    """
    # TODO: Tích hợp SMS provider thực tế
    print(f"[SMS] Gửi OTP tới {phone_number}: {otp_code}")
    return True


def store_otp(
    phone_number: str,
    otp_code: str,
    expiry_seconds: int = 300,
) -> None:
    """Lưu OTP vào cache với TTL.

    Args:
            phone_number: Số điện thoại (identifier)
            otp_code: Mã OTP
            expiry_seconds: Thời gian sống của OTP (tính bằng giây, default 5 phút)

    Note:
            Trong production, nên dùng Redis để lưu OTP.
    """
    _otp_cache[phone_number] = {
        "code": otp_code,
        "expires_at": get_utc_now() + timedelta(seconds=expiry_seconds),
        "attempts": 0,
    }


def verify_otp(phone_number: str, otp_code: str, max_attempts: int = 5) -> bool:
    """Xác minh OTP (kiểm tra hợp lệ, chưa hết hạn, và không vượt retry limit).

    Args:
            phone_number: Số điện thoại
            otp_code: Mã OTP nhập từ user
            max_attempts: Số lần nhập sai tối đa trước khi lock

    Returns:
            True nếu OTP hợp lệ, False nếu không hoặc hết hạn
    """
    if phone_number not in _otp_cache:
        return False

    otp_data = _otp_cache[phone_number]

    # Kiểm tra hết hạn
    if get_utc_now() > otp_data["expires_at"]:
        del _otp_cache[phone_number]
        return False

    # Kiểm tra vượt retry limit
    if otp_data["attempts"] >= max_attempts:
        del _otp_cache[phone_number]
        return False

    # Kiểm tra mã OTP
    if otp_data["code"] != otp_code:
        otp_data["attempts"] += 1
        return False

    return True


def clear_otp(phone_number: str) -> None:
    """Xóa OTP khỏi cache (sau khi xác minh thành công).

    Args:
            phone_number: Số điện thoại
    """
    if phone_number in _otp_cache:
        del _otp_cache[phone_number]


def get_otp_remaining_attempts(phone_number: str, max_attempts: int = 5) -> int:
    """Lấy số lần nhập sai còn lại cho OTP.

    Args:
            phone_number: Số điện thoại
            max_attempts: Tổng số lần được phép nhập

    Returns:
            Số lần còn lại, hoặc 0 nếu OTP không tồn tại/hết hạn
    """
    if phone_number not in _otp_cache:
        return 0

    otp_data = _otp_cache[phone_number]

    # Kiểm tra hết hạn
    if get_utc_now() > otp_data["expires_at"]:
        del _otp_cache[phone_number]
        return 0

    return max(0, max_attempts - otp_data["attempts"])
