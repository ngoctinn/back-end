# Module Auth - Tài Liệu API

Tài liệu này mô tả chi tiết module xác thực (Authentication & Authorization) cho hệ thống Spa Online CRM.

## 📋 Tổng Quan

Module `auth` cung cấp các chức năng:

- 🔐 **Đăng ký tài khoản** với xác minh email
- 📧 **Xác minh email** thông qua link gửi qua email
- 🔑 **Đăng nhập** với JWT access token
- 🔄 **Gia hạn token** (refresh access token)
- 🚪 **Đăng xuất** (revoke refresh token)
- 🔓 **Quên mật khẩu** + **Đặt lại mật khẩu**

### Kiến Trúc

```
src/modules/auth/
├── models.py       # Database models (User, RefreshToken, VerificationToken, ResetPasswordToken)
├── schemas.py      # Pydantic schemas (Request/Response DTOs)
├── crud.py         # Data access layer (CRUD operations)
├── service.py      # Business logic (authentication flow)
└── router.py       # API endpoints
```

---

## 🔐 Luồng Xác Thực

### 1. Đăng Ký Tài Khoản + Xác Minh Email

**Bước 1: Người dùng gửi yêu cầu đăng ký**

```bash
POST /auth/register
Content-Type: application/json

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

**Quy trình backend:**

1. Validate email (định dạng, không trùng lặp)
2. Hash password bằng bcrypt
3. Tạo user với `is_active = False` (chưa kích hoạt)
4. Tạo verification token (UUID 32 byte)
5. Lưu token với TTL 24 giờ
6. Gửi email xác minh chứa link: `https://frontend/auth/verify-email?token=<token>`
7. Return success message

**Lỗi có thể:**

- `400 Bad Request`: Email không hợp lệ hoặc đã tồn tại

---

**Bước 2: Người dùng click link xác minh email**

```bash
POST /auth/verify-email
Content-Type: application/json

{
  "token": "<token-from-email>"
}
```

**Response (200 OK):**

```json
{
  "message": "Email xác minh thành công",
  "email": "user@example.com"
}
```

**Quy trình backend:**

1. Tìm token trong DB
2. Kiểm tra token chưa hết hạn (expires_at > now)
3. Update user: `is_active = True`
4. Xóa token
5. Return success

**Lỗi có thể:**

- `400 Bad Request`: Token không tồn tại hoặc đã hết hạn

---

### 2. Đăng Nhập

```bash
POST /auth/login
Content-Type: application/json

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

**Headers Response:**

```
Set-Cookie: refresh_token=<opaque-token>; HttpOnly; SameSite=Lax; Max-Age=604800; Path=/auth
```

**Quy trình backend:**

1. Tìm user theo email
2. Xác minh password (bcrypt verify)
3. Kiểm tra `is_active == True` (tài khoản đã verify)
4. Tạo JWT access token chứa: `{sub: user_id, roles: user.roles}`
5. Tạo refresh token (opaque UUID)
6. Lưu refresh token vào DB
7. Set refresh token vào HTTP-only cookie (TTL 7 ngày)
8. Return access token

**Lỗi có thể:**

- `401 Unauthorized`: Email hoặc password không hợp lệ
- `403 Forbidden`: Tài khoản chưa được kích hoạt

---

### 3. Gia Hạn Access Token

**Khi access token sắp hết hạn, frontend gọi:**

```bash
POST /auth/refresh
Cookie: refresh_token=<opaque-token>
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Quy trình backend:**

1. Lấy refresh token từ cookie
2. Kiểm tra token tồn tại, chưa bị revoke
3. Lấy user từ refresh token
4. Kiểm tra user active
5. Tạo access token mới
6. Return token mới

**Lỗi có thể:**

- `401 Unauthorized`: Refresh token không hợp lệ hoặc không tồn tại

---

### 4. Đăng Xuất

```bash
POST /auth/logout
Cookie: refresh_token=<opaque-token>
```

**Response (200 OK):**

```json
{
  "message": "Đã đăng xuất"
}
```

**Quy trình backend:**

1. Lấy refresh token từ cookie
2. Đánh dấu token là `is_revoked = True` trong DB
3. Xóa cookie trên browser
4. Return success

