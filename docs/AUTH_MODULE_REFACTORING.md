# AUTH MODULE REFACTORING - TECHNICAL DOCUMENTATION

## Overview

Auth module đã được refactor từ một single service.py (312 dòng) thành các module chuyên biệt với trách nhiệm rõ ràng:

```
src/modules/auth/
├── auth_service.py          (150 dòng) - Đăng ký, đăng nhập, logout, refresh
├── token_service.py         (160 dòng) - Email verification, password reset
├── service.py               (50 dòng)  - Re-export wrapper (backward compatibility)
├── router.py                (211 dòng) - API endpoints
├── crud.py                  (163 dòng) - Database access + new cleanup methods
├── models.py                (104 dòng) - SQLModel definitions
├── schemas.py               (56 dòng)  - Pydantic schemas
└── __init__.py
```

## Module Descriptions

### 1. auth_service.py

**Trách nhiệm**: Xử lý authentication flows

**Functions**:

- `create_access_token_for_user(user)` - Tạo JWT access token
- `create_refresh_token_value()` - Tạo opaque refresh token
- `hash_password(plain_password)` - Hash mật khẩu
- `verify_password(plain, hashed)` - Xác minh mật khẩu
- `register_user(db, email, password)` - Đăng ký user mới
- `login_user(db, email, password)` - Xác thực và cấp tokens
- `refresh_access_token(db, refresh_token)` - Cấp access token mới
- `logout_user(db, refresh_token)` - Thu hồi refresh token

**Dependencies**: crud, core.security, core.email

**Related Endpoints**:

- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout

### 2. token_service.py

**Trách nhiệm**: Xử lý token lifecycle (verification, password reset)

**Functions**:

- `create_verification_token_value()` - Tạo token xác minh email
- `create_reset_token_value()` - Tạo token đặt lại mật khẩu
- `initiate_email_verification(db, user_id)` - Gửi lại email xác minh
- `confirm_email(db, token)` - Xác minh email từ token
- `initiate_password_reset(db, email)` - Tạo token reset, gửi email
- `confirm_password_reset(db, token, new_password)` - Đặt lại mật khẩu

**Dependencies**: crud, core.email, core.security

**Related Endpoints**:

- POST /auth/verify-email
- POST /auth/resend-verification-email (NEW)
- POST /auth/password-reset
- POST /auth/confirm-password-reset

### 3. service.py (Wrapper for Backward Compatibility)

**Trách nhiệm**: Re-export tất cả functions từ auth_service.py và token_service.py

**Purpose**: Đảm bảo code cũ không break khi import từ service.py

**Migration Path**: Nếu code khác import từ service.py, nó vẫn hoạt động

## Database Changes

### CRUD Enhancements (crud.py)

**New Functions**:

```python
def cleanup_old_refresh_tokens(db: Session, days: int = 7) -> int:
    """Xóa revoked refresh tokens cũ hơn N ngày."""
```

**Existing Functions** (unchanged):

- `delete_expired_tokens()` - Xóa verification/reset tokens hết hạn

## Background Tasks

### New Background Tasks (core/background_tasks.py)

```python
def cleanup_revoked_refresh_tokens():
    """Xóa refresh tokens đã bị thu hồi cổ hơn 7 ngày."""

def cleanup_expired_tokens():
    """Xóa token xác minh hết hạn."""

def run_all_cleanup_tasks():
    """Chạy tất cả cleanup tasks."""
```

**Usage Recommendation**:

- Chạy `cleanup_revoked_refresh_tokens()` hàng tuần
- Chạy `cleanup_expired_tokens()` hàng ngày
- Sử dụng APScheduler hoặc Celery để schedule

## Router Changes

### New Endpoint Implementation

**POST /auth/resend-verification-email**

```python
Endpoint:
  POST /auth/resend-verification-email

Authorization:
  Requires JWT Bearer token (get_current_user)

Response:
  {
    "message": "Email xác minh đã được gửi lại",
    "email": "user@example.com"
  }

Use Case:
  User đã đăng ký nhưng bỏ lỡ email xác minh
  User request gửi lại email xác minh
```

### Updated Imports

```python
from src.core.dependencies import get_current_user
from . import auth_service, token_service
from .models import User
```

## Migration Guide

### Updating Existing Code

**Old way** (still works - backward compatible):

```python
from src.modules.auth import service

result = service.register_user(db, email, password)
```

**New way** (recommended):

```python
from src.modules.auth import auth_service, token_service

result = auth_service.register_user(db, email, password)
```

## Testing Recommendations

### Unit Tests Structure

```
tests/
├── test_auth_service.py
│   ├── test_register_user
│   ├── test_login_user
│   ├── test_refresh_access_token
│   └── test_logout_user
│
├── test_token_service.py
│   ├── test_confirm_email
│   ├── test_initiate_password_reset
│   └── test_confirm_password_reset
│
└── test_background_tasks.py
    ├── test_cleanup_expired_tokens
    └── test_cleanup_revoked_refresh_tokens
```

## Performance Improvements

1. **Module Loading**: Tách module giúp load time nhanh hơn (import chỉ cần modules)
2. **Memory**: Mỗi module nhỏ hơn dễ optimize
3. **Testing**: Có thể test từng module độc lập
4. **Cleanup**: Background tasks tự động xóa token cũ → DB không bị bloat

## Security Enhancements

1. **Resend Verification**: Yêu cầu JWT auth → chống abuse
2. **Token Cleanup**: Xóa old tokens → giảm attack surface
3. **Revoke History**: Kiểm tra is_revoked flag → chống reuse

## Deployment Notes

1. ✅ **Backward Compatible**: Existing code không cần thay đổi
2. ✅ **No DB Migration**: Không cần migration mới (chỉ thêm logic cleanup)
3. ⚠️ **Setup Scheduler**: Cần setup APScheduler/Celery cho background tasks
4. ⚠️ **Test Infrastructure**: Cần fix test DB setup (migrations cho test DB)

## Files Summary

| File                | LOC | Purpose                        |
| ------------------- | --- | ------------------------------ |
| auth_service.py     | 150 | Core authentication flows      |
| token_service.py    | 160 | Token lifecycle management     |
| service.py          | 50  | Backward compatibility wrapper |
| router.py           | 211 | API endpoints                  |
| crud.py             | 163 | Database access layer          |
| background_tasks.py | 60  | Async cleanup tasks            |

**Total**: ~800 LOC (organized, testable, maintainable)
