# 🔐 Auth Module - Hướng Dẫn Chi Tiết

**Module:** `src/modules/auth`  
**Phiên bản:** 1.0  
**Cập nhật:** Oct 2025

---

## 📑 Mục Lục

1. [🎯 Tổng Quan](#-tổng-quan)
2. [📊 Cấu Trúc Module](#-cấu-trúc-module)
3. [🗄️ Database Models](#-database-models)
4. [🔑 Quản Lý Token](#-quản-lý-token)
5. [🔄 Luồng Xác Thực Chi Tiết](#-luồng-xác-thực-chi-tiết)
6. [📡 API Endpoints](#-api-endpoints)
7. [💻 Code Examples](#-code-examples)
8. [🔒 Bảo Mật](#-bảo-mật)
9. [⚙️ Cấu Hình](#-cấu-hình)
10. [🐛 Troubleshooting](#-troubleshooting)

---

## 🎯 Tổng Quan

Module Auth cung cấp hệ thống xác thực & ủy quyền hoàn chỉnh cho ứng dụng Spa Online CRM.

**Tính năng chính:**

- ✅ Đăng ký với xác minh email (OTP)
- ✅ Đăng nhập với JWT + Refresh Token
- ✅ Gia hạn token tự động
- ✅ Đăng xuất an toàn (revoke token)
- ✅ Quên mật khẩu + Đặt lại mật khẩu
- ✅ Bảo mật cao: bcrypt hashing, HTTP-only cookies, JWT signed

---

## 📊 Cấu Trúc Module

### Thư mục:

```
src/modules/auth/
├── __init__.py              # Module initialization
├── models.py                # SQLModel models (User, tokens)
├── schemas.py               # Pydantic DTOs (request/response)
├── crud.py                  # Database operations
├── router.py                # API endpoints (FastAPI router)
├── auth_service.py          # Authentication business logic
├── token_service.py         # Token management logic
└── service.py               # Backward compatibility wrapper
```

### Phân tách trách nhiệm:

- **`models.py`**: Định nghĩa bảng database
- **`schemas.py`**: Định nghĩa request/response bodies
- **`crud.py`**: Thao tác trực tiếp với database (Create, Read, Update, Delete)
- **`auth_service.py`**: Logic đăng nhập/đăng xuất/refresh token
- **`token_service.py`**: Logic xác minh email & reset password
- **`router.py`**: HTTP endpoints, dependency injection, error handling

---

## 🗄️ Database Models

### 1. User

Bảng người dùng, phục vụ xác thực hệ thống.

```python
class User(SQLModel, table=True):
    """Tài khoản người dùng."""

    id: Optional[int]              # Primary key
    email: str                     # Unique, indexed
    password_hash: str             # Bcrypt hash
    roles: str                     # Comma-separated (ví dụ: "user,admin")
    is_active: bool = False        # True = email đã verify
    created_at: datetime           # UTC timestamp
```

**Ý nghĩa:**

- `is_active = False`: Tài khoản vừa tạo, chưa verify email
- `is_active = True`: Email đã verify, có thể đăng nhập
- `roles`: Chuỗi vai trò (mặc định "user"), dùng để phân quyền

---

### 2. RefreshToken

Token để gia hạn access token, lưu dạng opaque (chuỗi random).

```python
class RefreshToken(SQLModel, table=True):
    """Refresh token - lưu dạng opaque (không phải JWT)."""

    id: Optional[int]              # Primary key
    user_id: int                   # Foreign key → User
    token: str                     # Random string (token_urlsafe(48))
    is_revoked: bool = False       # True = đã logout
    created_at: datetime           # UTC timestamp
```

**Ý nghĩa:**

- Lưu trên database để có thể thu hồi (revoke) khi logout
- `is_revoked = True`: Token bị vô hiệu hóa → không thể tạo access token
- TTL quản lý bằng app config, không lưu trong DB

---

### 3. VerificationToken

Token xác minh email, dùng một lần (one-time use).

```python
class VerificationToken(SQLModel, table=True):
    """Token xác minh email (OTP)."""

    id: Optional[int]              # Primary key
    user_id: int                   # Foreign key → User
    token: str                     # Random string (token_urlsafe(32))
    expires_at: datetime           # Hết hạn sau 24 giờ
    created_at: datetime           # UTC timestamp
```

**Ý nghĩa:**

- Gửi trong email verification link: `/auth/verify-email?token=XXX`
- TTL: 24 giờ (cấu hình: `VERIFICATION_TOKEN_EXPIRE_HOURS`)
- Xóa sau khi verify hoặc hết hạn

---

### 4. ResetPasswordToken

Token đặt lại mật khẩu, dùng một lần.

```python
class ResetPasswordToken(SQLModel, table=True):
    """Token đặt lại mật khẩu (OTP)."""

    id: Optional[int]              # Primary key
    user_id: int                   # Foreign key → User
    token: str                     # Random string (token_urlsafe(32))
    expires_at: datetime           # Hết hạn sau 1 giờ
    created_at: datetime           # UTC timestamp
```

**Ý nghĩa:**

- Gửi trong password reset email link
- TTL: 1 giờ (cấu hình: `PASSWORD_RESET_TOKEN_EXPIRE_HOURS`)
- Xóa sau khi reset hoặc hết hạn

---

## 🔑 Quản Lý Token

### Access Token (JWT)

**Loại:** JWT (JSON Web Token), signed với SECRET_KEY

```json
{
  "sub": "1",
  "roles": "user",
  "iat": 1697520000,
  "exp": 1697520900
}
```

**Đặc tính:**

- TTL: 15 phút (cấu hình: `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Được gửi trong header: `Authorization: Bearer <access_token>`
- Chứa thông tin: `user_id` (sub), `roles`
- Có thể giải mã mà không cần server (stateless)

---

### Refresh Token (Opaque)

**Loại:** Chuỗi random, lưu trong database

**Đặc tính:**

- TTL: 7 ngày (cấu hình: `REFRESH_TOKEN_EXPIRE_DAYS`)
- Lưu trong HTTP-only cookie: `refresh_token`
- Dùng để tạo access token mới
- Có thể revoke (logout)
- Stateful: cần kiểm tra database

---

### So Sánh

| Thuộc tính | Access Token            | Refresh Token    |
| :--------- | :---------------------- | :--------------- |
| Loại       | JWT                     | Opaque string    |
| TTL        | 15 min                  | 7 ngày           |
| Lưu ở      | Header (Authorization)  | HTTP-only Cookie |
| Giải mã    | Có (stateless)          | Không (stateful) |
| Revoke     | Không (hết hạn tự động) | Có (lưu DB)      |
| Dùng để    | Gọi API                 | Tạo access token |

---

## 🔄 Luồng Xác Thực Chi Tiết

### 1️⃣ Đăng Ký + Verify Email

#### Bước 1: Đăng ký

**Request:**

```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response:**

```json
{
  "message": "Đăng ký thành công. Vui lòng xác minh email",
  "email": "user@example.com"
}
```

**Quy trình:**

1. Validate email (format, not exists)
2. Hash password với bcrypt
3. Tạo User với `is_active = False`
4. Tạo VerificationToken (TTL 24h)
5. Gửi email xác minh
6. Trả response

**Email xác minh chứa:**

```html
Vui lòng nhấp vào link dưới để xác minh email:
https://backend-url/auth/verify-email?token=<token>
  Link hết hạn sau 24 giờ.</token
>
```

---

#### Bước 2: Xác minh email

**Request:**

```bash
POST /auth/verify-email
Content-Type: application/json

{
  "token": "token-from-email"
}
```

**Response:**

```json
{
  "message": "Email xác minh thành công",
  "email": "user@example.com"
}
```

**Quy trình:**

1. Tìm VerificationToken trong DB
2. Kiểm tra token chưa hết hạn
3. Update User: `is_active = True`
4. Xóa token
5. Trả response

**Sau khi xác minh:**

- ✅ Có thể đăng nhập
- ✅ Có thể gọi API (với access token)

---

### 2️⃣ Đăng Nhập

**Request:**

```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Headers (tự động set):**

```
Set-Cookie: refresh_token=<token>; HttpOnly; SameSite=Lax; Max-Age=604800; Path=/
```

**Quy trình:**

1. Tìm User theo email
2. Verify password (bcrypt)
3. Kiểm tra `is_active = True`
4. Tạo Access Token (JWT, TTL 15 min)
5. Tạo Refresh Token (opaque, TTL 7 ngày)
6. Lưu RefreshToken vào DB
7. Set HTTP-only cookie
8. Trả access_token

**Sau khi đăng nhập:**

- ✅ Client lưu access_token (memory hoặc local state)
- ✅ Browser tự động gửi refresh_token cookie
- ✅ Gọi API với header: `Authorization: Bearer <access_token>`

---

### 3️⃣ Gọi API Protected

**Request:**

```bash
GET /api/profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Quy trình:**

1. Extract token từ header `Authorization: Bearer <token>`
2. Decode & verify JWT signature
3. Kiểm tra hết hạn (`exp`)
4. Lấy `user_id` từ `sub`
5. Dependency `get_current_user` trả User object
6. Endpoint nhận User object, xử lý request

---

### 4️⃣ Gia Hạn Token

**Request:**

```bash
POST /auth/refresh
Cookie: refresh_token=<refresh_token>
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Quy trình:**

1. Lấy refresh_token từ cookie
2. Kiểm tra RefreshToken trong DB
3. Kiểm tra `is_revoked = False`
4. Kiểm tra user `is_active = True`
5. Tạo Access Token mới (JWT)
6. Trả access_token

**Khi nào gọi:**

- Access token hết hạn (401 Unauthorized)
- Ứng dụng client tự động gọi khi cần
- JavaScript: catch 401 response → call `/auth/refresh` → retry request

---

### 5️⃣ Đăng Xuất

**Request:**

```bash
POST /auth/logout
Cookie: refresh_token=<refresh_token>
```

**Response:**

```json
{
  "message": "Đã đăng xuất"
}
```

**Quy trình:**

1. Lấy refresh_token từ cookie
2. Đánh dấu RefreshToken: `is_revoked = True`
3. Xóa cookie trên trình duyệt
4. Trả response

**Sau khi đăng xuất:**

- ❌ Refresh token bị vô hiệu
- ❌ Access token sắp hết hạn sẽ không tạo được token mới
- ❌ API calls không thể thành công

---

### 6️⃣ Quên Mật Khẩu

#### Bước 1: Yêu cầu Reset

**Request:**

```bash
POST /auth/password-reset
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**

```json
{
  "message": "Nếu tài khoản tồn tại, email hướng dẫn đã được gửi"
}
```

**Quy trình:**

1. Tìm User theo email
2. Nếu tồn tại:
   - Xóa ResetPasswordToken cũ (nếu có)
   - Tạo ResetPasswordToken mới (TTL 1h)
   - Gửi email reset password
3. **Luôn trả success** (chống email enumeration attack)

**Email reset password chứa:**

```html
Bạn yêu cầu đặt lại mật khẩu. Vui lòng nhấp vào link dưới:
https://backend-url/auth/confirm-password-reset?token=<token>
  Link hết hạn sau 1 giờ.</token
>
```

---

#### Bước 2: Đặt Lại Mật Khẩu

**Request:**

```bash
POST /auth/confirm-password-reset
Content-Type: application/json

{
  "token": "token-from-email",
  "new_password": "NewSecurePassword123"
}
```

**Response:**

```json
{
  "message": "Mật khẩu đã được đặt lại thành công",
  "email": "user@example.com"
}
```

**Quy trình:**

1. Tìm ResetPasswordToken trong DB
2. Kiểm tra token chưa hết hạn
3. Validate password mới (min 8 ký tự)
4. Hash password mới
5. Update User: `password_hash = new_hash`
6. **Thu hồi tất cả RefreshToken cũ** (logout khỏi tất cả devices)
7. Xóa ResetPasswordToken
8. Trả response

**Sau khi reset:**

- ✅ Password cũ không dùng được nữa
- ✅ Tất cả sessions cũ bị logout
- ✅ Cần đăng nhập lại trên tất cả devices

---

### 7️⃣ Gửi Lại Email Xác Minh

**Request:**

```bash
POST /auth/resend-verification-email
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**

```json
{
  "message": "Email xác minh đã được gửi lại",
  "email": "user@example.com"
}
```

**Quy trình:**

1. Tìm User theo email
2. Nếu không tồn tại: trả success (chống enumeration)
3. Nếu `is_active = True`: trả "Tài khoản đã được kích hoạt"
4. Nếu `is_active = False`:
   - Xóa VerificationToken cũ
   - Tạo VerificationToken mới (TTL 24h)
   - Gửi email
   - Trả success

---

## 📡 API Endpoints

### Danh sách Endpoints

| Method | Endpoint                          | Auth | Mô Tả                   |
| :----- | :-------------------------------- | :--- | :---------------------- |
| POST   | `/auth/register`                  | ❌   | Đăng ký tài khoản       |
| POST   | `/auth/verify-email`              | ❌   | Xác minh email          |
| POST   | `/auth/resend-verification-email` | ❌   | Gửi lại email xác minh  |
| POST   | `/auth/login`                     | ❌   | Đăng nhập               |
| POST   | `/auth/refresh`                   | ❌   | Gia hạn token           |
| POST   | `/auth/logout`                    | ❌   | Đăng xuất               |
| POST   | `/auth/password-reset`            | ❌   | Yêu cầu reset password  |
| POST   | `/auth/confirm-password-reset`    | ❌   | Xác nhận reset password |
| GET    | `/auth/me`                        | ✅   | Lấy thông tin user      |

### Chi tiết Endpoints

#### POST /auth/register

Đăng ký tài khoản mới.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response (201 Created):**

```json
{
  "message": "Đăng ký thành công. Vui lòng xác minh email",
  "email": "user@example.com"
}
```

**Lỗi:**

- `400`: Email đã tồn tại
- `422`: Email hoặc password không hợp lệ

---

#### POST /auth/verify-email

Xác minh email từ token (nhận từ email).

**Request Body:**

```json
{
  "token": "SFMyNTY.g2wB..."
}
```

**Response (200 OK):**

```json
{
  "message": "Email xác minh thành công",
  "email": "user@example.com"
}
```

**Lỗi:**

- `400`: Token không hợp lệ hoặc hết hạn

---

#### POST /auth/resend-verification-email

Gửi lại email xác minh.

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**

```json
{
  "message": "Email xác minh đã được gửi lại",
  "email": "user@example.com"
}
```

---

#### POST /auth/login

Đăng nhập, trả access token.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Headers (tự động):**

```
Set-Cookie: refresh_token=...; HttpOnly; SameSite=Lax; Max-Age=604800; Path=/
```

**Lỗi:**

- `401`: Email/password không hợp lệ
- `403`: Tài khoản chưa verify email

---

#### POST /auth/refresh

Gia hạn access token từ refresh token.

**Request:**

```
Cookie: refresh_token=<token>
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Lỗi:**

- `401`: Refresh token không hợp lệ hoặc hết hạn

---

#### POST /auth/logout

Đăng xuất, revoke refresh token.

**Request:**

```
Cookie: refresh_token=<token>
```

**Response (200 OK):**

```json
{
  "message": "Đã đăng xuất"
}
```

---

#### POST /auth/password-reset

Yêu cầu đặt lại mật khẩu (bước 1).

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**

```json
{
  "message": "Nếu tài khoản tồn tại, email hướng dẫn đã được gửi"
}
```

---

#### POST /auth/confirm-password-reset

Xác nhận đặt lại mật khẩu (bước 2).

**Request Body:**

```json
{
  "token": "SFMyNTY.g2wB...",
  "new_password": "NewSecurePassword123"
}
```

**Response (200 OK):**

```json
{
  "message": "Mật khẩu đã được đặt lại thành công",
  "email": "user@example.com"
}
```

**Lỗi:**

- `400`: Token không hợp lệ, hết hạn, hoặc password không hợp lệ

---

#### GET /auth/me

Lấy thông tin user hiện tại (yêu cầu xác thực).

**Request:**

```
GET /auth/me
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "id": 1,
  "email": "user@example.com",
  "roles": ["user"],
  "is_active": true
}
```

**Lỗi:**

- `401`: Thiếu hoặc token không hợp lệ

---

## 💻 Code Examples

### 1. Register & Verify Email (Client)

```javascript
// Step 1: Register
const registerRes = await fetch("/auth/register", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "user@example.com",
    password: "SecurePassword123",
  }),
});

const registerData = await registerRes.json();
console.log(registerData.message);
// "Đăng ký thành công. Vui lòng xác minh email"

// Step 2: User clicks link in email, extract token from URL
// URL: https://app.com/verify?token=<token>
const token = new URLSearchParams(window.location.search).get("token");

// Step 3: Verify email
const verifyRes = await fetch("/auth/verify-email", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ token }),
});

const verifyData = await verifyRes.json();
console.log(verifyData.message);
// "Email xác minh thành công"
```

---

### 2. Login & API Call (Client)

```javascript
// Step 1: Login
const loginRes = await fetch("/auth/login", {
  method: "POST",
  credentials: "include", // Include cookies
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "user@example.com",
    password: "SecurePassword123",
  }),
});

const loginData = await loginRes.json();
const accessToken = loginData.access_token;

// Store in memory (or local state)
localStorage.setItem("access_token", accessToken);

// Step 2: Call API with token
const apiRes = await fetch("/api/profile", {
  method: "GET",
  credentials: "include", // Include refresh_token cookie
  headers: {
    Authorization: `Bearer ${accessToken}`,
    "Content-Type": "application/json",
  },
});

if (apiRes.status === 401) {
  // Token hết hạn, gia hạn
  const refreshRes = await fetch("/auth/refresh", {
    method: "POST",
    credentials: "include",
  });

  const refreshData = await refreshRes.json();
  const newAccessToken = refreshData.access_token;
  localStorage.setItem("access_token", newAccessToken);

  // Retry API call
  const retryRes = await fetch("/api/profile", {
    method: "GET",
    credentials: "include",
    headers: {
      Authorization: `Bearer ${newAccessToken}`,
      "Content-Type": "application/json",
    },
  });
  const data = await retryRes.json();
  return data;
}

const data = await apiRes.json();
return data;
```

---

### 3. Dependency Injection (Backend)

```python
from fastapi import Depends, HTTPException
from src.core.dependencies import get_current_user
from src.modules.auth.models import User

@router.get('/api/profile')
def get_profile(current_user: User = Depends(get_current_user)):
    """Get user profile (requires auth)."""
    return {
        'id': current_user.id,
        'email': current_user.email,
        'roles': current_user.roles.split(','),
    }
```

---

### 4. Custom Dependency (Backend)

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.core.db import get_session
from src.modules.auth.models import User

def get_admin_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> User:
    """Ensure user is admin."""
    if 'admin' not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Yêu cầu quyền admin'
        )
    return current_user

@router.delete('/api/users/{user_id}')
def delete_user(
    user_id: int,
    admin: User = Depends(get_admin_user)
):
    """Delete user (admin only)."""
    # ...
```

---

## 🔒 Bảo Mật

### Password Hashing

- **Thuật toán:** bcrypt
- **Work factor:** 12 (mặc định)
- **So sánh:** Timing-safe comparison

```python
from src.core.security import hash_password, verify_password

# Hash
pwd_hash = hash_password('plain_password')

# Verify
is_valid = verify_password('plain_password', pwd_hash)
```

---

### JWT Security

- **Thuật toán:** HS256 (HMAC-SHA256)
- **Secret:** 32+ ký tự (cấu hình: `SECRET_KEY`)
- **Signature:** Signed + verified

```python
# JWT header được decode:
{
  "alg": "HS256",
  "typ": "JWT"
}

# JWT payload chứa:
{
  "sub": "1",           # user_id
  "roles": "user",
  "iat": 1697520000,    # issued at
  "exp": 1697520900     # expiration
}
```

---

### HTTP-Only Cookies

- **Refresh token:** HTTP-only, không accessible từ JavaScript
- **SameSite=Lax:** Chống CSRF
- **Secure=False** (dev), **Secure=True** (prod)

```python
response.set_cookie(
    key='refresh_token',
    value=refresh_token,
    httponly=True,        # Không accessible từ JS
    samesite='lax',       # Chống CSRF
    secure=False,         # HTTPS (dev: False, prod: True)
    max_age=604800,       # 7 days
    path='/'
)
```

---

### Token Revocation

- **Access Token:** Không thể revoke (TTL ngắn 15 min)
- **Refresh Token:** Có thể revoke (lưu DB)

```python
# Logout: revoke refresh token
def logout_user(db: Session, refresh_token: str):
    rt = db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    ).scalar_one_or_none()

    if rt:
        rt.is_revoked = True
        db.commit()
```

---

### Email Verification

- **Mục đích:** Xác nhận email tồn tại & thuộc user
- **Token TTL:** 24 giờ
- **One-time use:** Xóa sau khi verify

---

### Password Reset

- **Mục đích:** Cấp quyền thay đổi password cho user
- **Token TTL:** 1 giờ
- **One-time use:** Xóa sau khi reset
- **Revoke all sessions:** Reset password → logout khỏi tất cả devices

---

### Email Enumeration Prevention

Endpoints không tiết lộ email có tồn tại:

- `/auth/password-reset`: Luôn trả success
- `/auth/resend-verification-email`: Luôn trả success

---

## ⚙️ Cấu Hình

### Environment Variables

```bash
# JWT
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
REFRESH_TOKEN_COOKIE_NAME=refresh_token

# Email (Token TTL)
VERIFICATION_TOKEN_EXPIRE_HOURS=24
PASSWORD_RESET_TOKEN_EXPIRE_HOURS=1

# Email Service
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@spa-crm.local
```

### Settings File

```python
# src/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"

    # Token TTL
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1

    # Email
    MAIL_SERVER: str
    MAIL_PORT: int = 587
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 🐛 Troubleshooting

### Email not sending

**Problem:** Verification email không được gửi

**Solutions:**

1. Kiểm tra SMTP settings trong `.env`
2. Gmail: Enable "Less secure app access" hoặc dùng App Password
3. Check email logs: `python -c "from src.core.email import send_test_email; send_test_email()"`

---

### Token expired immediately

**Problem:** Access token expires ngay tức khắc

**Solutions:**

1. Kiểm tra `ACCESS_TOKEN_EXPIRE_MINUTES` trong config
2. Kiểm tra system time (timezone issues)
3. Kiểm tra JWT expiration logic

---

### Password reset link not working

**Problem:** Link từ email không hoạt động

**Solutions:**

1. Kiểm tra token TTL: `PASSWORD_RESET_TOKEN_EXPIRE_HOURS`
2. Kiểm tra user click link quá lâu (hết hạn)
3. Kiểm tra token format trong URL

---

### Refresh token not working

**Problem:** `/auth/refresh` trả 401

**Solutions:**

1. Kiểm tra browser gửi cookie: DevTools → Network → Cookies
2. Kiểm tra `samesite` policy (CSRF)
3. Kiểm tra `secure=True` trên HTTPS (dev: False, prod: True)
4. Kiểm tra `is_revoked` flag trong DB

---

### CORS errors when calling auth endpoints

**Problem:** Browser block requests (CORS error)

**Solutions:**

1. Kiểm tra CORS settings trong `src/main.py`
2. Thêm credentials: `credentials: 'include'` trong fetch

---

## 📚 Tham Khảo

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [Passlib/Bcrypt](https://passlib.readthedocs.io/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [RFC 6750 - OAuth 2.0 Bearer Token](https://tools.ietf.org/html/rfc6750)

---

**Last Updated:** Oct 17, 2025  
**Module Version:** 1.0  
**Status:** Production Ready ✅
