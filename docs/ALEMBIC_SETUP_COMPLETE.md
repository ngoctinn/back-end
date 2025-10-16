# 📋 Setup Hướng Dẫn - Alembic Configuration

## ✅ Những Gì Được Cấu Hình

Dự án FastAPI của bạn đã được cấu hình hoàn toàn với **Alembic** cho quản lý database migrations. Dưới đây là tổng kết các thay đổi:

### 1. **alembic.ini** - Cấu Hình Chính

- ✅ Đặt `script_location` → `alembic/`
- ✅ Cấu hình `file_template` với timestamp (YYYYMMDD_HHMMSS_REV_MESSAGE)
- ✅ Để `sqlalchemy.url` trống (sẽ load từ `.env`)

### 2. **alembic/env.py** - Môi Trường Migration

- ✅ Import `settings` từ `src.core.config`
- ✅ Import tất cả models từ các modules (hiện tại: `auth`)
- ✅ Thiết lập `target_metadata = SQLModel.metadata`
- ✅ Cấu hình để load `DATABASE_URL` từ `.env`
- ✅ Bật `compare_type=True` và `compare_server_default=True` để autogenerate chính xác

### 3. **Documentation**

- ✅ `docs/ALEMBIC_CONFIG.md` - Hướng dẫn chi tiết
- ✅ `docs/ALEMBIC_QUICK_START.md` - Danh sách lệnh nhanh

### 4. **Helper Script**

- ✅ `scripts/alembic_helper.sh` - Script hỗ trợ các lệnh Alembic

---

## 🚀 Cách Sử Dụng Ngay

### Bước 1: Kiểm Tra `.env` File

Đảm bảo file `.env` có chứa `DATABASE_URL`:

```env
# Ví dụ cho PostgreSQL (Supabase)
DATABASE_URL=postgresql://user:password@host:5432/database

# Ví dụ cho SQLite (development)
DATABASE_URL=sqlite:///./app.db
```

### Bước 2: Tạo Migration Ban Đầu

```bash
cd e:\Projects\KLTN\back-end
alembic revision --autogenerate -m "create initial tables"
```

**Kết quả:** Tạo file mới trong `alembic/versions/` với SQL autogenerate

### Bước 3: Áp Dụng Migration

```bash
alembic upgrade head
```

**Kết quả:** Schema database được tạo từ models Python

---

## ⚠️ Quan Trọng: Khi Thêm Module/Model Mới

**Mỗi lần thêm module mới, PHẢI cập nhật `alembic/env.py`:**

```python
# Ví dụ: Thêm module customers
from src.modules.customers.models import Customer, CustomerNote

# Nếu thêm module appointments
from src.modules.appointments.models import Appointment
```

❌ **Nếu quên:** Alembic sẽ không tìm thấy model mới → "No changes detected"

---

## 📝 Workflow Khi Phát Triển

### Sơ Đồ Quy Trình

```
Thay đổi Model (.py)
        ↓
alembic revision --autogenerate
        ↓
Kiểm tra file migration (alembic/versions/)
        ↓
alembic upgrade head
        ↓
Test ứng dụng
        ↓
git add & commit
```

### Ví Dụ Cụ Thể

**Tình huống:** Thêm trường `phone_number` vào User

```bash
# 1. Sửa model
# src/modules/auth/models.py
# class User: phone_number: str = Field(nullable=True)

# 2. Tạo migration
alembic revision --autogenerate -m "add phone_number to user"

# 3. Kiểm tra file được tạo (optional)
# alembic/versions/20250116_143022_abc123_add_phone_number_to_user.py

# 4. Áp dụng
alembic upgrade head

# 5. Commit
git add alembic/versions/20250116_143022_abc123_add_phone_number_to_user.py
git commit -m "migration: add phone_number to user"
```

---

## 🔍 Troubleshooting

### ❌ Lỗi: "No changes detected"

```
Nguyên nhân: Model chưa được import trong alembic/env.py
Giải pháp: Thêm import trong alembic/env.py
```

### ❌ Lỗi: "sqlalchemy.exc.ArgumentError"

```
Nguyên nhân: DATABASE_URL không được đặt hoặc database không tồn tại
Giải pháp: Kiểm tra .env file và tạo database
```

### ❌ Lỗi: "ModuleNotFoundError: No module named 'src'"

```
Nguyên nhân: Đường dẫn sys.path chưa được thiết lập
Giải pháp: (Đã được xử lý trong env.py)
```

---

## 📚 Tài Liệu Tham Khảo

- **Chi tiết:** `docs/ALEMBIC_CONFIG.md`
- **Lệnh nhanh:** `docs/ALEMBIC_QUICK_START.md`
- **Official Docs:** https://alembic.sqlalchemy.org/

---

## ✅ Checklist Trước Khi Deploy

- [ ] Tất cả models được import trong `alembic/env.py`
- [ ] File `.env` chứa `DATABASE_URL` đúng
- [ ] Chạy `alembic upgrade head` thành công
- [ ] Kiểm tra schema database
- [ ] Tất cả migration files được commit

---

🎉 **Alembic đã được cấu hình xong!**

Bây giờ bạn có thể:
✅ Tạo models mới
✅ Tự động sinh migrations
✅ Quản lý schema database
✅ Tracking lịch sử thay đổi
