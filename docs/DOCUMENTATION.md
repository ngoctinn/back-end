# 📚 Tài Liệu Dự Án Spa Online CRM Backend

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
8. [🗄️ Database & Migrations](#-quản-lý-database--migrations)

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

---

## 🏗️ Kiến Trúc Dự Án

### Cấu trúc thư mục

```
back-end/
├── src/
│   ├── main.py                 # Khởi tạo FastAPI app
│   ├── core/                   # Cấu hình & utilities chung
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── security.py
│   │   ├── email.py
│   │   ├── dependencies.py
│   │   └── __init__.py
│   │
│   ├── modules/                # Domain modules
│   │   ├── auth/              # Xác thực & Ủy quyền
│   │   ├── customers/         # Quản lý khách hàng
│   │   ├── services/          # Quản lý dịch vụ
│   │   ├── appointments/      # Quản lý lịch hẹn
│   │   ├── staff/             # Quản lý nhân viên
│   │   └── __init__.py
│   │
│   └── tests/                  # Unit tests
│
├── alembic/                    # Database migrations
│   ├── env.py
│   └── versions/
│
├── docs/                       # Documentation
├── requirements.txt
├── alembic.ini
├── pyproject.toml
└── README.md
```

### Mô Hình Xử Lý Dữ Liệu

```
Client Request
    ↓
FastAPI Router (router.py)
    ↓
Dependency Injection (get_db, get_current_user)
    ↓
Service Layer (service.py) - Business logic
    ↓
CRUD Layer (crud.py) - Database operations
    ↓
SQLModel (models.py) ← → Database
    ↓
Response (schemas.py)
    ↓
Client Response
```

---

## 🔐 Module Auth

Xác thực & ủy quyền người dùng.

### 📊 Database Models

#### `User`

```
- id: Integer (PK)
- email: String (UK)
- password_hash: String
- full_name: String (NULL)
- is_active: Boolean (Default: True)
- roles: JSON (Default: [])
- created_at: DateTime
- updated_at: DateTime
- deleted_at: DateTime (soft delete)
```

#### `RefreshToken`

```
- id: Integer (PK)
- user_id: Integer (FK)
- token: String
- is_revoked: Boolean
- expires_at: DateTime
```

#### `VerificationToken` & `ResetPasswordToken`

```
- id: Integer (PK)
- user_id: Integer (FK)
- token: String
- expires_at: DateTime
```

### 🔄 Luồng Xác Thực

#### 1️⃣ Đăng Ký + Verify Email

**Bước 1: Đăng ký**

```
POST /auth/register
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

- Validate email (format, not exists)
- Hash password (bcrypt)
- Tạo User (is_active=False)
- Tạo VerificationToken (TTL 24h)
- Gửi email xác minh

**Bước 2: Xác minh email**

```
POST /auth/verify-email
{
  "token": "<token-from-email>"
}
```

- Tìm token trong DB
- Kiểm tra chưa hết hạn
- Update User: is_active=True
- Xóa token

---

#### 2️⃣ Đăng Nhập

```
POST /auth/login
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

- Tìm user theo email
- Verify password
- Kiểm tra is_active=True
- Tạo JWT access token (TTL 15 min)
- Tạo RefreshToken (TTL 7 ngày)
- Set HTTP-only cookie

---

#### 3️⃣ Gia Hạn Token

```
POST /auth/refresh
```

- Lấy refresh_token từ cookie
- Tạo JWT access token mới

---

#### 4️⃣ Đăng Xuất

```
POST /auth/logout
```

- Set RefreshToken.is_revoked=True
- Xóa cookie

---

#### 5️⃣ Quên Mật Khẩu

**Bước 1: Request reset**

```
POST /auth/password-reset
{
  "email": "user@example.com"
}
```

- Tìm user theo email
- Nếu tồn tại: Tạo ResetPasswordToken, gửi email
- Luôn return success (chống enumeration attack)

**Bước 2: Confirm reset**

```
POST /auth/confirm-password-reset
{
  "token": "<token-from-email>",
  "new_password": "NewPassword123"
}
```

- Kiểm tra token hợp lệ & chưa hết hạn
- Hash password mới
- Update User.password_hash
- Revoke tất cả RefreshTokens cũ
- Xóa token

### 📝 API Endpoints

| Method | Endpoint                       | Mô Tả            |
| :----- | :----------------------------- | :--------------- |
| POST   | `/auth/register`               | Đăng ký          |
| POST   | `/auth/verify-email`           | Verify email     |
| POST   | `/auth/login`                  | Đăng nhập        |
| POST   | `/auth/refresh`                | Gia hạn token    |
| POST   | `/auth/logout`                 | Đăng xuất        |
| POST   | `/auth/password-reset`         | Quên mật khẩu    |
| POST   | `/auth/confirm-password-reset` | Confirm reset pw |
| GET    | `/auth/me`                     | Lấy info user    |

---

## 👥 Module Customers

Quản lý hồ sơ khách hàng CRM.

**📖 [→ Xem hướng dẫn chi tiết](./CUSTOMERS_API_GUIDE.md)**

Tài liệu chi tiết bao gồm:

- ✅ Data model đầy đủ
- ✅ Tất cả API endpoints với ví dụ
- ✅ 5 luồng nghiệp vụ chính (Walk-in, Online, Linking, Delete, Restore)
- ✅ Xử lý lỗi và error codes
- ✅ Code examples (Python, cURL)
- ✅ Best practices

### 📊 Database Model: `Customer`

| Cột               | Loại     | Mô Tả                    |
| :---------------- | :------- | :----------------------- |
| id                | Integer  | PK                       |
| user_id           | Integer  | FK (NULL nếu walk-in)    |
| full_name         | String   | Họ tên khách hàng        |
| phone_number      | String   | Số điện thoại (UK)       |
| date_of_birth     | Date     | Ngày sinh                |
| gender            | String   | Giới tính (nam/nữ/khác)  |
| address           | String   | Địa chỉ                  |
| skin_type         | String   | Loại da (khô/dầu/...)    |
| health_conditions | Text     | Tình trạng sức khỏe      |
| notes             | Text     | Ghi chú CSKH             |
| is_active         | Boolean  | Hoạt động                |
| created_at        | DateTime | Thời gian tạo (UTC)      |
| updated_at        | DateTime | Thời gian cập nhật (UTC) |
| deleted_at        | DateTime | Soft delete marker       |

### 📝 API Endpoints

| Method | Endpoint             | Mô Tả                           |
| :----- | :------------------- | :------------------------------ |
| POST   | `/customers/walk-in` | Tạo khách hàng vãng lai         |
| POST   | `/customers/profile` | Hoàn thành hồ sơ (có tài khoản) |
| GET    | `/customers/{id}`    | Lấy chi tiết khách hàng         |
| PUT    | `/customers/{id}`    | Cập nhật thông tin              |
| DELETE | `/customers/{id}`    | Xóa mềm (soft delete)           |

### 🔄 Luồng Nghiệp Vụ

1. **Luồng 1:** Khách vãng lai → `POST /customers/walk-in`
2. **Luồng 2a:** Khách vãng lai → Đăng ký tài khoản
3. **Luồng 2b:** Hoàn thành hồ sơ → `POST /customers/profile`
4. **Luồng 3:** Liên kết khách hàng cũ với tài khoản mới (OTP verification)
5. **Luồng 4:** Xóa khách hàng → `DELETE /customers/{id}`
6. **Luồng 5:** Khôi phục khách hàng (admin)

---

## 💼 Module Services

Quản lý dịch vụ spa & sản phẩm.

### 📊 Database Model: `Service`

| Cột          | Loại     | Mô Tả              |
| :----------- | :------- | :----------------- |
| id           | Integer  | PK                 |
| name         | String   | Tên dịch vụ        |
| description  | Text     | Mô tả chi tiết     |
| price        | Decimal  | Giá dịch vụ        |
| duration_min | Integer  | Thời lượng (phút)  |
| is_active    | Boolean  | Dịch vụ hoạt động  |
| created_at   | DateTime | Thời gian tạo      |
| updated_at   | DateTime | Thời gian cập nhật |

### 📝 API Endpoints

| Method | Endpoint         | Mô Tả        |
| :----- | :--------------- | :----------- |
| POST   | `/services`      | Tạo dịch vụ  |
| GET    | `/services/{id}` | Lấy chi tiết |
| GET    | `/services`      | Danh sách    |
| PUT    | `/services/{id}` | Cập nhật     |
| DELETE | `/services/{id}` | Xóa          |

---

## 📅 Module Appointments

Quản lý lịch hẹn khách hàng - dịch vụ - nhân viên.

### 📊 Database Model: `Appointment`

| Cột              | Loại     | Mô Tả                                 |
| :--------------- | :------- | :------------------------------------ |
| id               | Integer  | PK                                    |
| customer_id      | Integer  | FK                                    |
| service_id       | Integer  | FK                                    |
| staff_id         | Integer  | FK                                    |
| scheduled_at     | DateTime | Thời gian bắt đầu                     |
| scheduled_end_at | DateTime | Thời gian kết thúc                    |
| status           | String   | pending/confirmed/cancelled/completed |
| notes            | Text     | Ghi chú                               |
| created_at       | DateTime | Thời gian tạo                         |
| updated_at       | DateTime | Thời gian cập nhật                    |

### 📝 API Endpoints

| Method | Endpoint                         | Mô Tả                |
| :----- | :------------------------------- | :------------------- |
| POST   | `/appointments`                  | Đặt lịch hẹn         |
| GET    | `/appointments/{id}`             | Chi tiết lịch hẹn    |
| GET    | `/appointments`                  | Danh sách (của user) |
| GET    | `/appointments/staff/{staff_id}` | Lịch của nhân viên   |
| PUT    | `/appointments/{id}`             | Cập nhật lịch hẹn    |
| DELETE | `/appointments/{id}`             | Hủy lịch hẹn         |

---

## 👨‍💼 Module Staff

Quản lý nhân viên spa.

### 📊 Database Model: `Staff`

| Cột          | Loại     | Mô Tả                          |
| :----------- | :------- | :----------------------------- |
| id           | Integer  | PK                             |
| user_id      | Integer  | FK                             |
| full_name    | String   | Họ tên nhân viên               |
| phone_number | String   | Số điện thoại                  |
| email        | String   | Email                          |
| position     | String   | therapist/receptionist/manager |
| department   | String   | Phòng ban                      |
| is_active    | Boolean  | Nhân viên hoạt động            |
| created_at   | DateTime | Thời gian tạo                  |
| updated_at   | DateTime | Thời gian cập nhật             |

### 📝 API Endpoints

| Method | Endpoint      | Mô Tả          |
| :----- | :------------ | :------------- |
| POST   | `/staff`      | Thêm nhân viên |
| GET    | `/staff/{id}` | Chi tiết       |
| GET    | `/staff`      | Danh sách      |
| PUT    | `/staff/{id}` | Cập nhật       |
| DELETE | `/staff/{id}` | Xóa            |

---

## 🗄️ Quản Lý Database & Migrations

Sử dụng **Alembic** để quản lý schema database.

### Các Lệnh Cơ Bản

```bash
# Xem trạng thái hiện tại
alembic current

# Xem lịch sử migrations
alembic history

# Tạo migration tự động
alembic revision --autogenerate -m "Describe your change"

# Áp dụng tất cả migrations pending
alembic upgrade head

# Quay lại 1 version
alembic downgrade -1

# Quay lại version cụ thể
alembic downgrade <revision-id>
```

### Quy Trình Thêm Model Mới

1. Tạo model trong `src/modules/<domain>/models.py`

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

## 📚 Tài Liệu Liên Quan

- **[README.md](../README.md)** - Project overview
- **[PRODUCT_BRIEF.md](./PRODUCT_BRIEF.md)** - Business specification
- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - Implementation progress
- **[requirements.txt](../requirements.txt)** - Python dependencies

---

## 🎓 Next Steps

1. **Bắt đầu development:**

   - Follow các bước trong [🎯 Bắt Đầu Nhanh](#-bắt-đầu-nhanh)
   - Kiểm tra Swagger docs: `http://localhost:8000/docs`

2. **Hiểu kiến trúc:**

   - Đọc [🏗️ Kiến Trúc Dự Án](#-kiến-trúc-dự-án)
   - Khám phá code trong `src/modules/`

3. **Implement features:**

   - Chọn module cần làm
   - Follow pattern: models → schemas → crud → service → router
   - Thêm unit tests

4. **Deploy:**
   - Xem [README.md](../README.md) để biết deployment guide
   - Setup production environment

---

**Phiên bản tài liệu:** 1.0 | Cập nhật: October 2025
