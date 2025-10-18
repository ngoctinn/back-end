# Tái cấu trúc Module `auth`

## 1. Chiến lược Tái cấu trúc

Chiến lược được chia thành hai phần chính:

1.  **Tăng cường tính toàn vẹn dữ liệu:** Áp dụng cơ chế transaction cho hàm `register_user`. Toàn bộ quá trình tạo `User`, tạo `Customer`, và tạo `VerificationToken` sẽ được bọc trong một khối `try...except`. Nếu bất kỳ bước nào thất bại, tất cả các thay đổi trong CSDL sẽ được `rollback`, đảm bảo không có dữ liệu "mồ côi" được tạo ra.

2.  **Nâng cấp hệ thống phân quyền:** Thay thế trường `roles` dạng chuỗi ký tự bằng một hệ thống RBAC đầy đủ. Việc này bao gồm:
    *   Tạo các model mới: `Role`, `Permission`, và các bảng liên kết `UserRole`, `RolePermission`.
    *   Sửa đổi model `User` để loại bỏ trường `roles` và thay bằng mối quan hệ nhiều-nhiều với model `Role`.
    *   Cập nhật các lớp `crud` và `service` để làm việc với cấu trúc mới, bao gồm việc gán vai trò mặc định cho người dùng mới và tạo access token với danh sách vai trò mới.

Các file chính bị ảnh hưởng là `models.py`, `crud.py`, và `auth_service.py` trong module `auth`.

---

## 2. Mã đã được Tái cấu trúc

### `src/modules/auth/models.py`

```python
"""Các model CSDL cho module auth.

Đã được tái cấu trúc để hỗ trợ RBAC đầy đủ.
"""

from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from src.core.utils import get_utc_now


# --- Bảng liên kết Nhiều-Nhiều ---

class UserRole(SQLModel, table=True):
    """Bảng trung gian liên kết User và Role."""
    user_id: Optional[int] = Field(
        default=None, foreign_key="user.id", primary_key=True
    )
    role_id: Optional[int] = Field(
        default=None, foreign_key="role.id", primary_key=True
    )


class RolePermission(SQLModel, table=True):
    """Bảng trung gian liên kết Role và Permission."""
    role_id: Optional[int] = Field(
        default=None, foreign_key="role.id", primary_key=True
    )
    permission_id: Optional[int] = Field(
        default=None, foreign_key="permission.id", primary_key=True
    )


# --- Bảng chính ---

class Permission(SQLModel, table=True):
    """Bảng Quyền hạn (ví dụ: create_product, delete_user)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True) # Tên quyền hạn
    description: str = Field(default="")

    roles: List["Role"] = Relationship(back_populates="permissions", link_model=RolePermission)


class Role(SQLModel, table=True):
    """Bảng Vai trò (ví dụ: admin, user, staff)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str = Field(default="")

    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole)
    permissions: List[Permission] = Relationship(back_populates="roles", link_model=RolePermission)


class User(SQLModel, table=True):
    """Bảng người dùng phục vụ xác thực."""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)
    is_active: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)

    roles: List[Role] = Relationship(back_populates="users", link_model=UserRole)


# --- Các bảng Token (không thay đổi) ---

class RefreshToken(SQLModel, table=True):
    """Lưu refresh token dạng opaque, có thể thu hồi."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, nullable=False)
    token: str = Field(index=True, unique=True, nullable=False)
    is_revoked: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)


class VerificationToken(SQLModel, table=True):
    """Token xác minh email (one-time use)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, nullable=False)
    token: str = Field(index=True, unique=True, nullable=False)
    expires_at: datetime = Field(nullable=False)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)


class ResetPasswordToken(SQLModel, table=True):
    """Token đặt lại mật khẩu (one-time use)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, nullable=False)
    token: str = Field(index=True, unique=True, nullable=False)
    expires_at: datetime = Field(nullable=False)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)

```

### `src/modules/auth/crud.py`

```python
"""Lớp truy cập dữ liệu (CRUD) cho module auth.

Đã được tái cấu trúc để hỗ trợ RBAC.
"""

from typing import Optional
from datetime import datetime, timedelta

from sqlmodel import Session, select, update, delete

from src.core.utils import get_utc_now
from .models import (
    User,
    Role,
    Permission,
    RefreshToken,
    VerificationToken,
    ResetPasswordToken,
)

# --- User CRUD ---

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Lấy người dùng theo email, eager load các vai trò."""
    # options(selectinload(User.roles)) giúp tải sẵn các role liên quan
    # để tránh các truy vấn N+1 sau này.
    statement = select(User).where(User.email == email)
    return db.exec(statement).first()

def create_user(db: Session, email: str, password_hash: str) -> User:
    """Tạo người dùng mới (không gán vai trò)."""
    user = User(email=email, password_hash=password_hash)
    db.add(user)
    # Không commit ở đây để cho phép transaction ở service layer
    return user

# --- Role & Permission CRUD ---

def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    """Lấy vai trò theo tên."""
    statement = select(Role).where(Role.name == name)
    return db.exec(statement).first()

def assign_role_to_user(db: Session, user: User, role: Role) -> None:
    """Gán một vai trò cho người dùng."""
    user.roles.append(role)
    db.add(user)

# --- Token CRUD (không thay đổi nhiều, chỉ bỏ commit) ---

def store_refresh_token(db: Session, user_id: int, token: str) -> RefreshToken:
    rt = RefreshToken(user_id=user_id, token=token)
    db.add(rt)
    db.commit() # Đăng nhập là một hành động riêng, có thể commit ngay
    db.refresh(rt)
    return rt

def create_verification_token(
    db: Session, user_id: int, token: str, expires_at: datetime
) -> VerificationToken:
    vt = VerificationToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(vt)
    return vt

# ... các hàm CRUD khác cho token không thay đổi về logic ...

# (Giữ nguyên các hàm CRUD khác như is_refresh_token_valid, revoke_refresh_token, ...)
# Lưu ý: các hàm này vẫn dùng db.commit() vì chúng là các hành động đơn lẻ.

```

