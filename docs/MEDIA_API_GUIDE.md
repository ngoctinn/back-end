# Hướng Dẫn Sử Dụng API Quản Lý Hình Ảnh (Media)

## 1. Giới Thiệu

Module Media cung cấp các API để tải lên, xóa và truy vấn hình ảnh, tích hợp với Supabase Storage để lưu trữ file và PostgreSQL để quản lý metadata.

## 2. Cài Đặt và Cấu Hình

### 2.1. Biến Môi Trường

Để module hoạt động, bạn cần cung cấp các biến môi trường sau trong file `.env` của dự án. Các giá trị này được lấy từ dashboard của dự án Supabase.

```dotenv
# .env

# ... các biến khác

# Supabase Settings
SUPABASE_URL="https://your-project-ref.supabase.co"
SUPABASE_KEY="your-public-anon-key"
SUPABASE_BUCKET_NAME="spa-images" # Hoặc tên bucket bạn đã tạo
```

### 2.2. Cài Đặt Thư Viện

Đảm bảo bạn đã cài đặt tất cả các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

### 2.3. Chạy Database Migration

Trước khi sử dụng, bạn cần chạy migration để tạo bảng `mediafile` trong cơ sở dữ liệu. Bảng này dùng để lưu thông tin metadata của ảnh.

```bash
# Chạy lệnh từ thư mục gốc của dự án
alembic upgrade head
```

Lệnh này sẽ áp dụng migration mới nhất, tạo bảng `mediafile` với các cột và chỉ mục cần thiết.

## 3. Hướng Dẫn Sử Dụng Các Endpoint

**Lưu ý:** Tất cả các endpoint yêu cầu xác thực bằng JWT Token. Vui lòng đính kèm `Authorization: Bearer <your_token>` trong header của mỗi request.

---

### 3.1. Tải Ảnh Đại Diện Cho Khách Hàng

- **Endpoint:** `POST /api/v1/media/upload/customer-avatar/{customer_id}`
- **Mô tả:** Tải lên ảnh đại diện cho một khách hàng cụ thể.
- **Parameters:**
  - `customer_id` (int, path): ID của khách hàng.
- **Request Body:** `multipart/form-data`
  - `file`: File ảnh cần tải lên.

**Ví dụ sử dụng `curl`:**

```bash
curl -X POST \
  http://localhost:8000/api/v1/media/upload/customer-avatar/123 \
  -H "Authorization: Bearer your_jwt_token" \
  -F "file=@/path/to/your/avatar.jpg"
```

**Phản hồi thành công (200 OK):**

```json
{
  "id": 1,
  "file_path": "customers/123/avatar_1665993600000.jpg",
  "public_url": "https://<project>.supabase.co/storage/v1/object/public/spa-images/customers/123/avatar_1665993600000.jpg",
  "file_type": "image/jpeg",
  "file_size": 204800,
  "related_entity_type": "customer",
  "related_entity_id": 123,
  "created_at": "2025-10-18T12:00:00Z"
}
```

**Các lỗi thường gặp:**
- `404 Not Found`: Khách hàng với `customer_id` không tồn tại.
- `413 Payload Too Large`: Kích thước file vượt quá giới hạn cho phép (mặc định 5MB).
- `400 Bad Request`: Loại file không được hỗ trợ.

---

### 3.2. Tải Ảnh Cho Dịch Vụ

- **Endpoint:** `POST /api/v1/media/upload/service-image/{service_id}`
- **Mô tả:** Tải lên ảnh minh họa cho một dịch vụ.
- **Parameters:**
  - `service_id` (int, path): ID của dịch vụ.
- **Request Body:** `multipart/form-data`
  - `file`: File ảnh cần tải lên.

**Ví dụ sử dụng `curl`:**

```bash
curl -X POST \
  http://localhost:8000/api/v1/media/upload/service-image/45 \
  -H "Authorization: Bearer your_jwt_token" \
  -F "file=@/path/to/your/service_image.png"
```

**Phản hồi thành công (200 OK):** (Tương tự như tải ảnh đại diện)

---

### 3.3. Xóa Một Ảnh

- **Endpoint:** `DELETE /api/v1/media/{media_id}`
- **Mô tả:** Xóa một file ảnh khỏi Supabase Storage và xóa record metadata khỏi CSDL.
- **Parameters:**
  - `media_id` (int, path): ID của record media (lấy từ phản hồi lúc tải lên).

**Ví dụ sử dụng `curl`:**

```bash
curl -X DELETE \
  http://localhost:8000/api/v1/media/1 \
  -H "Authorization: Bearer your_jwt_token"
```

**Phản hồi thành công (200 OK):**

```json
{
  "message": "Xóa ảnh thành công"
}
```

**Các lỗi thường gặp:**
- `404 Not Found`: Không tìm thấy ảnh với `media_id` đã cho.

---

### 3.4. Lấy Danh Sách Ảnh Của Một Đối Tượng

- **Endpoint:** `GET /api/v1/media/entity/{entity_type}/{entity_id}`
- **Mô tả:** Lấy danh sách tất cả các ảnh được liên kết với một đối tượng cụ thể (khách hàng, dịch vụ, nhân viên).
- **Parameters:**
  - `entity_type` (str, path): Loại đối tượng. Giá trị hợp lệ: `customer`, `service`, `staff`.
  - `entity_id` (int, path): ID của đối tượng.

**Ví dụ sử dụng `curl`:**

```bash
curl -X GET \
  http://localhost:8000/api/v1/media/entity/customer/123 \
  -H "Authorization: Bearer your_jwt_token"
```

**Phản hồi thành công (200 OK):**

```json
{
  "media_list": [
    {
      "id": 1,
      "file_path": "customers/123/avatar_1665993600000.jpg",
      "public_url": "https://...",
      "file_type": "image/jpeg",
      "file_size": 204800,
      "related_entity_type": "customer",
      "related_entity_id": 123,
      "created_at": "2025-10-18T12:00:00Z"
    }
    // ... các ảnh khác
  ]
}
```

**Các lỗi thường gặp:**
- `400 Bad Request`: `entity_type` không hợp lệ.
