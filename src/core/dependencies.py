"""Định nghĩa dependencies chung cho FastAPI (placeholder)."""

# TODO: khai báo dependency injection (database, auth) khi implement
"""Các dependency dùng chung cho FastAPI: xác thực và phân quyền.

Bao gồm:
- get_current_user: Lấy user từ JWT Bearer token.
- require_roles: Kiểm tra RBAC theo danh sách roles yêu cầu.
"""

from typing import Callable, Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from src.core.db import get_session
from src.core.security import decode_jwt_token
from src.modules.auth.models import User


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
	db: Session = Depends(get_session),
	creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
	"""Giải mã JWT từ header Authorization và trả về đối tượng User.

	- Trả 401 nếu không có hoặc token không hợp lệ.
	"""

	if not creds or not creds.scheme.lower() == "bearer":
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Thiếu token")

	try:
		payload = decode_jwt_token(creds.credentials)
	except Exception:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ")

	user_id = payload.get("sub")
	if not user_id:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token thiếu sub")

	user = db.get(User, int(user_id))
	if not user or not user.is_active:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Người dùng không tồn tại/không hoạt động")
	return user


def require_roles(*required_roles: str) -> Callable[[User], User]:
    """Factory tạo dependency kiểm tra quyền truy cập theo roles.

    Sử dụng: Depends(require_roles("admin", "manager"))
    """

    def _checker(user: User = Depends(get_current_user)) -> User:
        # Lấy tên các role của user từ CSDL
        user_roles: set[str] = {role.name for role in user.roles}
        if not user_roles.intersection(set(required_roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Không đủ quyền truy cập"
            )
        return user

    return _checker


def get_admin_user(user: User = Depends(require_roles("admin"))) -> User:
    """Dependency tiện ích để yêu cầu quyền admin."""
    return user