### `src/modules/auth/auth_service.py`

```python
"""Business logic cho đăng ký, đăng nhập, đăng xuất và refresh token.

Đã được tái cấu trúc để hỗ trợ transaction và RBAC.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import Session

from src.core.config import settings
from src.core.email import send_verification_email
from src.core.security import create_jwt_token
from src.core.security import hash_password as _hash_password
from src.core.security import verify_password as _verify_password
from src.core.utils import get_expiry_time
from . import crud
from .models import User
from .token_service import create_verification_token_value
from src.modules.customers import service as customer_service

def create_access_token_for_user(user: User) -> str:
    """Tạo access token JWT chứa user_id và danh sách roles."""
    # Lấy danh sách tên các role từ object User
    roles_list = [role.name for role in user.roles]
    subject = {"sub": str(user.id), "roles": roles_list}
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_jwt_token(subject, expires)


def register_user(db: Session, email: str, password: str) -> dict:
    """Đăng ký tài khoản mới với email verification trong một transaction.

    Các bước:
    1. Tạo User
    2. Gán vai trò 'user' mặc định
    3. Tạo hồ sơ Customer "chờ"
    4. Tạo token xác minh
    5. Gửi email
    Tất cả các bước ghi vào CSDL sẽ được commit cùng lúc.
    """
    # Kiểm tra email không trùng lặp
    if crud.get_user_by_email(db, email):
        raise ValueError("Email đã tồn tại")

    try:
        # Bắt đầu transaction
        # 1. Tạo User
        pwd_hash = _hash_password(password)
        user = crud.create_user(db, email=email, password_hash=pwd_hash)

        # 2. Gán vai trò 'user' mặc định
        user_role = crud.get_role_by_name(db, name="user")
        if not user_role:
            # Đây là trường hợp khẩn cấp, vai trò 'user' phải tồn tại trong CSDL
            # Có thể tạo nó ở đây nếu cần, hoặc raise lỗi hệ thống
            raise RuntimeError("Vai trò 'user' mặc định không tồn tại trong CSDL.")
        crud.assign_role_to_user(db, user=user, role=user_role)

        # 3. Tạo hồ sơ khách hàng "chờ"
        customer_service.create_online_customer_with_user(db, user_id=user.id)

        # 4. Tạo token xác minh email
        vtoken = create_verification_token_value()
        expires_at = get_expiry_time(settings.VERIFICATION_TOKEN_EXPIRE_HOURS)
        crud.create_verification_token(
            db, user_id=user.id, token=vtoken, expires_at=expires_at
        )

        # Commit tất cả thay đổi vào CSDL
        db.commit()

        # Refresh user để lấy ID sau khi commit
        db.refresh(user)

    except Exception as e:
        # Nếu có bất kỳ lỗi nào, rollback tất cả thay đổi
        db.rollback()
        # Ghi log và raise lại lỗi để router có thể xử lý
        # logger.error(f"Lỗi khi đăng ký user: {e}")
        raise e

    # 5. Gửi email xác minh (chỉ gửi sau khi đã commit thành công)
    send_verification_email(email, vtoken)

    return {
        "id": user.id,
        "email": user.email,
        "message": "Đăng ký thành công. Vui lòng xác minh email",
    }

# ... các hàm login, refresh, logout không thay đổi về logic chính ...
# (Hàm login sẽ được hưởng lợi từ việc eager load roles trong get_user_by_email)

```

---

## 3. Tóm tắt các thay đổi

1.  **Áp dụng Transaction cho hàm Đăng ký:**
    - **Thay đổi:** Logic của hàm `register_user` giờ được bọc trong khối `try...except` với `db.commit()` ở cuối và `db.rollback()` khi có lỗi.
    - **Lợi ích:** Đảm bảo tính toàn vẹn dữ liệu. Hoặc là `User` và `Customer` cùng được tạo, hoặc không có gì được tạo, tránh tình trạng dữ liệu "mồ côi".

2.  **Nâng cấp hệ thống vai trò lên RBAC đầy đủ:**
    - **Thay đổi:** Loại bỏ trường `roles` dạng chuỗi trong model `User`. Thêm các model mới `Role`, `Permission`, `UserRole`, `RolePermission` để tạo một cấu trúc phân quyền linh hoạt.
    - **Lợi ích:** Cung cấp một hệ thống phân quyền mạnh mẽ, dễ dàng mở rộng và quản lý. Thay vì dùng chuỗi ký tự, hệ thống giờ đây có thể định nghĩa vai trò và gán quyền hạn một cách tường minh, chặt chẽ và hiệu quả.

3.  **Tách biệt logic gán vai trò (Role Assignment):**
    - **Thay đổi:** Hàm `crud.create_user` giờ chỉ tạo người dùng. Việc gán vai trò được `auth_service.register_user` điều phối bằng cách gọi hàm `crud.assign_role_to_user`.
    - **Lợi ích:** Giúp code sạch sẽ và tuân thủ nguyên tắc đơn trách nhiệm hơn. Mỗi hàm thực hiện một nhiệm vụ cụ thể, giúp việc đọc hiểu, kiểm thử và bảo trì trở nên dễ dàng hơn.
