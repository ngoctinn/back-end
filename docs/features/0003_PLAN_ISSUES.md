# ⚠️ CÁC VẤN ĐỀ TIỀM ẨN & GIẢI PHÁP - PLAN 0003

## 📋 Tóm Tắt Thực Hiện

Kế hoạch 0003 có 10 vấn đề tiềm ẩn được phát hiện. Dưới đây là chi tiết từng vấn đề và giải pháp.

---

## 🔴 CÁC VẤN ĐỀ CRITICAL (Phải Sửa Ngay)

### 1️⃣ **CRITICAL: Xóa Hồ Sơ "Chờ" - Hard Delete Rất Nguy Hiểm**

**Vị trí:** Luồng 3.7, Bước 3.3

**Vấn đề hiện tại:**

```sql
-- NGUY HIỂM! Hard delete có thể break FK
DELETE FROM customer WHERE id = :old_stub_customer.id
```

**Tại sao nguy hiểm:**

- Nếu user đã tạo appointments trên hồ sơ "chờ" này, xóa sẽ break foreign key
- Không thể audit trail
- Không thể recover

**Giải pháp:**

```sql
-- Thay bằng soft delete
UPDATE customer
SET deleted_at = now(), updated_at = now()
WHERE id = :old_stub_customer.id
```

**Thực hiện:** Sửa logic luồng 3.7 Bước 3.3 ngay

---

### 2️⃣ **CRITICAL: Race Condition - Liên Kết Nhiều Tài Khoản Cùng SĐT**

**Vị trí:** Luồng 3.7, Transaction logic

**Vấn đề hiện tại:**

```
Thời điểm T1: User A query Customer(id=1, user_id=NULL) ✓
Thời điểm T2: User B query cùng Customer(id=1, user_id=NULL) ✓
Thời điểm T3: User A UPDATE customer SET user_id=A_id ✓
Thời điểm T4: User B UPDATE customer SET user_id=B_id ✓ (OVERWRITE!)
→ Customer bị liên kết với user B, user A bị fail

Hoặc: Foreign key conflict nếu trigger bỏ qua
```

**Giải pháp:**

```python
# Thêm Pessimistic Locking (FOR UPDATE)
customer_old = session.query(Customer).filter(
    Customer.id == old_real_customer.id
).with_for_update().first()  # ← LOCK FILE

# Kiểm tra xem user_id đã bị update không
if customer_old.user_id is not None:
    raise HTTPException(409, "Hồ sơ này đã được liên kết bởi người dùng khác")

# Bây giờ safe để UPDATE
customer_old.user_id = user_id
```

**Thực hiện:** Thêm `.with_for_update()` vào transaction 3.7 Bước 3.1

---

### 3️⃣ **CRITICAL: Số Điện Thoại Format Không Nhất Quán**

**Vị trí:** Customer model, toàn bộ service

**Vấn đề hiện tại:**

```
Khách hàng lịch sử: phone_number = "+84912345678"
User nhập: phone_number = "0912345678"
Query tìm kiếm: "WHERE phone_number = '0912345678'"
→ KHÔNG MATCH! ❌
```

**Giải pháp:**

```python
# Tạo utility function normalize_phone_number()
import re

def normalize_phone_number(phone: str) -> str:
    """
    Normalize số điện thoại Việt Nam.
    +84912345678 → 0912345678
    09-1234-5678 → 0912345678
    """
    if not phone:
        return None

    # Loại bỏ tất cả ký tự không phải số
    phone = re.sub(r'\D', '', phone)

    # Nếu bắt đầu bằng 84 (country code), convert thành 0
    if phone.startswith('84'):
        phone = '0' + phone[2:]

    return phone

# Sử dụng trong:
# 1. create_walk_in_customer()
phone_number = normalize_phone_number(phone_number)

# 2. initiate_account_linking()
phone_number = normalize_phone_number(phone_number)

# 3. get_customer_by_phone_and_no_user()
phone_number = normalize_phone_number(phone_number)
```

**Thực hiện:** Thêm `normalize_phone_number()` vào `src/core/utils.py` hoặc `src/modules/customers/utils.py`, dùng **trước mọi lần store/query**