---

### 5. Quên Mật Khẩu

**Bước 1: Người dùng yêu cầu reset password**

```bash
POST /auth/password-reset
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response (200 OK - luôn trả success):**

```json
{
  "message": "Nếu tài khoản tồn tại, email hướng dẫn đã được gửi"
}
```

**Quy trình backend:**

1. Tìm user theo email
2. Nếu user tồn tại:
   - Tạo reset token (UUID 32 byte)
   - Lưu token với TTL 1 giờ
   - Gửi email chứa link: `https://frontend/auth/reset-password?token=<token>`
3. Nếu email không tồn tại: **Delay 1-2 giây** (chống enumeration attack)
4. Luôn return success message (chống lộ thông tin email tồn tại)

---

**Bước 2: Người dùng click link và submit password mới**

```bash
POST /auth/confirm-password-reset
Content-Type: application/json

{
  "token": "<token-from-email>",
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

**Quy trình backend:**

1. Tìm reset token trong DB
2. Kiểm tra token chưa hết hạn (TTL 1 giờ)
3. Validate password mới (minimum 8 ký tự)
4. Hash password mới
5. Update user: `password_hash = new_hash`
6. **Revoke tất cả refresh tokens cũ** của user (buộc đăng nhập lại)
7. Xóa reset token
8. Return success

**Lỗi có thể:**

- `400 Bad Request`: Token không tồn tại, hết hạn, hoặc password không hợp lệ

---

## 📚 Schemas / Models

### Request Schemas

| Schema                        | Trường       | Loại     | Yêu Cầu | Mô Tả                                  |
| ----------------------------- | ------------ | -------- | ------- | -------------------------------------- |
| `RegisterRequest`             | email        | EmailStr | ✓       | Email người dùng (unique)              |
|                               | password     | str      | ✓       | Mật khẩu (min 8, max 128 ký tự)        |
| `LoginRequest`                | email        | EmailStr | ✓       | Email người dùng                       |
|                               | password     | str      | ✓       | Mật khẩu                               |
| `VerifyEmailRequest`          | token        | str      | ✓       | Token xác minh từ email (min 32 ký tự) |
| `PasswordResetRequest`        | email        | EmailStr | ✓       | Email người dùng                       |
| `ConfirmPasswordResetRequest` | token        | str      | ✓       | Token reset từ email                   |
|                               | new_password | str      | ✓       | Mật khẩu mới (min 8, max 128 ký tự)    |

### Response Schemas

| Schema            | Trường       | Loại             | Mô Tả             |
| ----------------- | ------------ | ---------------- | ----------------- |
| `TokenResponse`   | access_token | str              | JWT access token  |
|                   | token_type   | str              | "bearer"          |
| `MessageResponse` | message      | str              | Thông báo         |
|                   | email        | EmailStr \| null | Email (tuỳ chọn)  |
| `UserResponse`    | id           | int              | User ID           |
|                   | email        | EmailStr         | Email người dùng  |
|                   | roles        | list[str]        | Danh sách roles   |
|                   | is_active    | bool             | Trạng thái active |

### Database Models

**User**

```
- id (Primary Key)
- email (Unique, Indexed)
- password_hash
- roles (chuỗi, ví dụ: "user,admin")
- is_active (boolean, mặc định False)
- created_at (datetime)
```

**RefreshToken**

```
- id (Primary Key)
- user_id (Foreign Key → User)
- token (Unique, Indexed)
- is_revoked (boolean, mặc định False)
- created_at (datetime)
```

**VerificationToken**

```
- id (Primary Key)
- user_id (Foreign Key → User)
- token (Unique, Indexed)
- expires_at (datetime, TTL 24 giờ)
- created_at (datetime)
```

**ResetPasswordToken**

```
- id (Primary Key)
- user_id (Foreign Key → User)
- token (Unique, Indexed)
- expires_at (datetime, TTL 1 giờ)
- created_at (datetime)
```

---

## 🔑 JWT Token Structure

**Payload**

```json
{
  "sub": "1", // User ID (string)
  "roles": "user,admin", // Roles (string, dấu phẩy ngăn cách)
  "exp": 1634567890, // Expiration time (Unix timestamp)
  "iat": 1634564290 // Issued at (Unix timestamp)
}
```

**Cấu hình (từ .env)**

```
SECRET_KEY=<your-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## 🛡️ Bảo Mật

