"""API DOCUMENTATION - CUSTOMER MANAGEMENT ENDPOINTS

Tài liệu hướng dẫn sử dụng các API endpoints của module khách hàng.
"""

# ============================================================================

# 1. LUỒNG 1: KHÁCH HÀNG VÃNG LAI (WALK-IN)

# ============================================================================

"""
POST /customers/walk-in

Tạo khách hàng vãng lai (không cần tài khoản).

Request:
Content-Type: application/json
{
"full_name": "Nguyễn Văn A",
"phone_number": "0912345678"
}

Response 200 OK:
{
"id": 1,
"user_id": null,
"full_name": "Nguyễn Văn A",
"phone_number": "0912345678",
"date_of_birth": null,
"gender": null,
"address": null,
"notes": null,
"skin_type": null,
"health_conditions": null,
"is_active": true,
"created_at": "2025-10-16T21:00:00",
"updated_at": "2025-10-16T21:00:00",
"deleted_at": null
}

Response 409 Conflict:
{
"detail": "Số điện thoại đã tồn tại"
}
"""

# ============================================================================

# 2. LUỒNG 2: ĐẠN GKY ONLINE & HOÀN THIỆN HỒ SƠ

# ============================================================================

"""
POST /customers/profile

Hoàn thiện hồ sơ khách hàng sau khi đăng ký online.
Yêu cầu JWT token.

Headers:
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request:
{
"full_name": "Nguyễn Văn A",
"phone_number": "0912345678"
}

Response 200 OK:
{
"id": 2,
"user_id": 1,
"full_name": "Nguyễn Văn A",
"phone_number": "0912345678",
...
}

Response 401 Unauthorized:
{
"detail": "Token không hợp lệ"
}

Response 404 Not Found:
{
"detail": "Hồ sơ khách hàng không tìm thấy"
}

Response 409 Conflict:
{
"detail": "Số điện thoại đã tồn tại"
}
"""

# ============================================================================

# 3. LUỒNG 3: LIÊN KẾT TÀI KHOẢN

# ============================================================================

"""
GET /customers/me/profile

Lấy hồ sơ khách hàng của user hiện tại (Bước 1: Kích hoạt liên kết).
Yêu cầu JWT token.

Headers:
Authorization: Bearer <jwt_token>

Response 200 OK:
{
"id": 2,
"user_id": 1,
"full_name": null,
"phone_number": null,
"is_active": true,
"created_at": "2025-10-16T20:00:00",
"updated_at": "2025-10-16T20:00:00",
"deleted_at": null
}

    Note: Nếu full_name=null && phone_number=null → là hồ sơ "chờ"
          → Frontend hiển thị "Bạn là khách hàng thân thiết? Liên kết ngay!"

Response 401 Unauthorized:
{
"detail": "Token không hợp lệ"
}

Response 404 Not Found:
{
"detail": "Hồ sơ khách hàng không tìm thấy"
}
"""

"""
POST /customers/link-account/initiate

Bắt đầu liên kết tài khoản - Gửi OTP (Bước 2).
Yêu cầu JWT token.

Headers:
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request:
{
"phone_number": "0912345678"
}

Response 200 OK:
{
"message": "OTP đã được gửi đến 0912345678"
}

Response 401 Unauthorized:
{
"detail": "Token không hợp lệ"
}

Response 404 Not Found:
{
"detail": "Không tìm thấy hồ sơ khách hàng cũ với SĐT này"
}

Response 500 Internal Server Error:
{
"detail": "Lỗi gửi OTP: ..."
}

Note: Trong dev mode, OTP được in ra console
Định dạng SĐT: 0912345678 hoặc +84912345678 đều được
"""