---

## 🟠 CÁC VẤN ĐỀ HIGH PRIORITY

### 4️⃣ **HIGH: Duplicate Phone Number - Unique Constraint Conflict**

**Vị trí:** Bảng Customer, cột phone_number

**Vấn đề hiện tại:**

```sql
-- Schema hiện tại
CREATE TABLE customer (
    phone_number VARCHAR(20) UNIQUE,  -- ← PROBLEM!
    deleted_at TIMESTAMP NULL
);

-- Tình huống:
1. Walk-in: Customer(phone="0912345678", deleted_at=NULL)
2. User khác đăng ký: Cung cấp phone="0912345678"
→ UNIQUE constraint violation ❌
```

**Giải pháp A - PostgreSQL (Khuyến cáo):**

```sql
-- Partial Unique Index
CREATE UNIQUE INDEX unique_phone_not_deleted
ON customer(phone_number)
WHERE deleted_at IS NULL;

-- Giả sử có 2 record:
-- 1. id=1, phone="0912345678", deleted_at=NULL
-- 2. id=2, phone="0912345678", deleted_at='2025-10-16 10:00:00'
→ Index chỉ enforce unique trên deleted_at IS NULL
→ Được phép! ✓
```

**Giải pháp B - SQLite (Nếu không hỗ trợ partial index):**

```python
# Loại bỏ UNIQUE constraint ở DB
phone_number: str | None = Field(default=None, index=True)

# Validate trong application logic
existing = await crud.get_customer_by_phone_number(phone_number, include_deleted=False)
if existing:
    raise HTTPException(409, "SĐT này đã được sử dụng")
```

**Khuyến cáo:** Chọn **Giải pháp A** (PostgreSQL) hoặc **Giải pháp B** (SQLite compatible)

---

### 5️⃣ **HIGH: Duplicate Email - User Có Thể Tạo 2 Tài Khoản Bằng Email Cũ**

**Vị trí:** Bảng User, cột email

**Vấn đề hiện tại:**

```
Scenario:
1. User A tạo tài khoản: email="a@a.com" (deleted_at=NULL)
2. User A xóa tài khoản (soft delete): (deleted_at='2025-10-16 10:00:00')
3. User B tạo tài khoản: email="a@a.com"
→ UNIQUE constraint violation ❌
```

**Giải pháp - PostgreSQL:**

```sql
-- Partial Unique Index trên User table
CREATE UNIQUE INDEX unique_email_not_deleted
ON "user"(email)
WHERE deleted_at IS NULL;
```

**Thực hiện:**

- Thêm cột `deleted_at` vào **User model** (tương tự Customer)
- Thêm partial unique index trong Alembic migration

---

### 6️⃣ **HIGH: Email Field Ở Customer - Redundant** ✅ (ĐÃ QUYẾT ĐỊNH XOÁ)

**Vị trí:** Customer model

**Vấn đề:**

- Customer lưu email → User cũng lưu email → redundant, có thể out-of-sync

**Quyết Định:**
✅ **Xóa field `email` khỏi Customer model**

- Customer chỉ lưu: phone_number, full_name, address, skin_type, health_conditions, notes (thông tin CRM)
- Email lấy từ User.email khi cần thông qua relationship

**Status:** Đã cập nhật vào 0003_PLAN.md

---

## 🟡 CÁC VẤN ĐỀ MEDIUM PRIORITY

### 7️⃣ **MEDIUM: OTP Brute Force Attack - Không Có Rate Limit**

**Vị trí:** OTP module, service logic

**Vấn đề hiện tại:**

```
- Không limit số lần yêu cầu OTP
- Không limit số lần verify OTP
- Attacker có thể brute force 6-digit OTP (1M kombinasi)
```

**Giải pháp:**

