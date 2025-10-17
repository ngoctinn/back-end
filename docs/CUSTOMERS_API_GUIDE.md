# 👥 Customer Module - Hướng Dẫn Chi Tiết

**Phiên bản:** 1.0 | **Cập nhật:** Oct 17, 2025

---

## 📑 Mục Lục

1. [Tổng Quan](#-tổng-quan)
2. [Kiến Trúc Module](#-kiến-trúc-module)
3. [Data Model](#-data-model)
4. [API Endpoints](#-api-endpoints)
5. [Luồng Nghiệp Vụ](#-luồng-nghiệp-vụ)
6. [Ví Dụ Sử Dụng](#-ví-dụ-sử-dụng)
7. [Xử Lý Lỗi](#-xử-lý-lỗi)
8. [Best Practices](#-best-practices)

---

## 📋 Tổng Quan

### Mục Đích

Module `customers` quản lý **hồ sơ khách hàng (CRM)** độc lập với tài khoản xác thực (Auth).

**Đặc điểm chính:**

- ✅ **Khách hàng vãng lai (Walk-in):** Không cần tài khoản, chỉ cần tên + SĐT
- ✅ **Khách hàng online:** Liên kết với tài khoản User (1-to-1)
- ✅ **Quản lý hồ sơ:** Lưu thông tin chi tiết (ngày sinh, giới tính, loại da, ghi chú y tế)
- ✅ **Xóa mềm (Soft Delete):** Không xóa vĩnh viễn, có thể khôi phục
- ✅ **Tìm kiếm:** Theo tên hoặc số điện thoại

### Quy Ước

| Khái Niệm            | Định Nghĩa                            | Ví Dụ                                     |
| -------------------- | ------------------------------------- | ----------------------------------------- |
| **Walk-in Customer** | Khách hàng vãng lai, `user_id = NULL` | Khách đến lần đầu không đăng ký tài khoản |
| **Online Customer**  | Có tài khoản, `user_id != NULL`       | Khách đăng ký app, đã đăng nhập           |
| **Stub Customer**    | Hồ sơ "chờ" khi user vừa đăng ký      | Full name & phone chưa hoàn thành         |
| **Soft Delete**      | Đặt `deleted_at`, không xóa thực sự   | Có thể khôi phục sau                      |

---

## 🏗️ Kiến Trúc Module

### Cấu Trúc Thư Mục

```
src/modules/customers/
├── __init__.py              # Export công khai
├── models.py                # SQLModel - Database schema
├── schemas.py               # Pydantic - Request/Response DTOs
├── router.py                # FastAPI routes
├── service.py               # Business logic
├── crud.py                  # Database operations (CRUD)
└── test_customers.py        # Unit tests (nếu có)
```

### Kiến Trúc Tầng

```
┌─────────────────────────────────────────┐
│  FastAPI Router (router.py)             │  HTTP endpoints
│  ├─ POST /customers/walk-in             │  Create walk-in
│  ├─ POST /customers/profile             │  Complete profile
│  ├─ GET /customers/{id}                 │  Get customer
│  ├─ PUT /customers/{id}                 │  Update
│  └─ DELETE /customers/{id}              │  Soft delete
├─────────────────────────────────────────┤
│  Service Layer (service.py)             │  Business logic
│  ├─ create_walk_in_customer()           │
│  ├─ complete_customer_profile()         │
│  ├─ verify_otp_and_link_account()       │
│  ├─ delete_customer()                   │
│  └─ restore_customer()                  │
├─────────────────────────────────────────┤
│  CRUD Layer (crud.py)                   │  Database access
│  ├─ create_customer()                   │
│  ├─ get_customer_by_id()                │
│  ├─ update_customer()                   │
│  └─ soft_delete_customer()              │
├─────────────────────────────────────────┤
│  Database (PostgreSQL)                  │  Persistent data
│  └─ customer table                      │
└─────────────────────────────────────────┘
```

---

## 💾 Data Model

### Customer Table Schema

```sql
CREATE TABLE customer (
    id                 INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id            INTEGER UNIQUE NULL (FK -> user.id),
    full_name          VARCHAR(255) NULL,
    phone_number       VARCHAR(20) UNIQUE NULL,
    date_of_birth      DATE NULL,
    gender             VARCHAR(10) NULL,          -- 'nam', 'nữ', 'khác'
    address            TEXT NULL,
    notes              TEXT NULL,                 -- Ghi chú CSKH
    skin_type          VARCHAR(50) NULL,          -- 'khô', 'dầu', 'hỗn hợp', 'nhạy cảm'
    health_conditions  TEXT NULL,                 -- Dị ứng, bệnh nền
    is_active          BOOLEAN NOT NULL = True,
    created_at         TIMESTAMP NOT NULL,        -- UTC
    updated_at         TIMESTAMP NOT NULL,        -- UTC
    deleted_at         TIMESTAMP NULL             -- Soft delete
);

-- Indexes for performance
CREATE INDEX idx_customer_user_id ON customer(user_id);
CREATE INDEX idx_customer_phone_number ON customer(phone_number);
CREATE INDEX idx_customer_deleted_at ON customer(deleted_at);
```

### Pydantic Schemas

#### Request: Create Walk-in Customer

```python
class CustomerCreateRequest(BaseModel):
    full_name: str          # Min 1, Max 255
    phone_number: str       # Min 9, Max 20, auto-normalized
```

**Normalize** tự động:

- Loại bỏ khoảng trắng, ký tự đặc biệt
- Duy trì mã quốc gia (nếu có): `+84...` hoặc `0...`

#### Request: Complete Profile

```python
class CustomerCompleteProfileRequest(BaseModel):
    full_name: str                      # Required
    phone_number: str                   # Required
    date_of_birth: Optional[date]       # Optional
    gender: Optional[str]               # Optional
    address: Optional[str]              # Optional
    notes: Optional[str]                # Optional
    skin_type: Optional[str]            # Optional
    health_conditions: Optional[str]    # Optional
```

#### Request: Update Customer

```python
class CustomerUpdateRequest(BaseModel):
    full_name: Optional[str]            # All fields optional
    phone_number: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    address: Optional[str]
    notes: Optional[str]
    skin_type: Optional[str]
    health_conditions: Optional[str]
    is_active: Optional[bool]
```

#### Response: Customer

```python
class CustomerResponse(BaseModel):
    id: int
    user_id: Optional[int]
    full_name: Optional[str]
    phone_number: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    address: Optional[str]
    notes: Optional[str]
    skin_type: Optional[str]
    health_conditions: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True  # SQLAlchemy -> Pydantic
```

---

## 🔌 API Endpoints

### 1️⃣ Create Walk-in Customer (Luồng 1)

**Tạo khách hàng vãng lai - không yêu cầu tài khoản.**

```
POST /customers/walk-in
Content-Type: application/json

{
  "full_name": "Nguyễn Văn A",
  "phone_number": "0901234567"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "user_id": null,
  "full_name": "Nguyễn Văn A",
  "phone_number": "0901234567",
  "date_of_birth": null,
  "gender": null,
  "address": null,
  "notes": null,
  "skin_type": null,
  "health_conditions": null,
  "is_active": true,
  "created_at": "2025-10-17T10:30:00Z",
  "updated_at": "2025-10-17T10:30:00Z",
  "deleted_at": null
}
```

**Errors:**

| Status            | Error                      | Nguyên Nhân        |
| ----------------- | -------------------------- | ------------------ |
| `409 Conflict`    | `Số điện thoại đã tồn tại` | Phone number trùng |
| `400 Bad Request` | Validation error           | Request format sai |

---

### 2️⃣ Complete Profile (Luồng 2b)

**Hoàn thành hồ sơ khi user đã đăng ký - cập nhật full_name & phone_number cho stub customer.**

```
POST /customers/profile
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "full_name": "Nguyễn Văn B",
  "phone_number": "0987654321",
  "date_of_birth": "1990-05-15",
  "gender": "nam",
  "address": "123 Đường A, TP HCM",
  "skin_type": "hỗn hợp",
  "health_conditions": "Dị ứng với xà phòng mạnh"
}
```

**Response (200 OK):**

```json
{
  "id": 2,
  "user_id": 5,
  "full_name": "Nguyễn Văn B",
  "phone_number": "0987654321",
  "date_of_birth": "1990-05-15",
  "gender": "nam",
  "address": "123 Đường A, TP HCM",
  "notes": null,
  "skin_type": "hỗn hợp",
  "health_conditions": "Dị ứng với xà phòng mạnh",
  "is_active": true,
  "created_at": "2025-10-17T10:00:00Z",
  "updated_at": "2025-10-17T10:35:00Z",
  "deleted_at": null
}
```

**Requirements:**

- ✅ JWT token bắt buộc (authenticated user)
- ✅ User chỉ có thể cập nhật hồ sơ của chính mình
- ✅ Phone number phải duy nhất

**Errors:**

| Status             | Error                    | Nguyên Nhân                     |
| ------------------ | ------------------------ | ------------------------------- |
| `401 Unauthorized` | No token                 | Không gửi JWT                   |
| `404 Not Found`    | Hồ sơ không tìm thấy     | User chưa có stub customer      |
| `409 Conflict`     | Số điện thoại đã tồn tại | Phone trùng với khách hàng khác |

---

### 3️⃣ Get Customer

**Lấy thông tin khách hàng theo ID.**

```
GET /customers/{customer_id}

# Example
GET /customers/1
```

**Response (200 OK):**

```json
{
  "id": 1,
  "user_id": null,
  "full_name": "Nguyễn Văn A",
  "phone_number": "0901234567",
  "date_of_birth": null,
  "gender": null,
  "address": null,
  "notes": null,
  "skin_type": null,
  "health_conditions": null,
  "is_active": true,
  "created_at": "2025-10-17T10:30:00Z",
  "updated_at": "2025-10-17T10:30:00Z",
  "deleted_at": null
}
```

**Errors:**

| Status          | Error                                    |
| --------------- | ---------------------------------------- |
| `404 Not Found` | Khách hàng không tìm thấy hoặc đã bị xóa |

---

### 4️⃣ Update Customer

**Cập nhật thông tin khách hàng (yêu cầu authentication).**

```
PUT /customers/{customer_id}
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "full_name": "Nguyễn Văn A Updated",
  "address": "456 Đường B, Hà Nội",
  "notes": "Ưa thích massage nhẹ"
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "user_id": null,
  "full_name": "Nguyễn Văn A Updated",
  "phone_number": "0901234567",
  "date_of_birth": null,
  "gender": null,
  "address": "456 Đường B, Hà Nội",
  "notes": "Ưa thích massage nhẹ",
  "skin_type": null,
  "health_conditions": null,
  "is_active": true,
  "created_at": "2025-10-17T10:30:00Z",
  "updated_at": "2025-10-17T11:00:00Z",
  "deleted_at": null
}
```

**Notes:**

- ✅ Partial update (chỉ cập nhật fields được gửi)
- ✅ JWT token bắt buộc
- ✅ User chỉ có thể cập nhật hồ sơ của chính mình (nếu `user_id` trùng)

**Errors:**

| Status             | Error                     |
| ------------------ | ------------------------- |
| `401 Unauthorized` | No token                  |
| `403 Forbidden`    | User không sở hữu hồ sơ   |
| `404 Not Found`    | Khách hàng không tìm thấy |
| `409 Conflict`     | Phone number đã tồn tại   |

---

### 5️⃣ Delete Customer (Soft Delete - Luồng 4)

**Xóa mềm khách hàng (đặt `deleted_at`, không xóa vĩnh viễn).**

```
DELETE /customers/{customer_id}
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK):**

```json
{
  "message": "Khách hàng đã bị xóa",
  "can_restore": true
}
```

**Notes:**

- ✅ JWT token bắt buộc
- ✅ Dữ liệu vẫn tồn tại trong database
- ✅ Có thể khôi phục sau (thông qua admin panel)

**Errors:**

| Status             | Error                                    |
| ------------------ | ---------------------------------------- |
| `401 Unauthorized` | No token                                 |
| `404 Not Found`    | Khách hàng không tìm thấy hoặc đã bị xóa |

---

## 🔄 Luồng Nghiệp Vụ

### Luồng 1: Khách Hàng Vãng Lai Đến Lần Đầu

```
┌─────────────────────────────────────────────────────┐
│ Khách hàng vãng lai (không app, không tài khoản)   │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ Spa staff tạo khách hàng trên app:                 │
│ POST /customers/walk-in                             │
│ {full_name, phone_number}                          │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ ✅ Customer record tạo với user_id = NULL          │
│ - id: 1                                            │
│ - full_name: "Nguyễn Văn A"                        │
│ - phone_number: "0901234567"                       │
│ - user_id: NULL (vãng lai)                         │
└─────────────────────────────────────────────────────┘
```

**Code:**

```python
# service.py
customer = service.create_walk_in_customer(
    db,
    full_name="Nguyễn Văn A",
    phone_number="0901234567"
)
# ✅ Returns Customer(id=1, user_id=None, ...)
```

---

### Luồng 2a: Khách Hàng Đăng Ký Tài Khoản (Từ Vãng Lai)

```
┌─────────────────────────────────────────────────────┐
│ Khách hàng vãng lai (đã có record CRM)             │
│ Quyết định đăng ký tài khoản online                │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ Auth module: POST /auth/register                    │
│ {email, password}                                   │
│ → Tạo User record (id: 5)                          │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ Customers module: Tạo stub customer với user_id    │
│ create_online_customer_with_user(                  │
│     db,                                             │
│     user_id=5,                                      │
│     full_name=None,                                 │
│     phone_number=None                              │
│ )                                                   │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ ✅ Stub Customer tạo (Chờ hoàn thành hồ sơ)       │
│ - id: 2                                            │
│ - user_id: 5 (linked với user)                     │
│ - full_name: NULL (chưa hoàn thành)                │
│ - phone_number: NULL (chưa hoàn thành)             │
└─────────────────────────────────────────────────────┘
```

---

### Luồng 2b: Hoàn Thành Hồ Sơ

```
┌─────────────────────────────────────────────────────┐
│ Khách hàng đã đăng nhập (có JWT token)             │
│ Điền thêm thông tin hồ sơ                          │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ POST /customers/profile                             │
│ Authorization: Bearer <JWT>                         │
│ {                                                   │
│   full_name: "Nguyễn Văn B",                       │
│   phone_number: "0987654321",                      │
│   date_of_birth: "1990-05-15",                     │
│   ...                                               │
│ }                                                   │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ Service: Cập nhật stub customer                    │
│ complete_customer_profile(                         │
│     db,                                             │
│     customer_id=2,                                  │
│     full_name="Nguyễn Văn B",                      │
│     phone_number="0987654321"                      │
│ )                                                   │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ ✅ Stub Customer được cập nhật                      │
│ - id: 2                                            │
│ - user_id: 5                                       │
│ - full_name: "Nguyễn Văn B" ✅ (Được set)          │
│ - phone_number: "0987654321" ✅ (Được set)         │
│ - Các field khác: Được cập nhật theo request      │
└─────────────────────────────────────────────────────┘
```

---

### Luồng 3: Liên Kết Khách Hàng Cũ Với Tài Khoản Mới

```
┌──────────────────────────────────────────────────────┐
│ Khách hàng cũ (vãng lai, có record CRM)             │
│ + Tài khoản online mới                              │
│ → Muốn link 2 hồ sơ thành 1                        │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│ Step 1: Bắt đầu linking (Luồng 3c)                 │
│ POST /customers/link (hypothetical)                 │
│ {phone_number: "0901234567"}                       │
│ → Tìm old customer và send OTP                     │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│ Step 2: Xác minh OTP (Luồng 3d)                    │
│ POST /customers/verify-otp                         │
│ Authorization: Bearer <JWT>                         │
│ {                                                   │
│   phone_number: "0901234567",                      │
│   otp_code: "123456"                               │
│ }                                                   │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│ Service: Transaction (Atomic)                       │
│ verify_otp_and_link_account(                        │
│     db,                                             │
│     user_id=5,                                      │
│     phone_number="0901234567",                      │
│     otp_code="123456"                              │
│ )                                                   │
│                                                     │
│ Actions:                                            │
│ 1. Verify OTP                                       │
│ 2. Update old_customer.user_id = 5                 │
│ 3. Soft delete stub_customer                       │
│ 4. Commit transaction                              │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│ ✅ Linking thành công                              │
│                                                     │
│ OLD CUSTOMER (Vãng lai)          STUB CUSTOMER    │
│ id: 1                             id: 2            │
│ full_name: "Nguyễn Văn A"        full_name: NULL  │
│ phone: "0901234567"              phone: NULL      │
│ user_id: NULL ──────────────→    user_id: 5       │
│                (Link)            deleted_at: ✅   │
│                                  (Soft deleted)   │
│                                                     │
│ → Khách hàng sử dụng old_customer(id=1)           │
│ → Stub customer(id=2) không còn active             │
└──────────────────────────────────────────────────────┘
```

---

### Luồng 4: Xóa Khách Hàng (Soft Delete)

```
┌─────────────────────────────────────┐
│ User yêu cầu xóa tài khoản / hồ sơ │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ DELETE /customers/{customer_id}      │
│ Authorization: Bearer <JWT>          │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Service: Soft delete                │
│ delete_customer(db, customer_id)    │
│                                     │
│ Action: Set deleted_at = now()      │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ ✅ Customer "deleted"               │
│ - deleted_at: 2025-10-17T11:05:00Z │
│ - Dữ liệu vẫn có trong DB           │
│ - Không hiện trong GET endpoints    │
│ - Có thể khôi phục (admin)          │
└─────────────────────────────────────┘
```

---

### Luồng 5: Khôi Phục Khách Hàng (Admin)

```
┌──────────────────────────────────────┐
│ Admin restore deleted customer       │
│ restore_customer(db, customer_id)    │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Action: Set deleted_at = NULL        │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ ✅ Customer restored                │
│ - deleted_at: NULL                  │
│ - Quay trở lại hoạt động            │
└──────────────────────────────────────┘
```

---

## 📝 Ví Dụ Sử Dụng

### Python (Requests)

#### 1. Create Walk-in Customer

```python
import requests

url = "http://localhost:8000/customers/walk-in"
payload = {
    "full_name": "Nguyễn Văn A",
    "phone_number": "0901234567"
}
response = requests.post(url, json=payload)

if response.status_code == 200:
    customer = response.json()
    print(f"✅ Customer created: {customer['id']}")
else:
    print(f"❌ Error: {response.json()['detail']}")
```

#### 2. Complete Profile (Authenticated)

```python
import requests

url = "http://localhost:8000/customers/profile"
headers = {
    "Authorization": f"Bearer {jwt_token}"
}
payload = {
    "full_name": "Nguyễn Văn B",
    "phone_number": "0987654321",
    "date_of_birth": "1990-05-15",
    "gender": "nam",
    "address": "123 Đường A, TP HCM",
    "skin_type": "hỗn hợp",
    "health_conditions": "Dị ứng với xà phòng"
}
response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    print("✅ Profile completed")
else:
    print(f"❌ Error: {response.json()['detail']}")
```

#### 3. Update Customer

```python
import requests

customer_id = 1
url = f"http://localhost:8000/customers/{customer_id}"
headers = {"Authorization": f"Bearer {jwt_token}"}
payload = {
    "notes": "Ưa thích massage nhẹ, tránh vùng vai"
}
response = requests.put(url, json=payload, headers=headers)

if response.status_code == 200:
    print("✅ Customer updated")
else:
    print(f"❌ Error: {response.json()['detail']}")
```

#### 4. Get Customer

```python
import requests

customer_id = 1
url = f"http://localhost:8000/customers/{customer_id}"
response = requests.get(url)

if response.status_code == 200:
    customer = response.json()
    print(f"Name: {customer['full_name']}")
    print(f"Phone: {customer['phone_number']}")
    print(f"Skin Type: {customer['skin_type']}")
else:
    print("❌ Customer not found")
```

#### 5. Delete Customer

```python
import requests

customer_id = 1
url = f"http://localhost:8000/customers/{customer_id}"
headers = {"Authorization": f"Bearer {jwt_token}"}
response = requests.delete(url, headers=headers)

if response.status_code == 200:
    print(f"✅ {response.json()['message']}")
else:
    print(f"❌ Error: {response.json()['detail']}")
```

### cURL

#### Create Walk-in Customer

```bash
curl -X POST "http://localhost:8000/customers/walk-in" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Nguyễn Văn A",
    "phone_number": "0901234567"
  }'
```

#### Get Customer

```bash
curl -X GET "http://localhost:8000/customers/1"
```

#### Update Customer (with JWT)

```bash
curl -X PUT "http://localhost:8000/customers/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Ưa thích massage nhẹ"
  }'
```

---

## ⚠️ Xử Lý Lỗi

### Custom Exceptions

```python
class CustomerNotFoundError(Exception):
    """Khách hàng không tìm thấy."""
    pass

class PhoneNumberAlreadyExistsError(Exception):
    """Số điện thoại đã tồn tại."""
    pass

class InvalidOTPError(Exception):
    """OTP không hợp lệ hoặc hết hạn."""
    pass

class AccountLinkingError(Exception):
    """Lỗi khi liên kết tài khoản."""
    pass
```

### Error Response Format

```json
{
  "detail": "Số điện thoại đã tồn tại"
}
```

### HTTP Status Codes

| Code               | Meaning            | Thường gặp khi                            |
| ------------------ | ------------------ | ----------------------------------------- |
| `200 OK`           | Thành công         | GET, PUT, DELETE thành công               |
| `201 Created`      | Tạo thành công     | POST thành công                           |
| `400 Bad Request`  | Request sai format | Validation error (phone format sai, etc.) |
| `401 Unauthorized` | Cần authentication | Quên gửi JWT token                        |
| `403 Forbidden`    | Không có quyền     | User cập nhật hồ sơ người khác            |
| `404 Not Found`    | Không tìm thấy     | Customer không tồn tại                    |
| `409 Conflict`     | Dữ liệu xung đột   | Phone number trùng                        |
| `500 Server Error` | Lỗi server         | Database error, etc.                      |

---

## 🎯 Best Practices

### 1. Validate Phone Numbers

**Luôn normalize phone numbers:**

```python
from src.core.utils import normalize_phone_number

phone = normalize_phone_number("0901 234 567")
# Result: "0901234567"

phone = normalize_phone_number("+84 901 234 567")
# Result: "+84901234567"
```

### 2. Use Service Layer for Business Logic

❌ **Sai - Trực tiếp call CRUD:**

```python
@router.post("/customers/create")
def create(request: CustomerCreateRequest, db: Session):
    customer = crud.create_customer(
        db,
        full_name=request.full_name,
        phone_number=request.phone_number
    )
    return customer
```

✅ **Đúng - Gọi Service layer:**

```python
@router.post("/customers/walk-in")
def create_walk_in(request: CustomerCreateRequest, db: Session):
    try:
        customer = service.create_walk_in_customer(
            db,
            full_name=request.full_name,
            phone_number=request.phone_number
        )
        return customer
    except service.PhoneNumberAlreadyExistsError:
        raise HTTPException(status_code=409, detail="...")
```

### 3. Check Soft-Deleted Records

**Luôn kiểm tra `deleted_at` khi lấy records:**

```python
# ✅ Đúng - Exclude soft-deleted
customer = crud.get_customer_by_id(db, customer_id, include_deleted=False)

# ❌ Sai - Có thể lấy deleted record
customer = db.query(Customer).filter(Customer.id == customer_id).first()
```

### 4. Use Transactions for Account Linking

**Luôn dùng transaction khi update multiple records:**

```python
try:
    old_customer.user_id = user_id
    stub_customer.deleted_at = get_utc_now()
    db.commit()  # Atomic operation
except Exception as e:
    db.rollback()  # Rollback nếu có error
    raise
```

### 5. Implement Proper Authorization

**Kiểm tra ownership khi update:**

```python
# ✅ User chỉ có thể cập nhật hồ sơ của chính mình
if customer.user_id and customer.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Forbidden")
```

### 6. Log Important Operations

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"✓ Khách hàng tạo: ID={customer.id}, {full_name}")
logger.warning(f"⚠️ SĐT trùng: {phone_number}")
logger.error(f"❌ Lỗi linking: {str(e)}")
```

### 7. Handle Pagination in Search

```python
customers, total, total_pages = service.search_customers(
    db,
    search_query="Nguyễn",
    page=1,
    per_page=20
)
print(f"Found {total} customers on {total_pages} pages")
```

---

## 📚 Related Documentation

- **[DOCUMENTATION.md](./DOCUMENTATION.md)** - Tài liệu chính dự án
- **[AUTH_API_GUIDE.md](./AUTH_API_GUIDE.md)** - Auth module guide
- **[PRODUCT_BRIEF.md](./PRODUCT_BRIEF.md)** - Business requirements

---

**Hỏi gì khác?** Xem Swagger API docs tại `http://localhost:8000/docs`
