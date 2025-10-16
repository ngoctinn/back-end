# 📚 Tài Liệu Dự Án - Index

Danh mục tài liệu cho dự án Spa Online CRM Backend.

## 🎯 Bắt Đầu Nhanh

- 📖 **[README.md](../README.md)** - Project overview & khởi động
- 🚀 **[AUTH_QUICK_START.md](./AUTH_QUICK_START.md)** - 5 phút intro auth module

## 📚 Tài Liệu Chi Tiết

### 🔐 Authentication & Authorization

| File                                                                     | Mục Đích                      | Cho Ai                 |
| ------------------------------------------------------------------------ | ----------------------------- | ---------------------- |
| **[AUTH_API_GUIDE.md](./AUTH_API_GUIDE.md)**                             | Chi tiết API, flows, security | Developers, Architects |
| **[AUTH_QUICK_START.md](./AUTH_QUICK_START.md)**                         | Khởi động nhanh, ví dụ        | New developers         |
| **[IMPLEMENTATION_EMAIL_FEATURE.md](./IMPLEMENTATION_EMAIL_FEATURE.md)** | Email feature triển khai      | Backend devs           |

### 🔧 Database & Migrations

| File                                                         | Mục Đích               |
| ------------------------------------------------------------ | ---------------------- |
| **[ALEMBIC_QUICK_START.md](./ALEMBIC_QUICK_START.md)**       | Migrations quick start |
| **[ALEMBIC_CONFIG.md](./ALEMBIC_CONFIG.md)**                 | Alembic configuration  |
| **[ALEMBIC_SETUP_COMPLETE.md](./ALEMBIC_SETUP_COMPLETE.md)** | Setup documentation    |

### 📋 Kế Hoạch & Phân Tích

| File                                                 | Nội Dung               |
| ---------------------------------------------------- | ---------------------- |
| **[features/0001_PLAN.md](./features/0001_PLAN.md)** | Plan: Xác thực & Phiên |
| **[features/0002_PLAN.md](./features/0002_PLAN.md)** | Plan: Email features   |

### 📦 Sản Phẩm & Kinh Doanh

| File                                       | Nội Dung          |
| ------------------------------------------ | ----------------- |
| **[PRODUCT_BRIEF.md](./PRODUCT_BRIEF.md)** | Product brief     |
| **[feat/auth.md](./feat/auth.md)**         | Auth feature spec |

---

## 🗂️ Cấu Trúc Code

### Module Auth

```
src/modules/auth/
├── models.py       # 4 models (User, RefreshToken, VerificationToken, ResetPasswordToken)
├── schemas.py      # 9 schemas (Request/Response DTOs)
├── crud.py         # 18 functions (DB operations)
├── service.py      # 10+ functions (Business logic)
└── router.py       # 7 endpoints (API)
```

**Docstring Coverage:** 100%

### Email Module

```
src/core/email.py
├── send_verification_email()      # Gửi email verify
├── send_password_reset_email()    # Gửi email reset
├── send_email_async()             # Helper SMTP
└── HTML templates (2)             # Email templates
```

**Docstring Coverage:** 100%

---

## 🎓 Hướng Dẫn Học Tập

### 1️⃣ Bắt Đầu (15 phút)

1. Đọc: [README.md](../README.md) - Cấu trúc & setup
2. Đọc: [AUTH_QUICK_START.md](./AUTH_QUICK_START.md) - Overview
3. Chạy: `uvicorn src.main:app --reload`
4. Test: Swagger UI at http://localhost:8000/docs

### 2️⃣ Hiểu Chi Tiết (1 giờ)

1. Đọc: [AUTH_API_GUIDE.md](./AUTH_API_GUIDE.md)
   - Section "🔐 Luồng Xác Thực" - Hiểu luồng
   - Section "📚 Schemas / Models" - Dữ liệu
   - Section "🛡️ Bảo Mật" - Security
2. Explore: Code trong `src/modules/auth/`
3. Test: cURL examples

### 3️⃣ Tích Hợp Frontend (30 phút)

1. Đọc: [AUTH_API_GUIDE.md](./AUTH_API_GUIDE.md) → "🔌 Tích Hợp Frontend"
2. Copy: Code từ "Frontend (JavaScript/TypeScript)" example
3. Tuỳ chỉnh: Theo framework của bạn (React, Vue, etc.)

### 4️⃣ Extend Features (Tuỳ bộ)

1. Đọc: [AUTH_QUICK_START.md](./AUTH_QUICK_START.md) → "🔧 Cách Extend"
2. Implement: RBAC, OAuth, 2FA, etc.

---

## 🔍 Tìm Kiếm Nhanh

### "Tôi muốn biết..."

| Câu hỏi                    | File             | Section                 |
| -------------------------- | ---------------- | ----------------------- |
| Làm thế nào để đăng ký?    | AUTH_API_GUIDE   | 🔐 Luồng → 1. Đăng Ký   |
| Cấu trúc JWT token?        | AUTH_API_GUIDE   | 🔑 JWT Token Structure  |
| Làm sao tích hợp frontend? | AUTH_API_GUIDE   | 🔌 Tích Hợp Frontend    |
| Setup SMTP?                | AUTH_QUICK_START | Troubleshooting → Email |
| Làm sao add RBAC?          | AUTH_QUICK_START | 🔧 Cách Extend          |
| Database schema?           | AUTH_QUICK_START | 📊 Database Schema      |
| Unit tests?                | AUTH_QUICK_START | 🧪 Unit Tests           |
| Security checklist?        | AUTH_QUICK_START | 🔐 Security Checklist   |
| Common issues?             | AUTH_QUICK_START | 🐛 Common Issues        |

---

## 📊 Tài Liệu Stats

| Loại             | Số Lượng   | Chi Tiết              |
| ---------------- | ---------- | --------------------- |
| **Tệp tài liệu** | 11         | 3 guides + 8 existing |
| **Endpoints**    | 7          | Tất cả documented     |
| **Models**       | 4          | 100% docstrings       |
| **Schemas**      | 9          | Tất cả mô tả          |
| **Luồng chính**  | 5          | Chi tiết step-by-step |
| **Ví dụ code**   | 15+        | JS, cURL, patterns    |
| **Ngôn ngữ**     | Tiếng Việt | 100%                  |

---

## ✅ Quality Checklist

- [x] Đầy đủ (comprehensive)
- [x] Rõ ràng (clear)
- [x] Chính xác (accurate)
- [x] Dễ dùng (usable)
- [x] Cập nhật (up-to-date)
- [x] Tiếng Việt
- [x] Có ví dụ
- [x] Có troubleshooting
- [x] Có links cross-reference
- [x] Có checklist

---

## 🔗 External Links

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [JWT Specification](https://tools.ietf.org/html/rfc7519)
- [OWASP Security](https://owasp.org/www-project-top-ten/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)

---

## 📧 Thắc Mắc?

Xem section "Troubleshooting" hoặc "Common Issues" trong tài liệu tương ứng.

---

**Last Updated:** Oct 16, 2025  
**Status:** ✅ Complete  
**Coverage:** 100%