```python
# src/core/otp.py

def generate_and_send_otp(phone_number: str, redis_client) -> bool:
    # Rate limit: 3 yêu cầu per 1 giờ
    key_requests = f"otp_requests:{phone_number}"
    requests_count = redis_client.incr(key_requests)

    if requests_count > 3:
        # Reset timer: 1 giờ = 3600 giây
        redis_client.expire(key_requests, 3600)
        raise HTTPException(429, "Quá nhiều yêu cầu, thử lại sau 1 giờ")

    if requests_count == 1:
        redis_client.expire(key_requests, 3600)

    # Generate OTP
    otp_code = generate_otp(6)

    # Store OTP + expiry (5 phút)
    key_otp = f"otp:{phone_number}"
    redis_client.setex(key_otp, 300, otp_code)  # 5 * 60 = 300 giây

    # Store verify attempts counter
    key_attempts = f"otp_attempts:{phone_number}"
    redis_client.delete(key_attempts)  # Reset attempts khi generate OTP mới

    # Gửi SMS
    return await send_otp_sms(phone_number, otp_code)


def verify_otp(phone_number: str, otp_code: str, redis_client) -> bool:
    # Retry limit: 5 lần
    key_attempts = f"otp_attempts:{phone_number}"
    attempts = redis_client.incr(key_attempts)

    if attempts > 5:
        # Xóa OTP, bắt user yêu cầu OTP mới
        redis_client.delete(f"otp:{phone_number}")
        raise HTTPException(400, "Quá nhiều lần nhập sai, vui lòng yêu cầu OTP mới")

    # Verify OTP
    key_otp = f"otp:{phone_number}"
    stored_otp = redis_client.get(key_otp)

    if not stored_otp:
        raise HTTPException(400, "OTP đã hết hạn")

    if stored_otp.decode() != otp_code:
        raise HTTPException(400, "OTP không đúng")

    # Success - clean up
    redis_client.delete(key_otp)
    redis_client.delete(key_attempts)

    return True
```

**Thực hiện:** Cập nhật `src/core/otp.py` với rate limiting logic

---

### 8️⃣ **MEDIUM: Query Customer Bằng Phone Number Chỉ - Endpoint Thiếu**

**Vị trí:** Router, frontend

**Vấn đề hiện tại:**

```
Lễ tân muốn lấy khách hàng bằng SĐT thôi
- API hiện tại: GET /customers/{customer_id}
- Lễ tân không biết customer_id
- Phải dùng search? Thì search endpoint là gì?
```

**Giải pháp:**

```python
# Thêm endpoint mới
@router.get("/customers/phone/{phone_number}", response_model=CustomerResponse)
async def get_customer_by_phone(
    phone_number: str,
    current_user: User = Depends(get_current_user)
):
    """
    Lấy khách hàng theo số điện thoại.
    Dành cho lễ tân quầy tiếp.
    """
    from src.core.utils import normalize_phone_number

    phone_number = normalize_phone_number(phone_number)

    customer = await crud.get_customer_by_phone_number(phone_number, include_deleted=False)
    if not customer:
        raise HTTPException(404, "Khách hàng không tìm thấy")

    return customer
```

**Hoặc cải thiện search endpoint:**

```python
@router.get("/customers/search")
async def search_customers(
    q: str,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    Tìm kiếm khách hàng theo tên hoặc SĐT.
    q: "0912345678" hoặc "Chị An"
    """
    from src.core.utils import normalize_phone_number

    # Nếu q là SĐT, normalize
    if q.replace('-', '').replace(' ', '').isdigit():
        q = normalize_phone_number(q)

    customers = await search_customers_service(q, skip=skip, limit=limit)
    return customers
```

**Thực hiện:** Thêm endpoint `GET /customers/phone/{phone_number}`

---

### 9️⃣ **MEDIUM: Authorization Checks Bị Thiếu**

**Vị trí:** Router endpoints

**Vấn đề hiện tại:**

```python
@router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: int):  # ← Không check role!
    # Bất kỳ ai cũng có thể xóa?
```

**Giải pháp:**