### Token Hết Hạn (TTL)

| Loại Token           | TTL     | Mục Đích                       |
| -------------------- | ------- | ------------------------------ |
| Access Token         | 15 phút | Short-lived, minimize exposure |
| Refresh Token        | 7 ngày  | Long-lived, lưu browser cookie |
| Verification Token   | 24 giờ  | Email verification             |
| Reset Password Token | 1 giờ   | Một lần sử dụng                |

### Chiến Lược Bảo Mật

✅ **Password Hashing:** bcrypt với salt  
✅ **Token Storage:** Refresh token lưu HTTP-only cookie (không lộ XSS)  
✅ **Token Revocation:** Refresh token đánh dấu revoked khi logout  
✅ **Enumeration Protection:** Delay 1-2s khi email không tồn tại  
✅ **Password Reset:** Revoke tất cả token cũ khi reset password  
✅ **HTTPS Required:** Bắt buộc HTTPS trong production

### Cookie Attributes

```
Set-Cookie: refresh_token=<value>
  HttpOnly    # Không access từ JavaScript (chống XSS)
  SameSite=Lax # Chống CSRF
  Secure      # Chỉ qua HTTPS (trong production)
  Max-Age=604800 # 7 ngày
  Path=/auth  # Chỉ gửi cho path /auth
```

---

## 📧 Email Templates

### Verification Email

**Tiêu đề:** "Xác minh Email của Bạn - Spa Online CRM"

**Nội dung:**

- Chào mừng người dùng
- Button "Xác minh Email" (link chứa token)
- Text link dự phòng
- Lưu ý: Link hết hạn sau 24 giờ
- Footer: Thông tin liên lạc + disclaimer

### Reset Password Email

**Tiêu đề:** "Đặt lại Mật khẩu - Spa Online CRM"

**Nội dung:**

- Thông báo reset request
- Button "Đặt lại Mật khẩu" (link chứa token)
- Text link dự phòng
- Lưu ý: Link hết hạn sau 1 giờ
- ⚠️ Cảnh báo bảo mật
- Footer: Thông tin liên lạc + security contact

---

## 🧪 Ví Dụ Sử Dụng

### Frontend (JavaScript/TypeScript)

```javascript
// 1. Đăng ký
const registerResponse = await fetch("http://localhost:8000/auth/register", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "user@example.com",
    password: "SecurePassword123",
  }),
});

// 2. Xác minh email (sau khi click link)
const verifyResponse = await fetch("http://localhost:8000/auth/verify-email", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    token: "token-from-email",
  }),
});

// 3. Đăng nhập
const loginResponse = await fetch("http://localhost:8000/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  credentials: "include", // Để gửi/nhận cookie
  body: JSON.stringify({
    email: "user@example.com",
    password: "SecurePassword123",
  }),
});

const { access_token } = await loginResponse.json();

// 4. Sử dụng access token cho request khác
const profileResponse = await fetch("http://localhost:8000/api/users/me", {
  headers: {
    Authorization: `Bearer ${access_token}`,
  },
});

// 5. Gia hạn token (access token sắp hết hạn)
const refreshResponse = await fetch("http://localhost:8000/auth/refresh", {
  method: "POST",
  credentials: "include", // Gửi cookie refresh_token
});

const { access_token: new_token } = await refreshResponse.json();

// 6. Đăng xuất
await fetch("http://localhost:8000/auth/logout", {
  method: "POST",
  credentials: "include", // Gửi cookie để revoke
});

// 7. Quên mật khẩu
const resetRequest = await fetch("http://localhost:8000/auth/password-reset", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "user@example.com",
  }),
});

// 8. Confirm reset password (sau khi click link)
const confirmReset = await fetch(
  "http://localhost:8000/auth/confirm-password-reset",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      token: "token-from-email",
      new_password: "NewSecurePassword123",
    }),
  }
);
```

### cURL Examples

