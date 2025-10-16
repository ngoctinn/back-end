# 📋 TÓM TẮT - QUẢN LÝ LUỒNG KHÁCH HÀNG (0003_PLAN)

## 🎯 Mục Đích

Triển khai 3 luồng khách hàng: Walk-in, Lazy Registration, Account Linking

## 📦 Module Tạo Mới

- `src/modules/customers/` (models, schemas, crud, service, router)
- `src/core/otp.py`

## 🔄 3 Luồng Chính

| Luồng                 | Kịch Bản                                        | Endpoint                        |
| --------------------- | ----------------------------------------------- | ------------------------------- |
| **Walk-in**           | Lễ tân tạo khách hàng (user_id=NULL)            | POST /customers/walk-in         |
| **Lazy Registration** | User đăng ký email+password → tạo stub customer | POST /auth/register             |
| **Account Linking**   | User cũ liên kết account bằng OTP               | POST /customers/link-account/\* |

## 🗄️ Bảng Chính

- **customer** (id, user_id, full_name, phone_number, ..., deleted_at)
  - Soft delete: `deleted_at IS NULL` trong all queries

## 🔐 Endpoints Chính

| Method | Endpoint                         | Mô Tả                        |
| ------ | -------------------------------- | ---------------------------- |
| POST   | /customers/walk-in               | Tạo khách hàng vãng lai      |
| POST   | /customers/profile               | Hoàn thiện hồ sơ             |
| GET    | /customers/{id}                  | Lấy thông tin                |
| DELETE | /customers/{id}                  | Xóa mềm                      |
| POST   | /customers/{id}/restore          | Khôi phục                    |
| GET    | /customers/me                    | Hồ sơ của user               |
| POST   | /customers/link-account/initiate | Bắt đầu liên kết (gửi OTP)   |
| POST   | /customers/link-account/verify   | Xác nhận liên kết (nhập OTP) |

## ⚙️ Công Nghệ & Yêu Cầu

- **Soft Delete**: Bắt buộc (không xóa cứng)
- **Transaction**: Luồng liên kết cần transaction + FOR UPDATE lock
- **OTP**: Redis cache, TTL 5 phút, retry limit 5 lần
- **Phone Normalize**: Normalize trước save/query
- **Authorization**: Role-based (receptionist, admin)

## 📝 Tệp Liên Quan

### Chi Tiết Kế Hoạch

- **0003_PLAN.md** - Kế hoạch đầy đủ (bao gồm logic từng bước)
- **0003_PLAN_CLEAN.md** - Phiên bản gọn (10 phần)

### Vấn Đề & Giải Pháp

- **0003_PLAN_ISSUES.md** - 10 vấn đề tiềm ẩn + cách fix

## ✅ Checklist Triển Khai

- [ ] Tạo Customer model + crud + service + router
- [ ] Sửa Auth service để tạo Customer khi register
- [ ] Implement OTP module
- [ ] Implement account linking logic (transaction + lock)
- [ ] Soft delete + restore logic
- [ ] Phone number normalize utility
- [ ] Unit tests (create, search, link, delete)
- [ ] Integration tests
- [ ] Migration Alembic
- [ ] Rate limiting + authorization checks

## 📚 Thứ Tự Ưu Tiên

1. **Tuần 1:** Models, CRUD, basic endpoints, OTP, linking logic
2. **Tuần 2:** Phone normalize, tests, rate limiting
3. **Tuần 3:** Performance tuning, indexes