```python
# src/core/dependencies.py

from typing import List

def require_role(required_roles: List[str]):
    """
    Dependency để check role của user.
    """
    def _require_role(current_user: User = Depends(get_current_user)):
        if not hasattr(current_user, 'role') or current_user.role not in required_roles:
            raise HTTPException(403, "Bạn không có quyền thực hiện hành động này")
        return current_user
    return Depends(_require_role)


# Sử dụng trong router
@router.delete("/customers/{customer_id}")
async def delete_customer(
    customer_id: int,
    current_user: User = Depends(require_role(["receptionist", "admin"]))
):
    """Chỉ lễ tân và admin được phép xóa"""
    return await service.delete_customer(customer_id)

@router.post("/customers/{customer_id}/restore")
async def restore_customer(
    customer_id: int,
    current_user: User = Depends(require_role(["admin"]))
):
    """Chỉ admin được phép khôi phục"""
    return await service.restore_customer(customer_id)
```

**Thực hiện:** Thêm dependency `require_role()`, áp dụng vào các endpoint sensitive

---

## 🟢 CÁC VẤN ĐỀ LOW PRIORITY

### 🔟 **LOW: Concurrency Testing Bị Thiếu**

**Vị trí:** Testing

**Vấn đề hiện tại:**

- Luồng 3.7 (hợp nhất hồ sơ) có race condition risk
- **Không có spec về concurrent testing**

**Giải pháp:**

```python
# tests/test_customers_concurrent.py

import asyncio
from httpx import AsyncClient
import pytest

@pytest.mark.asyncio
async def test_concurrent_account_linking():
    """
    Test race condition khi 2 user liên kết cùng SĐT
    """
    phone_number = "0912345678"

    # Pre-setup: Tạo 1 customer cũ
    old_customer = await create_customer(phone_number=phone_number, user_id=None)

    # Create 2 user accounts
    user_a = await create_user(email="a@a.com")
    user_b = await create_user(email="b@b.com")

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Concurrent requests: cả 2 user cố liên kết cùng SĐT
        async def link_account(user_id):
            return await client.post(
                "/customers/link-account/initiate",
                json={"phone_number": phone_number},
                headers={"Authorization": f"Bearer {user_id}"}
            )

        # Chạy concurrent
        results = await asyncio.gather(
            link_account(user_a.id),
            link_account(user_b.id),
            return_exceptions=True
        )

        # Kiểm tra: Chỉ 1 request thành công, 1 request fail
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == 200)
        assert success_count == 1, "Chỉ 1 user được phép liên kết"
```

**Thực hiện:** Thêm integration test cho concurrent requests (tuỳ chọn, ưu tiên thấp)

---

## 📋 SUMMARY - PRIORITY MATRIX

| Priority    | Vấn Đề | Hành Động                              | Tệp                        |
| ----------- | ------ | -------------------------------------- | -------------------------- | ------- |
| 🔴 CRITICAL | 8.2    | Sửa 3.7.3.3: DELETE → soft delete      | 0003_PLAN.md               |
| 🔴 CRITICAL | 8.5    | Thêm `.with_for_update()`              | crud.py                    |
| 🔴 CRITICAL | 8.9    | Thêm `normalize_phone_number()`        | utils.py                   |
| 🟠 HIGH     | 8.1    | Thêm partial unique index              | alembic migration          |
| 🟠 HIGH     | 8.3    | Thêm `deleted_at` cho User             | models.py                  |
| 🟠 HIGH     | 8.6    | Xóa email field khỏi Customer          | models.py                  | ✅ DONE |
| 🟡 MEDIUM   | 8.4    | Thêm rate limit OTP                    | otp.py                     |
| 🟡 MEDIUM   | 8.7    | Thêm `/customers/phone/{phone_number}` | router.py                  |
| 🟡 MEDIUM   | 8.8    | Thêm role checks                       | router.py, dependencies.py |
| 🟢 LOW      | 8.10   | Thêm concurrent test                   | tests/                     |

---

## ✅ Tiếp Theo

1. **Ngay lập tức:** Fix 3 vấn đề CRITICAL (8.2, 8.5, 8.9)
2. **Tuần này:** Fix các vấn đề HIGH (8.1, 8.3)
3. **Tuần tới:** Fix các vấn đề MEDIUM (8.4, 8.7, 8.8)
4. **Nếu có thời gian:** Fix vấn đề LOW (8.10)