"""
POST /customers/link-account/verify

Xác minh OTP và hoàn tất liên kết tài khoản (Bước 3).
Yêu cầu JWT token.

Headers:
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request:
{
"phone_number": "0912345678",
"otp_code": "123456"
}

Response 200 OK:
{
"id": 1,
"user_id": 1,
"full_name": "Nguyễn Văn A",
"phone_number": "0912345678",
"date_of_birth": "1990-05-15",
"gender": "Nam",
"address": "Hà Nội",
"notes": "Khách hàng thân thiết",
"skin_type": "Khô",
"health_conditions": null,
"is_active": true,
"created_at": "2025-10-01T10:00:00",
"updated_at": "2025-10-16T21:05:00",
"deleted_at": null
}

    Note: Trả về hồ sơ khách hàng CỪ (đã cập nhật user_id)
          Hồ sơ stub của user mới bị xóa mềm (deleted_at được đặt)

Response 401 Unauthorized:
{
"detail": "OTP không hợp lệ hoặc hết hạn"
}

Response 404 Not Found:
{
"detail": "Hồ sơ khách hàng không tìm thấy"
}

Response 409 Conflict:
{
"detail": "Lỗi liên kết tài khoản: ..."
}

Note: OTP hết hạn sau 5 phút
Nếu nhập sai 5 lần → OTP bị lock
"""

# ============================================================================

# 4. TRUY VẤN & QUẢN LÝ KHÁCH HÀNG

# ============================================================================

"""
GET /customers/{customer_id}

Lấy thông tin khách hàng theo ID.
Không bao gồm khách hàng bị xóa mềm.

Path Parameter:
customer_id: int (ID khách hàng)

Response 200 OK:
{
"id": 1,
"user_id": null,
"full_name": "Nguyễn Văn A",
"phone_number": "0912345678",
...
}

Response 404 Not Found:
{
"detail": "Khách hàng không tìm thấy"
}
"""

"""
GET /customers?search_query=Nguyễn&page=1&per_page=20

Tìm kiếm khách hàng theo tên hoặc SĐT.
Không bao gồm khách hàng bị xóa mềm.

Query Parameters:
search_query: str (optional) - Tìm kiếm theo tên hoặc SĐT
page: int (default=1) - Trang (1-based)
per_page: int (default=20) - Số item trên mỗi trang

Response 200 OK:
{
"customers": [
{
"id": 1,
"full_name": "Nguyễn Văn A",
"phone_number": "0912345678",
...
},
{
"id": 3,
"full_name": "Nguyễn Thị B",
"phone_number": "0987654321",
...
}
],
"total": 2,
"page": 1,
"per_page": 20
}

Examples:
GET /customers
GET /customers?search_query=Nguyễn
GET /customers?search_query=0912345678
GET /customers?page=2&per_page=10
"""

"""
PUT /customers/{customer_id}

Cập nhật thông tin khách hàng.
Yêu cầu JWT token.

Headers:
Authorization: Bearer <jwt_token>
Content-Type: application/json

Path Parameter:
customer_id: int

Request:
{
"full_name": "Nguyễn Văn A",
"phone_number": "0912345678",
"date_of_birth": "1990-05-15",
"gender": "Nam",
"address": "123 Đường Lê Lợi, Hà Nội",
"notes": "Khách hàng VIP",
"skin_type": "Dầu",
"health_conditions": null,
"is_active": true
}

    Note: Tất cả fields là optional (chỉ cập nhật fields được gửi)

Response 200 OK:
{
"id": 1,
"full_name": "Nguyễn Văn A",
...
}

Response 401 Unauthorized:
{
"detail": "Token không hợp lệ"
}

Response 404 Not Found:
{
"detail": "Khách hàng không tìm thấy"
}

Response 409 Conflict:
{
"detail": "Số điện thoại đã tồn tại"
}
"""

# ============================================================================

# 5. XÓA & KHÔI PHỤC

# ============================================================================

"""
DELETE /customers/{customer_id}

Xóa mềm khách hàng (đặt deleted_at = now()).
Yêu cầu JWT token.

Headers:
Authorization: Bearer <jwt_token>

Path Parameter:
customer_id: int

Response 200 OK:
{
"message": "Khách hàng đã bị xóa",
"can_restore": true
}

Response 401 Unauthorized:
{
"detail": "Token không hợp lệ"
}

Response 404 Not Found:
{
"detail": "Khách hàng không tìm thấy hoặc đã bị xóa"
}

Note: Soft delete - Khách hàng không bị xóa cứng khỏi DB
Có thể khôi phục bất kỳ lúc nào
"""

