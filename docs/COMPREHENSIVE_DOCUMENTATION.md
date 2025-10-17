# 📚 Tài Liệu Toàn Diện - Spa Online CRM Backend

**Phiên bản:** 1.0 | **Ngôn ngữ:** Tiếng Việt | **Cập nhật:** Oct 2025

---

## 📑 Mục Lục

1. [🎯 Bắt Đầu Nhanh](#-bắt-đầu-nhanh)
2. [🏗️ Kiến Trúc Dự Án](#-kiến-trúc-dự-án)
3. [🔐 Module Auth](#-module-auth)
4. [👥 Module Customers](#-module-customers)
5. [💼 Module Services](#-module-services)
6. [📅 Module Appointments](#-module-appointments)
7. [👨‍💼 Module Staff](#-module-staff)
8. [🗄️ Quản Lý Database & Migrations](#-quản-lý-database--migrations)
9. [🧪 Testing](#-testing)
10. [📋 Troubleshooting & FAQ](#-troubleshooting--faq)
11. [🔒 Security Checklist](#-security-checklist)

---

## 🎯 Bắt Đầu Nhanh

### Yêu cầu hệ thống

- **Python:** 3.13+
- **PostgreSQL:** 12+
- **OS:** Windows, macOS, Linux

### Cài đặt (5 phút)

```bash
# 1. Clone repository
git clone <repo-url>
cd back-end

# 2. Tạo virtual environment
python -m venv .venv

# 3. Activate environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 4. Cài đặt dependencies
pip install -r requirements.txt

# 5. Cấu hình environment
cp .env.example .env
# Chỉnh sửa .env với thông tin database, email, JWT secret

# 6. Chạy migrations
alembic upgrade head

# 7. Khởi động server
uvicorn src.main:app --reload

# Server chạy tại: http://localhost:8000
# Swagger API docs: http://localhost:8000/docs
```

### Test nhanh

```bash
# Đăng ký
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Pass123456"}'

# Đăng nhập
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Pass123456"}'
```

---

## 🏗️ Kiến Trúc Dự Án

### Cấu trúc thư mục

```
back-end/
├── src/
│   ├── main.py                 # Khởi tạo FastAPI app
│   ├── __init__.py
│   │
│   ├── core/                   # Cấu hình & utilities chung
│   │   ├── config.py          # Cấu hình Pydantic Settings
│   │   ├── db.py              # Database connection
│   │   ├── security.py        # JWT & password hashing
│   │   ├── email.py           # Email service
│   │   ├── otp.py             # OTP utilities
│   │   ├── dependencies.py    # Dependency injection (get_db, get_current_user)
│   │   ├── background_tasks.py # Async tasks
│   │   ├── utils.py           # Helper functions
│   │   └── __init__.py
│   │
│   ├── modules/                # Domain modules (Business logic)
│   │   ├── auth/              # 🔐 Xác thực & Ủy quyền
│   │   │   ├── models.py      # Database models (User, RefreshToken, ...)
│   │   │   ├── schemas.py     # Pydantic DTOs (Request/Response)
│   │   │   ├── crud.py        # Data access operations
│   │   │   ├── service.py     # Business logic
│   │   │   ├── router.py      # API endpoints
│   │   │   ├── auth_service.py
│   │   │   ├── token_service.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── customers/          # 👥 Quản lý khách hàng (CRM)
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── crud.py
│   │   │   ├── service.py
│   │   │   ├── router.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── services/           # 💼 Quản lý dịch vụ & sản phẩm
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── crud.py
│   │   │   ├── service.py
│   │   │   ├── router.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── appointments/       # 📅 Quản lý lịch hẹn
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── crud.py
│   │   │   ├── service.py
│   │   │   ├── router.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── staff/              # 👨‍💼 Quản lý nhân viên
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── crud.py
│   │   │   ├── service.py
│   │   │   ├── router.py
│   │   │   └── __init__.py
│   │   │
│   │   └── __init__.py
│   │
│   └── tests/                  # Unit tests
│       ├── test_customers.py
│       ├── test_auth.py
│       └── __init__.py
│
├── alembic/                    # Database migrations
│   ├── env.py
│   ├── versions/
│   │   ├── 20251016_*.py
│   │   └── ...
│   └── script.py.mako
│
├── .env.example                # Environment template
├── .env                        # Environment config (local)
├── requirements.txt            # Python dependencies
├── alembic.ini                 # Alembic config
├── pyproject.toml              # Project metadata
├── README.md                   # Project overview
└── docs/                       # Documentation
    ├── COMPREHENSIVE_DOCUMENTATION.md (📍 You are here)
    ├── PRODUCT_BRIEF.md
    ├── IMPLEMENTATION_SUMMARY.md
    └── ...
```

### Luồng dữ liệu

```
Client Request
    ↓
FastAPI Router (route.py)
    ↓
Dependency Injection (get_db, get_current_user)
    ↓
Service Layer (service.py) - Business logic
    ↓
CRUD Layer (crud.py) - Database operations
    ↓
SQLModel (models.py) + Database
    ↓
Response → Pydantic Schema (schemas.py)
    ↓
Client Response
```

---

## 🔐 Module Auth

Xác thực & ủy quyền người dùng. Hỗ trợ JWT tokens, email verification, password reset.

### 📊 Database Models

#### `User`

Bảng người dùng chính.

| Cột             | Loại     | Constraint   | Mô Tả                               |
| :-------------- | :------- | :----------- | :---------------------------------- |
| `id`            | Integer  | PK           | User ID                             |
| `email`         | String   | UK, NOT NULL | Email (unique)                      |
| `password_hash` | String   | NOT NULL     | Mật khẩu hash (bcrypt)              |
| `full_name`     | String   | NULL         | Họ tên đầy đủ                       |
| `phone_number`  | String   | NULL         | Số điện thoại                       |
| `is_active`     | Boolean  | Default:True | Tài khoản kích hoạt                 |
| `roles`         | JSON     | Default:[]   | Danh sách vai trò ["admin", "user"] |
| `created_at`    | DateTime | Default:now  | Thời gian tạo                       |
| `updated_at`    | DateTime | Default:now  | Thời gian cập nhật                  |
| `deleted_at`    | DateTime | NULL         | Soft delete                         |

#### `RefreshToken`

Lưu trữ refresh tokens để gia hạn access tokens.

| Cột          | Loại     | Mô Tả                      |
| :----------- | :------- | :------------------------- |
| `id`         | Integer  | PK                         |
| `user_id`    | Integer  | FK → User.id               |
| `token`      | String   | Opaque token (UUID)        |
| `is_revoked` | Boolean  | Token bị revoke            |
| `expires_at` | DateTime | Thời gian hết hạn (7 ngày) |
| `created_at` | DateTime | Thời gian tạo              |

#### `VerificationToken` & `ResetPasswordToken`

Tương tự, lưu verification emails & password reset.

### 🔄 Luồng Xác Thực

#### 1️⃣ Đăng Ký + Verify Email

**POST /auth/register**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

Quy trình:

1. Validate email (format, not exists)
2. Hash password → bcrypt
3. Tạo User (is_active=False)
4. Tạo VerificationToken (TTL 24h)
5. Gửi email xác minh → link: `/auth/verify-email?token=<token>`
6. Return: `{ "message": "Đăng ký thành công", "email": "..." }`

**POST /auth/verify-email**

```json
{
  "token": "<token-from-email>"
}
```

Quy trình:

1. Tìm token trong DB
2. Kiểm tra chưa hết hạn (expires_at > now)
3. Update User: is_active=True
4. Xóa VerificationToken
5. Return: `{ "message": "Email xác minh thành công" }`

---

#### 2️⃣ Đăng Nhập

**POST /auth/login**

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Headers: `Set-Cookie: refresh_token=<opaque>; HttpOnly; SameSite=Lax; Max-Age=604800`

Quy trình:

1. Tìm user theo email
2. Verify password (bcrypt)
3. Kiểm tra is_active=True
4. Tạo JWT access token (TTL 15 min): `{ sub: user_id, roles: [...] }`
5. Tạo RefreshToken (TTL 7 ngày)
6. Set HTTP-only cookie
7. Return access_token

---

#### 3️⃣ Gia Hạn Token

**POST /auth/refresh**

Cookie: `refresh_token=<opaque>`

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Quy trình:

1. Lấy refresh_token từ cookie
2. Tìm RefreshToken trong DB
3. Kiểm tra is_revoked=False, expires_at > now
4. Tạo JWT access token mới
5. Return access_token

---

#### 4️⃣ Đăng Xuất

**POST /auth/logout**

Cookie: `refresh_token=<opaque>`

Quy trình:

1. Lấy refresh_token từ cookie
2. Set RefreshToken.is_revoked=True
3. Xóa cookie
4. Return: `{ "message": "Đã đăng xuất" }`

---

#### 5️⃣ Quên Mật Khẩu

**POST /auth/password-reset**

```json
{
  "email": "user@example.com"
}
```

Response: `{ "message": "Nếu email tồn tại, hướng dẫn đã được gửi" }` (luôn)

Quy trình:

1. Tìm user theo email
2. Nếu tồn tại:
   - Tạo ResetPasswordToken (TTL 1h)
   - Gửi email: link `/auth/reset-password?token=<token>`
3. Nếu không tồn tại: **Delay 1-2 giây** (chống enumeration)
4. Luôn return success

**POST /auth/confirm-password-reset**

```json
{
  "token": "<token-from-email>",
  "new_password": "NewPassword123"
}
```

Quy trình:

1. Tìm ResetPasswordToken
2. Kiểm tra expires_at > now
3. Validate new_password (min 8 ký tự)
4. Hash password mới
5. Update User.password_hash
6. **Revoke tất cả RefreshTokens cũ** (force re-login)
7. Xóa ResetPasswordToken
8. Return: `{ "message": "Mật khẩu đã được đặt lại" }`

### 🛡️ JWT Token Structure

```
Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "sub": 123,              // user_id
  "roles": ["user", "admin"],
  "iat": 1634567890,       // issued at
  "exp": 1634568490        // expires at (15 min)
}

Signature: HMAC-SHA256(base64(header) + "." + base64(payload), SECRET_KEY)
```

### 📝 API Endpoints

| Method | Endpoint                       | Auth | Mô Tả              |
| :----- | :----------------------------- | :--- | :----------------- |
| POST   | `/auth/register`               | -    | Đăng ký            |
| POST   | `/auth/verify-email`           | -    | Verify email       |
| POST   | `/auth/login`                  | -    | Đăng nhập          |
| POST   | `/auth/refresh`                | -    | Gia hạn token      |
| POST   | `/auth/logout`                 | ✓    | Đăng xuất          |
| POST   | `/auth/password-reset`         | -    | Quên mật khẩu      |
| POST   | `/auth/confirm-password-reset` | -    | Confirm reset pw   |
| GET    | `/auth/me`                     | ✓    | Lấy thông tin user |

---

## 👥 Module Customers

Quản lý hồ sơ khách hàng CRM.

### 📊 Database Model: `Customer`

| Cột                 | Loại     | Constraint   | Mô Tả                     |
| :------------------ | :------- | :----------- | :------------------------ |
| `id`                | Integer  | PK           | Customer ID               |
| `user_id`           | Integer  | FK, NULL     | Link đến User account     |
| `full_name`         | String   | NOT NULL     | Họ tên khách hàng         |
| `phone_number`      | String   | UK           | Số điện thoại             |
| `email`             | String   | NULL         | Email                     |
| `date_of_birth`     | Date     | NULL         | Ngày sinh                 |
| `gender`            | String   | NULL         | Giới tính (M/F/Other)     |
| `address`           | String   | NULL         | Địa chỉ                   |
| `notes`             | Text     | NULL         | Ghi chú CSKH              |
| `skin_type`         | String   | NULL         | Loại da (Normal/Dry/Oily) |
| `health_conditions` | Text     | NULL         | Tình trạng sức khỏe       |
| `is_active`         | Boolean  | Default:True | Khách hàng hoạt động      |
| `created_at`        | DateTime | Default:now  | Thời gian tạo             |
| `updated_at`        | DateTime | Default:now  | Thời gian cập nhật        |
| `deleted_at`        | DateTime | NULL         | Soft delete               |

### 📝 API Endpoints

| Method | Endpoint            | Auth | Mô Tả                  |
| :----- | :------------------ | :--- | :--------------------- |
| POST   | `/customers`        | ✓    | Tạo khách hàng mới     |
| GET    | `/customers/{id}`   | ✓    | Lấy chi tiết           |
| GET    | `/customers`        | ✓    | Danh sách (phân trang) |
| PUT    | `/customers/{id}`   | ✓    | Cập nhật               |
| DELETE | `/customers/{id}`   | ✓    | Xóa (soft delete)      |
| GET    | `/customers/search` | ✓    | Tìm kiếm               |

---

## 💼 Module Services

Quản lý dịch vụ spa & sản phẩm.

### 📊 Database Model: `Service`

| Cột            | Loại     | Constraint   | Mô Tả              |
| :------------- | :------- | :----------- | :----------------- |
| `id`           | Integer  | PK           | Service ID         |
| `name`         | String   | NOT NULL     | Tên dịch vụ        |
| `description`  | Text     | NULL         | Mô tả chi tiết     |
| `price`        | Decimal  | NOT NULL     | Giá dịch vụ        |
| `duration_min` | Integer  | NOT NULL     | Thời lượng (phút)  |
| `is_active`    | Boolean  | Default:True | Dịch vụ hoạt động  |
| `created_at`   | DateTime | Default:now  | Thời gian tạo      |
| `updated_at`   | DateTime | Default:now  | Thời gian cập nhật |

### 📝 API Endpoints

| Method | Endpoint         | Auth | Mô Tả        |
| :----- | :--------------- | :--- | :----------- |
| POST   | `/services`      | ✓    | Tạo dịch vụ  |
| GET    | `/services/{id}` | -    | Lấy chi tiết |
| GET    | `/services`      | -    | Danh sách    |
| PUT    | `/services/{id}` | ✓    | Cập nhật     |
| DELETE | `/services/{id}` | ✓    | Xóa          |

---

## 📅 Module Appointments

Quản lý lịch hẹn khách hàng - dịch vụ - nhân viên.

### 📊 Database Model: `Appointment`

| Cột                | Loại     | Constraint      | Mô Tả                                 |
| :----------------- | :------- | :-------------- | :------------------------------------ |
| `id`               | Integer  | PK              | Appointment ID                        |
| `customer_id`      | Integer  | FK              | Khách hàng                            |
| `service_id`       | Integer  | FK              | Dịch vụ                               |
| `staff_id`         | Integer  | FK              | Nhân viên thực hiện                   |
| `scheduled_at`     | DateTime | NOT NULL        | Thời gian bắt đầu                     |
| `scheduled_end_at` | DateTime | NOT NULL        | Thời gian kết thúc                    |
| `status`           | String   | Default:pending | pending/confirmed/cancelled/completed |
| `notes`            | Text     | NULL            | Ghi chú                               |
| `created_at`       | DateTime | Default:now     | Thời gian tạo                         |
| `updated_at`       | DateTime | Default:now     | Thời gian cập nhật                    |

### 📝 API Endpoints

| Method | Endpoint                         | Auth | Mô Tả                |
| :----- | :------------------------------- | :--- | :------------------- |
| POST   | `/appointments`                  | ✓    | Đặt lịch hẹn         |
| GET    | `/appointments/{id}`             | ✓    | Chi tiết lịch hẹn    |
| GET    | `/appointments`                  | ✓    | Danh sách (của user) |
| GET    | `/appointments/staff/{staff_id}` | ✓    | Lịch của nhân viên   |
| PUT    | `/appointments/{id}`             | ✓    | Cập nhật lịch hẹn    |
| DELETE | `/appointments/{id}`             | ✓    | Hủy lịch hẹn         |

---

## 👨‍💼 Module Staff

Quản lý nhân viên spa.

### 📊 Database Model: `Staff`

| Cột            | Loại     | Constraint   | Mô Tả                                   |
| :------------- | :------- | :----------- | :-------------------------------------- |
| `id`           | Integer  | PK           | Staff ID                                |
| `user_id`      | Integer  | FK           | Link User account                       |
| `full_name`    | String   | NOT NULL     | Họ tên nhân viên                        |
| `phone_number` | String   | NULL         | Số điện thoại                           |
| `email`        | String   | NULL         | Email                                   |
| `position`     | String   | NOT NULL     | Vị trí (therapist/receptionist/manager) |
| `department`   | String   | NULL         | Phòng ban                               |
| `is_active`    | Boolean  | Default:True | Nhân viên hoạt động                     |
| `created_at`   | DateTime | Default:now  | Thời gian tạo                           |
| `updated_at`   | DateTime | Default:now  | Thời gian cập nhật                      |

### 📝 API Endpoints

| Method | Endpoint      | Auth | Mô Tả          |
| :----- | :------------ | :--- | :------------- |
| POST   | `/staff`      | ✓    | Thêm nhân viên |
| GET    | `/staff/{id}` | ✓    | Chi tiết       |
| GET    | `/staff`      | ✓    | Danh sách      |
| PUT    | `/staff/{id}` | ✓    | Cập nhật       |
| DELETE | `/staff/{id}` | ✓    | Xóa            |

---

## 🗄️ Quản Lý Database & Migrations

Sử dụng **Alembic** để quản lý schema database.

### Cơ Bản

```bash
# Xem trạng thái hiện tại
alembic current

# Xem lịch sử migrations
alembic history

# Tạo migration tự động (khi thay đổi models)
alembic revision --autogenerate -m "Describe your change"

# Áp dụng tất cả migrations pending
alembic upgrade head

# Quay lại 1 version
alembic downgrade -1

# Quay lại version cụ thể
alembic downgrade <revision-id>
```

### Quy Trình Thêm Model Mới

1. Tạo model mới trong `src/modules/<domain>/models.py`

   ```python
   class NewModel(SQLModel, table=True):
       __tablename__ = "new_models"
       id: int | None = Field(default=None, primary_key=True)
       # ... fields
   ```

2. Import model trong `src/core/db.py` (để Alembic phát hiện)

3. Tạo migration

   ```bash
   alembic revision --autogenerate -m "create new_models table"
   ```

4. Review migration file trong `alembic/versions/`

5. Áp dụng migration
   ```bash
   alembic upgrade head
   ```

### Cấu Hình Environment

Tạo file `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/spa_crm

# JWT
SECRET_KEY=your-super-secret-key-min-32-chars-xxxxxxxx
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=noreply@spacrm.com

# Frontend
FRONTEND_URL=http://localhost:3000
VERIFICATION_URL_TEMPLATE=http://localhost:3000/auth/verify-email?token={token}
RESET_PASSWORD_URL_TEMPLATE=http://localhost:3000/auth/reset-password?token={token}

# Environment
ENVIRONMENT=development
DEBUG=true
```

---

## 🧪 Testing

### Unit Tests

```bash
# Chạy tất cả tests
pytest

# Chạy tests từ file cụ thể
pytest tests/test_auth.py

# Chạy test cụ thể
pytest tests/test_auth.py::test_register

# Chạy với coverage report
pytest --cov=src tests/
```

### Test Template (pytest)

```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestAuthRegister:
    def test_register_success(self):
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123"
            }
        )
        assert response.status_code == 201
        assert response.json()["email"] == "test@example.com"

    def test_register_duplicate_email(self):
        # First registration
        client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123"
            }
        )
        # Duplicate attempt
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123"
            }
        )
        assert response.status_code == 400
        assert "Email already exists" in response.json()["detail"]
```

---

## 📋 Troubleshooting & FAQ

### 🐛 Vấn đề Phổ Biến

#### 1. **Email không được gửi**

**Triệu chứng:** Đăng ký thành công nhưng không nhận email

**Giải pháp:**

- Kiểm tra `.env`: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`
- Nếu dùng Gmail: [Bật "Less secure app"](https://myaccount.google.com/app-passwords) hoặc dùng App Password
- Kiểm tra logs: `tail -f logs/app.log | grep email`
- Test SMTP:
  ```bash
  python -c "
  import smtplib
  sm = smtplib.SMTP('smtp.gmail.com', 587)
  sm.starttls()
  sm.login('your-email@gmail.com', 'your-password')
  print('SMTP OK')
  "
  ```

#### 2. **JWT token expired**

**Triệu chứng:** `401 Unauthorized - Token expired`

**Giải pháp:**

- Sử dụng refresh endpoint: `POST /auth/refresh`
- Kiểm tra `ACCESS_TOKEN_EXPIRE_MINUTES` trong `.env` (default 15)
- Kiểm tra đồng hồ server

#### 3. **Password reset token không hợp lệ**

**Triệu chứng:** `400 Bad Request - Invalid or expired token`

**Giải pháp:**

- Token có TTL 1 giờ → copy & paste token nhanh
- Kiểm tra token không có ký tự bị mã hóa
- Restart server (nếu thay đổi `SECRET_KEY`)

#### 4. **Database connection failed**

**Triệu chứng:** `sqlalchemy.exc.OperationalError`

**Giải pháp:**

- Kiểm tra PostgreSQL đang chạy: `psql -l`
- Kiểm tra `DATABASE_URL` trong `.env`
- Test connection: `psql postgresql://user:pass@localhost:5432/spa_crm`

#### 5. **CORS Error**

**Triệu chứng:** Frontend gặp CORS error

**Giải pháp:**

- Thêm vào `src/main.py`:

  ```python
  from fastapi.middleware.cors import CORSMiddleware

  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:3000"],  # Frontend URL
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

### ❓ FAQ

**Q: Làm cách nào để thêm role/permission cho user?**

A:

```python
# User model có field: roles: list[str] = Field(default=[])
# Trong service:
user.roles = ["admin", "staff"]
session.add(user)
session.commit()

# Kiểm tra trong router:
from src.core.dependencies import get_current_user

@router.get("/admin-only")
async def admin_endpoint(user = Depends(get_current_user)):
    if "admin" not in user.roles:
        raise HTTPException(status_code=403, detail="Not allowed")
    return {"message": "Admin access"}
```

**Q: Cách implement 2FA?**

A: Thêm OTP table & logic:

1. Tạo model: `class OTP(SQLModel, table=True): ...`
2. Trong service: Tạo OTP 6 ký tự, gửi SMS
3. Endpoint `/auth/verify-otp?code=123456`

**Q: Database backup?**

A:

```bash
# Backup
pg_dump -U user -d spa_crm > backup.sql

# Restore
psql -U user -d spa_crm < backup.sql
```

---

## 🔒 Security Checklist

Trước khi deploy production:

- [ ] **JWT Secret:** Đặt `SECRET_KEY` dài 32+ ký tự, random
- [ ] **Database:**
  - [ ] Change default password
  - [ ] Enable SSL/TLS connection
  - [ ] Backup regulary
- [ ] **HTTPS:** Sử dụng HTTPS (không HTTP)
- [ ] **CORS:** Giới hạn origins tới frontend domain chính xác
- [ ] **Rate Limiting:** Thêm rate limit để chống brute force

  ```python
  from slowapi import Limiter
  from slowapi.util import get_remote_address

  limiter = Limiter(key_func=get_remote_address)
  app.state.limiter = limiter

  @router.post("/auth/login")
  @limiter.limit("5/minute")  # Max 5 requests per minute
  async def login(...):
      ...
  ```

- [ ] **Input Validation:** Validate tất cả inputs (Pydantic tự validate)
- [ ] **SQL Injection:** Sử dụng SQLModel/SQLAlchemy (an toàn tự động)
- [ ] **CSRF Protection:** Thêm CSRF tokens nếu dùng forms
- [ ] **Logging:** Enable audit logs
  ```python
  import logging
  logger = logging.getLogger(__name__)
  logger.info(f"User {user_id} logged in from {request.client.host}")
  ```
- [ ] **Error Handling:** Không lộ stack traces
  ```python
  @app.exception_handler(Exception)
  async def generic_exception_handler(request, exc):
      return JSONResponse(
          status_code=500,
          content={"detail": "Internal server error"}
      )
  ```
- [ ] **Dependencies:** Check CVE mỗi tháng
  ```bash
  pip install safety
  safety check
  ```

---

## 📚 Tài Liệu Liên Quan

- **[README.md](../README.md)** - Project overview
- **[PRODUCT_BRIEF.md](./PRODUCT_BRIEF.md)** - Product specification
- **[requirements.txt](../requirements.txt)** - Python dependencies
- **[.env.example](../.env.example)** - Environment template

---

## 🎓 Next Steps

1. **Bắt đầu development:**

   - Đọc phần [🎯 Bắt Đầu Nhanh](#-bắt-đầu-nhanh)
   - Chạy server & kiểm tra Swagger docs

2. **Hiểu kiến trúc:**

   - Đọc [🏗️ Kiến Trúc Dự Án](#-kiến-trúc-dự-án)
   - Khám phá code trong `src/modules/`

3. **Implement features:**

   - Chọn module muốn làm (auth, customers, etc.)
   - Follow pattern: models → schemas → crud → service → router
   - Thêm unit tests

4. **Deploy:**
   - Tham khảo [🔒 Security Checklist](#-security-checklist)
   - Sử dụng Docker/Kubernetes
   - Monitor logs & metrics

---

**Cách sử dụng tài liệu này:**

- **Bắt đầu?** → Đọc [🎯 Bắt Đầu Nhanh](#-bắt-đầu-nhanh)
- **Cần chi tiết module?** → Mở section module (🔐 Auth, 👥 Customers, etc.)
- **Có vấn đề?** → Tham khảo [📋 Troubleshooting](#-troubleshooting--faq)
- **Deploy?** → Kiểm tra [🔒 Security Checklist](#-security-checklist)

**Phiên bản tài liệu:** 1.0 | Cập nhật: October 2025
