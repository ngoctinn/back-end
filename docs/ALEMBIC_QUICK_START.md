# 🚀 Quick Start - Alembic Commands

## 📋 Danh Sách Lệnh Nhanh

### 1. Tạo Migration Tự Động (Phổ Biến Nhất)

```bash
alembic revision --autogenerate -m "add user table"
```

✅ Dùng khi: Vừa thay đổi model và muốn Alembic tự sinh SQL

### 2. Áp Dụng Migration (Nâng Cấp DB)

```bash
alembic upgrade head
```

✅ Dùng để: Chạy tất cả migration chưa áp dụng lên database

### 3. Hoàn Tác Migration (Giảm Cấp DB)

```bash
alembic downgrade -1
```

✅ Dùng để: Quay lại trạng thái trước migration cuối cùng

### 4. Xem Lịch Sử Migration

```bash
alembic history
```

✅ Để biết: Tất cả các migration đã tạo

### 5. Kiểm Tra Trạng Thái Hiện Tại

```bash
alembic current
```

✅ Để biết: Database đang ở revision nào

---

## 📝 Quy Trình Điển Hình

### Thêm Model Mới

1. **Tạo file model** → `src/modules/customers/models.py`
2. **Import model trong `alembic/env.py`:**
   ```python
   from src.modules.customers.models import Customer
   ```
3. **Tạo migration:**
   ```bash
   alembic revision --autogenerate -m "add customer table"
   ```
4. **Kiểm tra file migration** → `alembic/versions/...`
5. **Áp dụng:**
   ```bash
   alembic upgrade head
   ```
6. **Commit:** `git add alembic/versions/...`

### Sửa Model Hiện Tại

1. **Chỉnh sửa model** → thêm/xóa field
2. **Tạo migration:**
   ```bash
   alembic revision --autogenerate -m "add phone to user"
   ```
3. **Áp dụng:**
   ```bash
   alembic upgrade head
   ```

---

## ⚡ Tips Hữu Ích

### Xem chi tiết migration trước khi áp dụng

```bash
# Xem SQL sẽ được chạy
alembic upgrade head --sql
```

### Áp dụng migration lên một revision cụ thể

```bash
alembic upgrade abc1234  # abc1234 là revision ID
```

### Hoàn tác toàn bộ về ban đầu

```bash
alembic downgrade base
```

---

## ⚠️ Lỗi Thường Gặp

| Lỗi                            | Nguyên Nhân                                  | Giải Pháp                         |
| ------------------------------ | -------------------------------------------- | --------------------------------- |
| "No changes detected"          | Model chưa import trong env.py               | Thêm import vào `alembic/env.py`  |
| "ModuleNotFoundError: src"     | Đường dẫn sys.path không đúng                | Đã được cấu hình sẵn trong env.py |
| "sqlalchemy.exc.ArgumentError" | Database URL sai hoặc database không tồn tại | Kiểm tra `.env` và DATABASE_URL   |

---

📖 **Tài liệu chi tiết:** Xem `docs/ALEMBIC_CONFIG.md`