"""
POST /customers/{customer_id}/restore

Khôi phục khách hàng bị xóa mềm (set deleted_at = NULL).
Yêu cầu JWT token.

Headers:
Authorization: Bearer <jwt_token>

Path Parameter:
customer_id: int

Response 200 OK:
{
"id": 1,
"full_name": "Nguyễn Văn A",
"phone_number": "0912345678",
...
"deleted_at": null
}

Response 401 Unauthorized:
{
"detail": "Token không hợp lệ"
}

Response 404 Not Found:
{
"detail": "Khách hàng không tìm thấy hoặc chưa bị xóa"
}
"""

# ============================================================================

# CURL EXAMPLES

# ============================================================================

"""

# 1. Tạo khách hàng vãng lai

curl -X POST http://localhost:8000/customers/walk-in \\
-H "Content-Type: application/json" \\
-d '{
"full_name": "Nguyễn Văn A",
"phone_number": "0912345678"
}'

# 2. Lấy khách hàng

curl http://localhost:8000/customers/1

# 3. Tìm kiếm khách hàng

curl "http://localhost:8000/customers?search_query=Nguyễn&page=1&per_page=20"

# 4. Cập nhật khách hàng (cần JWT token)

curl -X PUT http://localhost:8000/customers/1 \\
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \\
-H "Content-Type: application/json" \\
-d '{
"full_name": "Nguyễn Văn B",
"gender": "Nam"
}'

# 5. Xóa mềm khách hàng

curl -X DELETE http://localhost:8000/customers/1 \\
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

# 6. Khôi phục khách hàng

curl -X POST http://localhost:8000/customers/1/restore \\
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

# 7. Hoàn thiện hồ sơ

curl -X POST http://localhost:8000/customers/profile \\
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \\
-H "Content-Type: application/json" \\
-d '{
"full_name": "Nguyễn Văn A",
"phone_number": "0912345678"
}'

# 8. Lấy hồ sơ khách hàng của user hiện tại

curl http://localhost:8000/customers/me/profile \\
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

# 9. Bắt đầu liên kết tài khoản (gửi OTP)

curl -X POST http://localhost:8000/customers/link-account/initiate \\
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \\
-H "Content-Type: application/json" \\
-d '{
"phone_number": "0912345678"
}'

# 10. Xác minh OTP và hoàn tất liên kết

curl -X POST http://localhost:8000/customers/link-account/verify \\
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \\
-H "Content-Type: application/json" \\
-d '{
"phone_number": "0912345678",
"otp_code": "123456"
}'
"""

# ============================================================================

# PYTHON REQUESTS EXAMPLES

# ============================================================================

"""
import requests

BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIs..." # JWT token từ auth

# 1. Tạo khách hàng vãng lai

response = requests.post(
f"{BASE_URL}/customers/walk-in",
json={
"full_name": "Nguyễn Văn A",
"phone_number": "0912345678"
}
)
print(response.json())

# 2. Lấy khách hàng

response = requests.get(f"{BASE_URL}/customers/1")
print(response.json())

# 3. Tìm kiếm

response = requests.get(
f"{BASE_URL}/customers",
params={
"search_query": "Nguyễn",
"page": 1,
"per_page": 20
}
)
print(response.json())

# 4. Cập nhật khách hàng

response = requests.put(
f"{BASE_URL}/customers/1",
headers={"Authorization": f"Bearer {TOKEN}"},
json={
"full_name": "Nguyễn Văn B",
"gender": "Nam"
}
)
print(response.json())

# 5. Xóa mềm

response = requests.delete(
f"{BASE_URL}/customers/1",
headers={"Authorization": f"Bearer {TOKEN}"}
)
print(response.json())

# 6. Khôi phục

response = requests.post(
f"{BASE_URL}/customers/1/restore",
headers={"Authorization": f"Bearer {TOKEN}"}
)
print(response.json())
"""
