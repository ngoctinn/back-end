# KẾ HOẠCH KỸ THUẬT: QUẢN LÝ LUỒNG KHÁCH HÀNG (CUSTOMER JOURNEY)

## 1. Mô tả Ngữ cảnh

Triển khai hệ thống quản lý khách hàng toàn diện với 3 luồng chính: Khách hàng vãng lai (Walk-in), Đăng ký online nhanh gọn (Lazy Registration), và Liên kết tài khoản cho khách hàng cũ (Account Linking). Hệ thống phân tách rõ ràng giữa bảng User (xác thực) và bảng Customer (hồ sơ CRM), cho phép một khách hàng có thể tồn tại mà không cần tài khoản online.

---

## 2. Các Tệp và Hàm Liên quan

### Tạo mới:

- **`src/modules/customers/models.py`**

  - `Customer(SQLModel, table=True)` với fields: id, user_id, full_name, phone_number, date_of_birth, gender, address, notes, skin_type, health_conditions, is_active, created_at, updated_at, deleted_at

- **`src/modules/customers/schemas.py`**

  - `CustomerCreateRequest`, `CustomerUpdateRequest`, `CustomerLinkRequest`, `CustomerVerifyOTPRequest`, `CustomerResponse`, `CustomerListResponse`

- **`src/modules/customers/crud.py`**

  - `create_customer()`, `get_customer_by_id()`, `get_customer_by_user_id()`, `get_customer_by_phone_number()`, `get_customer_by_phone_and_no_user()`, `update_customer()`, `soft_delete_customer()`, `restore_customer()`, `find_customer_by_query()`, `link_customer_with_user()`, `unlink_customer_from_user()`

- **`src/modules/customers/service.py`**

  - `create_walk_in_customer()`, `create_online_customer_with_user()`, `complete_customer_profile()`, `initiate_account_linking()`, `verify_otp_and_link_account()`, `delete_customer()`, `restore_customer()`, `search_customers()`

- **`src/modules/customers/router.py`**

  - POST `/customers/walk-in`
  - POST `/customers/profile`
  - GET `/customers/{customer_id}`
  - PUT `/customers/{customer_id}`
  - DELETE `/customers/{customer_id}`
  - POST `/customers/{customer_id}/restore`
  - GET `/customers/search`
  - POST `/customers/link-account/initiate`
  - POST `/customers/link-account/verify`
  - GET `/customers/me`

- **`src/core/otp.py`**
  - `generate_otp()`, `send_otp_sms()`, `store_otp()`, `verify_otp()`, `clear_otp()`

### Sửa đổi:

- **`src/modules/auth/models.py`** - Customer back-reference (tuỳ chọn)
- **`src/modules/auth/schemas.py`** - RegisterRequest thêm phone_number, full_name
- **`src/modules/auth/service.py`** - register_user() gọi create_online_customer_with_user()
- **`src/modules/auth/router.py`** - POST /auth/register thêm fields
- **`src/main.py`** - Gắn customers_router

---

## 3. Luồng Chi Tiết (Step-by-Step)

### 3.1 Luồng 1: Khách Hàng Vãng Lai (Walk-in)

1. Lễ tân: POST `/customers/walk-in` với {full_name, phone_number}
2. Backend: Validate → create_customer(full_name, phone_number, user_id=NULL)
3. Lưu vào DB: Customer(full_name="...", phone_number="...", user_id=NULL, ...)
4. Response: {id, full_name, phone_number, user_id=null, ...}

### 3.2 Luồng 2a: Đăng Ký Online (Lazy Registration)

1. User: POST `/auth/register` với {email, password}
2. Backend (Transaction):
   - Tạo User(email, password_hash, is_active=False)
   - Gọi create_online_customer_with_user(user_id, None, None)
   - Tạo Customer(user_id=user_id, full_name=NULL, phone_number=NULL)
   - Tạo email verification token
   - Gửi email xác minh
3. Response: "Đăng ký thành công. Vui lòng xác minh email"

### 3.3 Luồng 2b: Hoàn Thiện Hồ Sơ Khi Đặt Lịch

1. User: POST `/customers/profile` với {full_name, phone_number} (JWT required)
2. Backend:
   - Lấy user_id từ JWT
   - Query get_customer_by_user_id(user_id)
   - Validate full_name, phone_number
   - update_customer(customer_id, {full_name, phone_number})
