# Quick Start - Module Auth

Hướng dẫn nhanh để hiểu và sử dụng module auth.

## 📋 5 phút Overview

### Là gì?

Module `auth` xử lý:

- 🔐 **Đăng ký + Email verification** (user phải verify email trước khi dùng)
- 🔑 **Đăng nhập** (trả JWT access token + HTTP-only refresh token cookie)
- 🔄 **Gia hạn token** (dùng refresh token để lấy access token mới)
- 🚪 **Đăng xuất** (revoke refresh token)
- 🔓 **Quên mật khẩu** (email reset + confirm password mới)

### Cấu trúc

```
models.py  ─┐
            ├─→ router.py (Endpoints)
schemas.py ─┤
            ├─→ service.py (Business Logic)
crud.py ────┤
            ├─→ Database
```

## 🚀 Chạy Demo

### 1. Setup

```bash
# Khởi động server
uvicorn src.main:app --reload

# Server chạy tại: http://localhost:8000
```

### 2. Truy cập Swagger UI

```
http://localhost:8000/docs
```

### 3. Test Endpoints

**A. Đăng ký**

```
POST /auth/register
{
  "email": "test@example.com",
  "password": "SecurePass123"
}
```

Response:

```json
{
  "message": "Đăng ký thành công. Vui lòng xác minh email",
  "email": "test@example.com"
}
```

**B. Xác minh email** (dùng token từ email)

```
POST /auth/verify-email
{
  "token": "<token-from-email>"
}
```

**C. Đăng nhập**

```
POST /auth/login
{
  "email": "test@example.com",
  "password": "SecurePass123"
}
```

Response:

```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

_Cookie `refresh_token` được set tự động_

**D. Gia hạn token**

```
POST /auth/refresh
(Cookie sẽ được gửi tự động)
```

Response:

```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

## 💡 Ý Tưởng Thiết Kế

### Tại sao User phải verify email?

Để đảm bảo:

- ✅ Email hợp lệ (người dùng có quyền truy cập)
- ✅ Nhận email alerts sau này
- ✅ Chống spam registration

### Tại sao lại có 2 loại token?

| Token       | TTL    | Mục đích         | Lưu trữ          |
| ----------- | ------ | ---------------- | ---------------- |
| **Access**  | 15 min | Xác thực request | Memory (Browser) |
| **Refresh** | 7 ngày | Lấy token mới    | Cookie HTTP-only |

Lợi ích:

- Access token ngắn → nếu bị leak, nguy hiểm ít
- Refresh token dài → tránh phải login lại thường xuyên
- HTTP-only cookie → chống XSS

### Tại sao delay khi email không tồn tại?

**Enumeration Attack:** Attacker có thể phát hiện email nào đã register bằng cách check response time.

**Solution:** Delay 1-2 giây khi email không tồn tại → response time luôn gần nhau.

## 🔧 Cách Extend

### Thêm Role-Based Access Control (RBAC)

**Current:** `User.roles = "user,admin"` (string)

**To implement RBAC:**

```python
# dependencies.py
from fastapi import Depends, HTTPException

def require_roles(required_roles: list[str]):
    async def check_role(user: User = Depends(get_current_user)):
        user_roles = user.roles.split(',')
        if not any(r in user_roles for r in required_roles):
            raise HTTPException(status_code=403, detail="Không có quyền")
        return user
    return check_role

# Usage trong router
@router.get("/admin-only")
def admin_endpoint(user: User = Depends(require_roles(["admin"]))):
    return {"message": f"Hello {user.email} (admin)"}
```

### Thêm Social Login (Google OAuth)

Có sẵn config:

```python
# config.py
GOOGLE_CLIENT_ID: str
GOOGLE_CLIENT_SECRET: str
```

Implementation không có trong plan, nhưng cấu hình đã sẵn.

### Thêm 2FA (Two-Factor Authentication)

```python
# models.py
class User(SQLModel, table=True):
    # ... existing fields ...
    two_fa_enabled: bool = False
    two_fa_secret: Optional[str] = None

# Service
def enable_2fa(user: User) -> str:
    # Tạo QR code (pyotp)
    # Return secret
    pass

def verify_2fa_token(user: User, token: str) -> bool:
    # Xác minh token
    pass
```

## 🧪 Unit Tests

### Basic Test Structure

```python
# tests/test_auth.py
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_register_success():
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "SecurePass123"}
    )
    assert response.status_code == 201
    assert response.json()["message"] == "Đăng ký thành công..."

def test_login_success():
    # Register first
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "SecurePass123"}
    )

    # Verify email (mock token verification)
    # ... verify email logic ...

    # Login
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "SecurePass123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_fail_wrong_password():
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "WrongPassword"}
    )
    assert response.status_code == 401
```

## 📊 Database Schema

```sql
-- User
CREATE TABLE "user" (
  id SERIAL PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  password_hash VARCHAR NOT NULL,
  roles VARCHAR DEFAULT 'user',
  is_active BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- RefreshToken
CREATE TABLE refreshtoken (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES "user"(id),
  token VARCHAR UNIQUE NOT NULL,
  is_revoked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- VerificationToken (Email verify)
CREATE TABLE verificationtoken (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES "user"(id),
  token VARCHAR UNIQUE NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- ResetPasswordToken
CREATE TABLE resetpasswordtoken (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES "user"(id),
  token VARCHAR UNIQUE NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔐 Security Checklist

- ✅ Password hashing (bcrypt)
- ✅ JWT signed (HS256)
- ✅ Refresh token HTTP-only cookie
- ✅ Token TTL (expires_at)
- ✅ Revocation support (is_revoked)
- ✅ Enumeration protection (delay)
- ⚠️ HTTPS (configure in production)
- ⚠️ Rate limiting (not implemented)
- ⚠️ CORS (configure in main.py)

## 🐛 Common Issues

### Issue: Email không được gửi

**Nguyên nhân:** SMTP config sai hoặc AppPassword không hợp lệ

**Fix:**

```env
# Gmail: Dùng App Password
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_STARTTLS=true
MAIL_SSL_TLS=false
```

### Issue: Login thất bại (403 Forbidden)

**Nguyên nhân:** User chưa verify email

**Fix:** Verify email trước (xác minh token từ email)

### Issue: Refresh token expired

**Nguyên nhân:** Refresh token hơn 7 ngày tuổi

**Fix:** User phải login lại

## 📚 File Details

| File         | Mục đích                  | Dòng code |
| ------------ | ------------------------- | --------- |
| `models.py`  | Database schema           | ~50       |
| `schemas.py` | Request/Response DTOs     | ~60       |
| `crud.py`    | DB operations             | ~150      |
| `service.py` | Business logic            | ~300      |
| `router.py`  | API endpoints             | ~200      |
| `email.py`   | Email templates + sending | ~350      |

## 🎯 Next Steps

- [ ] Thêm rate limiting
- [ ] Thêm background task cleanup (expired tokens)
- [ ] Thêm logging/audit trail
- [ ] Implement RBAC (require_roles dependency)
- [ ] Add 2FA support
- [ ] Integrate with Google OAuth
- [ ] Write comprehensive unit tests
- [ ] Document API with OpenAPI examples

## 🔗 Links

- **Full Docs:** `docs/AUTH_API_GUIDE.md`
- **Plan:** `docs/features/0001_PLAN.md` (xác thực) + `0002_PLAN.md` (email)
- **Swagger:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
