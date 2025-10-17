# Spa Customer Care Platform - Backend

Tài liệu này mô tả cấu trúc và hướng dẫn khởi động backend dự án Spa Online CRM.

## 📁 Cấu Trúc Thư Mục

```
src/
├── main.py              # Khởi tạo ứng dụng FastAPI
├── core/                # Thành phần dùng chung
│   ├── config.py        # Cấu hình (Settings, Pydantic BaseSettings)
│   ├── db.py            # Database setup (SQLModel, Alembic)
│   ├── security.py      # Bảo mật (JWT, Password hashing)
│   ├── dependencies.py   # Dependencies chung (get_db, get_current_user)
│   ├── email.py         # Email sending (SMTP)
│   └── background_tasks.py # Background jobs (token cleanup)
├── modules/             # Domain-driven modules
│   ├── auth/            # Xác thực & Ủy quyền
│   │   ├── models.py    # User, RefreshToken, VerificationToken, etc.
│   │   ├── schemas.py   # Pydantic DTOs
│   │   ├── crud.py      # Database operations
│   │   ├── service.py   # Business logic
│   │   └── router.py    # API endpoints
│   ├── customers/       # Quản lý khách hàng (CRM)
│   ├── services/        # Quản lý dịch vụ & sản phẩm
│   ├── appointments/    # Quản lý lịch hẹn
│   └── staff/           # Quản lý nhân viên
└── tests/               # Unit tests

alembic/                # Database migrations
├── versions/
│   └── <migration-files>
└── env.py
```

## 🚀 Khởi Động Nhanh

### 1. Cài Đặt Dependencies

```bash
# Tạo virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Cài packages
pip install -r requirements.txt
```

### 2. Cấu Hình Môi Trường

Sao chép `.env.example` → `.env` và cập nhật:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/spa_crm

# JWT
SECRET_KEY=your-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@spa-crm.local
MAIL_STARTTLS=true
MAIL_SSL_TLS=false

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

### 3. Cấu Hình Database

```bash
# Chạy migrations
alembic upgrade head

# Xem database
# Dùng pgAdmin hoặc DBeaver để connect
```

### 4. Khởi Động Server

```bash
# Development mode (with auto-reload)
uvicorn src.main:app --reload

# Server sẽ chạy tại: http://localhost:8000
```

### 5. Truy Cập API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📚 Tài Liệu Module

### 🔐 Auth Module (Xác Thực)

📖 **[Chi tiết: `docs/DOCUMENTATION.md#-module-auth`](./docs/DOCUMENTATION.md)**

Module quản lý xác thực & ủy quyền với JWT + Email verification.

**Tính năng:**

- ✅ **Đăng ký** với xác minh email (OTP token, TTL 24h)
- ✅ **Đăng nhập** tạo JWT access token (TTL 15 min) + Refresh token (TTL 7 ngày)
- ✅ **Gia hạn token** từ refresh token
- ✅ **Đăng xuất** với revoke token
- ✅ **Quên mật khẩu** + Đặt lại mật khẩu qua email (OTP token, TTL 1h)
- ✅ **Gửi lại email xác minh** nếu không nhận được email đầu tiên

**Models:**

- `User` - Tài khoản người dùng (email, password_hash, roles, is_active)
- `RefreshToken` - Lưu refresh token (opaque, có thể revoke)
- `VerificationToken` - Token xác minh email (one-time use, TTL 24h)
- `ResetPasswordToken` - Token đặt lại mật khẩu (one-time use, TTL 1h)

**API Endpoints:**

```bash
POST   /auth/register                    # Đăng ký tài khoản
POST   /auth/verify-email                # Xác minh email
POST   /auth/resend-verification-email   # Gửi lại email xác minh
POST   /auth/login                       # Đăng nhập
POST   /auth/refresh                     # Gia hạn access token
POST   /auth/logout                      # Đăng xuất (revoke refresh token)
POST   /auth/password-reset              # Yêu cầu reset password
POST   /auth/confirm-password-reset      # Xác nhận & đặt mật khẩu mới
GET    /auth/me                          # Lấy thông tin user hiện tại
```

**Luồng sử dụng:**

1. Đăng ký → Email xác minh → Verify email → Sẵn sàng đăng nhập
2. Đăng nhập → Nhận JWT access token + HTTP-only refresh token cookie
3. Gọi API với header `Authorization: Bearer <access_token>`
4. Khi access token hết hạn → Gọi `/auth/refresh` để tạo token mới
5. Đăng xuất → Revoke refresh token, xóa cookie

### 📧 Email Feature

📖 **[Chi tiết: `docs/IMPLEMENTATION_EMAIL_FEATURE.md`](./IMPLEMENTATION_EMAIL_FEATURE.md)**

- Email xác minh đăng ký (24h TTL)
- Email reset password (1h TTL)
- Template HTML chuyên nghiệp
- SMTP integration

## 🔄 Quy Trình Phát Triển

### 1. Viết Kế Hoạch Kỹ Thuật

```bash
# Tạo file kế hoạch: docs/features/000N_PLAN.md
# Tuân thủ: .github/prompts/plan_feature.prompt.md
```

### 2. Triển Khai Feature

```bash
# Theo kế hoạch đã viết
# Code theo: .github/instructions/back-end.instructions.md
#            .github/instructions/clean-code.instructions.md
```

### 3. Viết Tài Liệu

```bash
# Cập nhật: docs/MODULE_NAME_API_GUIDE.md
# Tuân thủ: .github/prompts/write_docs.prompt.md
```

### 4. Test & Commit

```bash
# Chạy tests
pytest tests/

# Commit
git commit -m "Implement: feature description"
```

## 🧪 Testing

```bash
# Chạy tất cả tests
pytest

# Chạy tests với coverage
pytest --cov=src tests/

# Chạy test file cụ thể
pytest tests/test_auth.py
```

## 🔐 Bảo Mật

### Checklist Production

- [ ] HTTPS enabled
- [ ] `secure=True` cho cookies
- [ ] CORS cấu hình chặt chẽ
- [ ] Rate limiting (chống brute force)
- [ ] Input validation & sanitization
- [ ] SQL injection protection (SQLModel/SQLAlchemy)
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Environment variables bảo mật
- [ ] Logging không lộ sensitive data

## 🐛 Troubleshooting

### Database connection failed

```bash
# Check PostgreSQL running
psql -U user -d spa_crm

# Check DATABASE_URL in .env
# Format: postgresql://user:password@localhost:5432/spa_crm
```

### Email not sending

```bash
# Check SMTP settings in .env
# Gmail: Enable "Less secure app access" hoặc dùng App Password
# Hotmail: Dùng SMTP riêng
```

### Migration error

```bash
# Xem migration history
alembic history

# Rollback migration
alembic downgrade -1

# Tạo migration mới
alembic revision --autogenerate -m "description"
```

## 📚 Tham Khảo

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [OWASP Security Cheat Sheets](https://cheatsheetseries.owasp.org/)

## 👥 Contributors

- Backend Team: KLTN Project

## 📄 License

Proprietary - Spa Online CRM Project