3. Response: {id, user_id, full_name, phone_number, ...}

### 3.4 Luồng 3a: Khách Hàng Cũ Đăng Ký Online

- Giống Luồng 2a hoàn toàn
- Kết quả: User mới + Customer "chờ" (stub) mới

### 3.5 Luồng 3b: Kích Hoạt Liên Kết (Account Linking)

1. User: GET `/customers/me` (JWT required)
2. Backend:
   - Query get_customer_by_user_id(user_id) lấy hồ sơ "chờ"
   - Kiểm tra: full_name IS NULL AND phone_number IS NULL
   - Nếu đúng: Frontend hiển thị "Bạn là khách hàng thân thiết? Liên kết ngay!"

### 3.6 Luồng 3c: Xác Minh & Gửi OTP

1. User: POST `/customers/link-account/initiate` với {phone_number} (JWT required)
2. Backend:
   - Validate phone_number format
   - Query get_customer_by_phone_and_no_user(phone_number) tìm hồ sơ cũ
   - Nếu tìm thấy: generate_otp() + send_otp_sms()
   - store_otp(phone_number, otp_code, 5 phút)
3. Response: "OTP đã được gửi đến 0912345678"

### 3.7 Luồng 3d: Hoàn Tất Hợp Nhất (Verify & Link)

1. User: POST `/customers/link-account/verify` với {phone_number, otp_code} (JWT required)
2. Backend:
   - verify_otp(phone_number, otp_code)
   - **Transaction:**
     - Lấy stub_customer = get_customer_by_user_id(user_id) (hồ sơ "chờ")
     - Lấy old_customer = get_customer_by_phone_and_no_user(phone_number) (hồ sơ cũ)
     - UPDATE old_customer: SET user_id = :user_id
     - Soft delete stub_customer: SET deleted_at = now()
   - clear_otp(phone_number)
3. Response: "Liên kết tài khoản thành công! {customer}"

### 3.8 Luồng 4: Xóa Mềm Khách Hàng (Soft Delete)

1. Lễ tân/Admin: DELETE `/customers/{customer_id}` (JWT required)
2. Backend:
   - Validate customer tồn tại (deleted_at IS NULL)
   - soft_delete_customer(customer_id): UPDATE customer SET deleted_at = now()
3. Response: {message: "Khách hàng đã bị xóa", can_restore: true}

### 3.9 Luồng 5: Khôi Phục Khách Hàng (Restore)

1. Admin: POST `/customers/{customer_id}/restore` (JWT required)
2. Backend:
   - Validate customer bị xoá (deleted_at IS NOT NULL)
   - restore_customer(customer_id): UPDATE customer SET deleted_at = NULL
3. Response: {message: "Khách hàng đã được khôi phục", customer: {...}}

---

## 4. Bảng Database

### Bảng `customer`

| Cột                 | Kiểu        | Nullable | Constraint   | Mô Tả                 |
| ------------------- | ----------- | -------- | ------------ | --------------------- |
| `id`                | Integer     | NO       | PRIMARY KEY  | ID khách hàng         |
| `user_id`           | Integer     | YES      | FK→user(id)  | ID tài khoản (nếu có) |
| `full_name`         | String(255) | YES      |              | Họ tên                |
| `phone_number`      | String(20)  | YES      | INDEX        | SĐT                   |
| `email`             | String(255) | YES      |              | Email                 |
| `date_of_birth`     | Date        | YES      |              | Ngày sinh             |
| `gender`            | String(10)  | YES      |              | Giới tính             |
| `address`           | Text        | YES      |              | Địa chỉ               |
| `notes`             | Text        | YES      |              | Ghi chú CRM           |
| `skin_type`         | String(50)  | YES      |              | Loại da               |
| `health_conditions` | Text        | YES      |              | Tình trạng sức khỏe   |
| `is_active`         | Boolean     | NO       | DEFAULT TRUE | Trạng thái            |
| `created_at`        | DateTime    | NO       | DEFAULT NOW  | Ngày tạo              |
| `updated_at`        | DateTime    | NO       | DEFAULT NOW  | Ngày cập nhật         |
| `deleted_at`        | DateTime    | YES      | DEFAULT NULL | Soft delete           |

### Indexes

