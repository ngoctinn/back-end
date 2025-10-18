# 📸 HƯỚNG DẪN SỬ DỤNG MODULE QUẢN LÝ HÌNH ẢNH (MEDIA)

## ⚡ Quick Start

### 1. Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình Environment (.env)

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_public_key
SUPABASE_BUCKET_NAME=spa-images
```

### 3. Tạo Bucket trên Supabase

- Vào Supabase Console → Storage
- Click "Create new bucket"
- Name: `spa-images`
- Check "Public bucket"

### 4. Chạy Migration

```bash
alembic upgrade head
```

### 5. Chạy Ứng Dụng

```bash
uvicorn src.main:app --reload
```

---

## 🎯 EXAMPLES

### Tải ảnh đại diện khách hàng

**Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/media/upload/customer-avatar/1" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -F "file=@path/to/image.jpg"
```

**Response:**

```json
{
  "id": 1,
  "file_path": "customers/1/avatar_1697571600000.jpg",
  "public_url": "https://..../spa-images/customers/1/avatar_1697571600000.jpg",
  "file_type": "image/jpeg",
  "file_size": 204800,
  "related_entity_type": "customer",
  "related_entity_id": 1,
  "created_at": "2025-10-17T12:00:00"
}
```

### Tải ảnh dịch vụ

```bash
curl -X POST "http://localhost:8000/api/v1/media/upload/service-image/5" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -F "file=@path/to/service.jpg"
```

### Lấy danh sách ảnh

```bash
curl -X GET "http://localhost:8000/api/v1/media/entity/customer/1" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Response:**

```json
{
  "media_list": [
    {
      "id": 1,
      "file_path": "customers/1/avatar_1697571600000.jpg",
      "public_url": "https://...",
      "file_type": "image/jpeg",
      "file_size": 204800,
      "related_entity_type": "customer",
      "related_entity_id": 1,
      "created_at": "2025-10-17T12:00:00"
    }
  ]
}
```

### Xóa ảnh

```bash
curl -X DELETE "http://localhost:8000/api/v1/media/1" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Response:**

```json
{
  "message": "Xóa ảnh thành công"
}
```

---

## 📚 SWAGGER UI

Truy cập tại: `http://localhost:8000/docs`

Tất cả endpoint được tự động sinh ra trong Swagger UI.

---

## 🔧 CẤU HÌNH

### Thay đổi Kích Thước File Tối Đa

Mở `src/modules/media/service.py` và sửa:

```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

### Hỗ Trợ Loại File Khác

```python
# Mở src/modules/media/service.py
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/bmp",
    # Thêm loại mới tại đây
}
```

---

## 🧪 TESTING

```bash
# Chạy test media
pytest tests/test_media.py -v

# Chạy tất cả test media
pytest tests/test_media*.py -v

# Chạy với coverage
pytest tests/test_media.py --cov=src.modules.media
```

---

## 🐛 TROUBLESHOOTING

### Lỗi: "Form data requires 'python-multipart'"

```bash
pip install python-multipart
```

### Lỗi: "Supabase connection failed"

- Kiểm tra `SUPABASE_URL` và `SUPABASE_KEY` trong `.env`
- Kiểm tra kết nối internet

### Lỗi: "Bucket not found"

- Kiểm tra tên bucket: `SUPABASE_BUCKET_NAME`
- Kiểm tra bucket công khai hay không

---

## 📂 CẤU TRÚC THƯ MỤC

```
src/modules/media/
├── __init__.py          # Package
├── models.py            # SQLModel (MediaFile)
├── schemas.py           # Pydantic (Request/Response)
├── crud.py              # Database Operations
├── service.py           # Business Logic
└── router.py            # API Endpoints

src/core/
└── storage.py           # Supabase Operations
```

---

## 🚀 PRODUCTION NOTES

1. Sử dụng environment production cho Supabase
2. Tăng `MAX_FILE_SIZE` nếu cần
3. Bật logging cho debugging
4. Cấu hình CORS nếu frontend khác domain
5. Sử dụng HTTPS cho production

---

## 📞 SUPPORT

Để báo cáo lỗi hoặc yêu cầu tính năng:

- Kiểm tra logs: Xem `service.py` và `storage.py`
- Chạy test: `pytest tests/test_media.py -v`
- Kiểm tra database: Các records trong bảng `mediafile`

---

**Module Media v1.0** ✨  
Ready for Production 🚀
