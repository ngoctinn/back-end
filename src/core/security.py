"""Tiện ích bảo mật chung: JWT và hashing mật khẩu.

Ghi chú:
- Sử dụng thuật toán HS256 (được cấu hình qua settings.ALGORITHM).
- Hash mật khẩu bằng thư viện bcrypt.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import bcrypt
import jwt

from src.core.config import settings


def hash_password(plain_password: str) -> str:
	"""Hash mật khẩu bằng bcrypt và trả về chuỗi đã mã hóa.

	- Đầu vào: mật khẩu thuần (plain text)
	- Đầu ra: mật khẩu đã hash (str)
	"""

	salt = bcrypt.gensalt()
	hashed: bytes = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
	return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
	"""Kiểm tra mật khẩu thuần có khớp với hash hay không."""

	try:
		return bcrypt.checkpw(
			plain_password.encode("utf-8"), hashed_password.encode("utf-8")
		)
	except Exception:
		return False


def create_jwt_token(subject: Dict[str, Any], expires_delta: timedelta) -> str:
	"""Tạo JWT token với payload `subject` và thời gian hết hạn.

	- Claims tối thiểu: `exp`, `iat`.
	- Trả về: chuỗi JWT đã ký.
	"""

	now = datetime.now(timezone.utc)
	payload: Dict[str, Any] = {
		"iat": int(now.timestamp()),
		"exp": int((now + expires_delta).timestamp()),
		**subject,
	}
	token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
	return token


def decode_jwt_token(token: str) -> Dict[str, Any]:
	"""Giải mã và xác minh JWT, trả về payload nếu hợp lệ.

	- Ném `jwt.PyJWTError` nếu token không hợp lệ hoặc hết hạn.
	"""

	payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
	return payload