```sql
-- Primary & Foreign Key
CREATE INDEX idx_customer_user_id ON customer(user_id);
CREATE INDEX idx_customer_phone ON customer(phone_number);
CREATE INDEX idx_customer_deleted_at ON customer(deleted_at);

-- Compound index for soft delete queries
CREATE INDEX idx_customer_phone_not_deleted ON customer(phone_number) WHERE deleted_at IS NULL;
```

---

## 5. Dependencies & Helpers

### Dependencies

- **`get_current_user(token: str)`** - Lấy User từ JWT (từ 0001_PLAN)
- **`get_customer_or_none(current_user: User)`** - Lấy Customer liên kết, trả None nếu không có

### Helper Functions

- **Trong `src/core/utils.py`:**
  - `normalize_phone_number(phone: str) -> str` - Normalize SĐT (0912345678 / +84912345678)

---

## 6. Validation Rules

- **phone_number**: Format Việt Nam, không duplicate (trong non-deleted records)
- **full_name**: 1-255 ký tự, không bỏ trống khi có user_id
- **email**: Email format hợp lệ (từ User)
- **OTP**: 6 ký tự, TTL 5 phút

---

## 7. Error Handling

| HTTP | Error             | Mô Tả                              |
| ---- | ----------------- | ---------------------------------- |
| 400  | Bad Request       | Dữ liệu invalid                    |
| 404  | Not Found         | Customer / hồ sơ cũ không tìm thấy |
| 409  | Conflict          | Phone/email đã tồn tại             |
| 401  | Unauthorized      | JWT không hợp lệ                   |
| 429  | Too Many Requests | Rate limit (OTP)                   |
| 500  | Server Error      | Lỗi server (SMS fail, etc.)        |

---

## 8. Alembic Migration

```sql
-- Tạo bảng Customer
CREATE TABLE customer (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) ON DELETE SET NULL,
    full_name VARCHAR(255),
    phone_number VARCHAR(20),
    date_of_birth DATE,
    gender VARCHAR(10),
    address TEXT,
    notes TEXT,
    skin_type VARCHAR(50),
    health_conditions TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL
);

-- Tạo indexes
CREATE INDEX idx_customer_user_id ON customer(user_id);
CREATE INDEX idx_customer_phone ON customer(phone_number);
CREATE INDEX idx_customer_deleted_at ON customer(deleted_at);
```

---

## 9. Notes & Considerations

1. **Soft Delete (Xóa Mềm) - BẮT BUỘC**

   - Tất cả delete phải dùng soft delete (SET deleted_at = now())
   - Không được xóa cứng (DELETE statement)
   - Tất cả query phải filter `deleted_at IS NULL`

2. **Transaction Safety**

   - Luồng 3d (hợp nhất hồ sơ) chạy trong transaction
   - Thêm `.with_for_update()` lock để tránh race condition

3. **OTP Management**

   - Dùng Redis hoặc cache backend (không DB)
   - TTL 5 phút
   - Retry limit 5 lần
   - Rate limit 3 yêu cầu/1 giờ

4. **Phone Number Normalize**

   - Áp dụng `normalize_phone_number()` **trước mọi lần store/query**
   - Xử lý cả "+84..." và "0..." formats

5. **SMS Service**

   - Nếu không có: Log OTP, email fallback, hoặc webhook
   - Dev mode: In OTP ra console

6. **Index Performance**

   - Partial unique index trên phone_number WHERE deleted_at IS NULL (PostgreSQL)
   - Hoặc application-level validation (SQLite)

7. **Testing**

   - Unit test: create, update, soft delete, restore, search
   - Integration test: tất cả endpoints + concurrent requests
   - Mock SMS service

8. **Authorization**
   - Thêm role-based checks (receptionist, admin)
   - DELETE: receptionist + admin
   - RESTORE: admin only

---

## 10. Timeline & Thực Hiện

| Tuần | Task                            | Priority |
| ---- | ------------------------------- | -------- |
| 1    | Models + CRUD + basic endpoints | HIGH     |
| 1    | OTP + Account linking logic     | HIGH     |
| 1    | Soft delete + restore           | HIGH     |
| 2    | Phone normalize + validation    | HIGH     |
| 2    | Unit tests + integration tests  | MEDIUM   |
| 2    | Rate limiting + authorization   | MEDIUM   |
| 3    | Performance tuning + indexes    | LOW      |