```bash
# 1. Đăng ký
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123"
  }'

# 2. Xác minh email
curl -X POST http://localhost:8000/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{"token": "<token-from-email>"}'

# 3. Đăng nhập (lưu cookies)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123"
  }'

# 4. Gia hạn token (sử dụng cookies)
curl -X POST http://localhost:8000/auth/refresh \
  -b cookies.txt

# 5. Quên mật khẩu
curl -X POST http://localhost:8000/auth/password-reset \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# 6. Confirm reset password
curl -X POST http://localhost:8000/auth/confirm-password-reset \
  -H "Content-Type: application/json" \
  -d '{
    "token": "<token-from-email>",
    "new_password": "NewSecurePassword123"
  }'

# 7. Đăng xuất (sử dụng cookies)
curl -X POST http://localhost:8000/auth/logout \
  -b cookies.txt
```

---

## 🔌 Tích Hợp Frontend

### Configuration

```javascript
// config.ts
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || "http://localhost:8000",
  ENDPOINTS: {
    REGISTER: "/auth/register",
    VERIFY_EMAIL: "/auth/verify-email",
    LOGIN: "/auth/login",
    REFRESH: "/auth/refresh",
    LOGOUT: "/auth/logout",
    PASSWORD_RESET: "/auth/password-reset",
    CONFIRM_PASSWORD_RESET: "/auth/confirm-password-reset",
  },
};
```

### Auth Service Pattern

```javascript
// authService.ts
class AuthService {
  // Lưu access token
  private accessToken: string | null = null;

  async register(email: string, password: string) {
    const res = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.REGISTER}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return res.json();
  }

  async verifyEmail(token: string) {
    const res = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.VERIFY_EMAIL}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ token })
    });
    return res.json();
  }

  async login(email: string, password: string) {
    const res = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.LOGIN}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    this.accessToken = data.access_token;
    return data;
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  async refreshToken() {
    const res = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.REFRESH}`, {
      method: 'POST',
      credentials: 'include'
    });
    const data = await res.json();
    this.accessToken = data.access_token;
    return data;
  }

  async logout() {
    await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.LOGOUT}`, {
      method: 'POST',
      credentials: 'include'
    });
    this.accessToken = null;
  }

  async requestPasswordReset(email: string) {
    const res = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.PASSWORD_RESET}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    return res.json();
  }

  async confirmPasswordReset(token: string, newPassword: string) {
    const res = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CONFIRM_PASSWORD_RESET}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, new_password: newPassword })
    });
    return res.json();
  }
}
```

---

## ⚙️ Cấu Hình Môi Trường

**`.env` (Backend)**

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/spa_crm

# JWT
SECRET_KEY=your-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
REFRESH_TOKEN_COOKIE_NAME=refresh_token

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@spa-crm.local
MAIL_STARTTLS=true
MAIL_SSL_TLS=false

# Token Expiry
VERIFICATION_TOKEN_EXPIRE_HOURS=24
RESET_TOKEN_EXPIRE_HOURS=1

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

---

## 🚀 Khởi Động

### 1. Cài Dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu Hình Database

```bash
# Chạy migration
alembic upgrade head
```

### 3. Cấu Hình Email

- Tạo App Password (nếu dùng Gmail)
- Cập nhật `.env` với SMTP settings

### 4. Khởi Động Server

```bash
# Development
uvicorn src.main:app --reload

# Production
gunicorn -w 4 -b 0.0.0.0:8000 src.main:app
```

### 5. Truy Cập API Docs

```
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
```

---

## 📝 Lưu Ý

- ✅ Module auth không phụ thuộc vào các module khác (customers, services, appointments)
- ✅ RBAC (Role-Based Access Control) có thể triển khai sau bằng `require_roles` dependency
- ✅ Email verification có thể tùy chọn (có thể bỏ qua nếu cần)
- ✅ Refresh token có thể lưu Redis thay vì DB để tăng hiệu năng
- ⚠️ HTTPS bắt buộc trong production (secure=true cho cookie)
- ⚠️ Rate limiting nên thêm để chống brute force

---

## 🔗 Tham Khảo

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Tokens](https://tools.ietf.org/html/rfc7519)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
