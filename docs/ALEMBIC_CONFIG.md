# 📋 Hướng Dẫn Cấu Hình Alembic cho Dự Án FastAPI

## 📌 Tổng Quan

**Alembic** là công cụ quản lý database migrations cho SQLAlchemy/SQLModel. Nó cho phép:

- ✅ Tạo schema mới từ models Python
- ✅ Tạo migration tự động từ thay đổi models
- ✅ Quản lý lịch sử thay đổi database
- ✅ Rollback các thay đổi nếu cần

## 🏗️ Cấu Trúc Thư Mục

```
alembic/
├── env.py                # Môi trường migration (cấu hình quan trọng)
├── script.py.mako       # Template để tạo file migration
├── versions/            # Các file migration được tạo ra
└── README               # Hướng dẫn Alembic

alembic.ini             # File cấu hình Alembic chính
```

## ⚙️ Các Tệp Được Cấu Hình

### 1. **alembic.ini** - File Cấu Hình Chính

**Các thiết lập quan trọng:**

```ini
# Vị trí script migration
script_location = %(here)s/alembic

# Định dạng tên file migration (có timestamp)
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d%%(second).2d_%%(rev)s_%%(slug)s

# Database URL (sẽ được override từ .env)
sqlalchemy.url =
```

**Lợi ích của định dạng timestamp:**

- Dễ dàng theo dõi thứ tự migration
- Tránh conflict khi nhiều dev làm việc song song
- Tên file: `20250116_143022_abc1234_create_initial_tables.py`

### 2. **alembic/env.py** - Cấu Hình Môi Trường Migration

**Các phần quan trọng:**

#### a) Import Models

```python
# Import tất cả models để Alembic phát hiện
from src.modules.auth.models import User, RefreshToken, VerificationToken, ResetPasswordToken
```

⚠️ **Quan trọng:** Khi thêm module mới, phải thêm import ở đây để Alembic tìm thấy model mới!

#### b) Đặt Target Metadata

```python
target_metadata = SQLModel.metadata
```

Dùng `SQLModel.metadata` để Alembic biết toàn bộ schema của ứng dụng.

#### c) Cấu Hình Database URL

```python
configuration["sqlalchemy.url"] = settings.DATABASE_URL
```

Lấy URL từ `settings` (file `.env`), không cứng mã vào file.

#### d) Các Option Autogenerate

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    compare_type=True,  # So sánh kiểu dữ liệu (int vs bigint)
    compare_server_default=True,  # So sánh giá trị mặc định server
)
```

## 🚀 Cách Sử Dụng

### 1️⃣ **Tạo Migration Tự Động** (khi có thay đổi models)

```bash
alembic revision --autogenerate -m "mô tả ngắn gọn"
```

**Ví dụ:**

```bash
alembic revision --autogenerate -m "add user table"
alembic revision --autogenerate -m "add email index to users"
```

**Kết quả:**

```
Tạo file mới: alembic/versions/20250116_143022_abc1234_add_user_table.py
```

### 2️⃣ **Tạo Migration Trống** (cần viết SQL thủ công)

```bash
alembic revision -m "mô tả"
```

**Khi nào dùng:** Khi muốn viết SQL phức tạp không thể autogenerate.

### 3️⃣ **Áp Dụng Migration (Nâng Cấp)**

```bash
# Áp dụng tất cả migration chưa áp dụng
alembic upgrade head

# Áp dụng lên revision cụ thể
alembic upgrade abc1234

# Áp dụng một số revision nhất định
alembic upgrade +2
```

### 4️⃣ **Hoàn Tác Migration (Giảm Cấp)**

```bash
# Hoàn tác 1 migration
alembic downgrade -1

# Hoàn tác toàn bộ về trạng thái ban đầu
alembic downgrade base

# Hoàn tác về revision cụ thể
alembic downgrade abc1234
```

### 5️⃣ **Kiểm Tra Trạng Thái**

```bash
# Xem lịch sử migration
alembic history

# Xem revision hiện tại
alembic current

# So sánh schema hiện tại với target
alembic heads
```

## 📝 Quy Trình Phát Triển

### Khi Thêm Module Mới

1. **Tạo file models mới** (ví dụ: `src/modules/customers/models.py`)

2. **Cập nhật `alembic/env.py`** - Thêm import:

   ```python
   from src.modules.customers.models import Customer  # Thêm dòng này
   ```

3. **Tạo migration:**

   ```bash
   alembic revision --autogenerate -m "add customer table"
   ```

4. **Kiểm tra file migration** được tạo ra (`alembic/versions/...`)

5. **Áp dụng migration:**
   ```bash
   alembic upgrade head
   ```

### Khi Chỉnh Sửa Model Hiện Tại

1. **Thay đổi model** trong `src/modules/{module}/models.py`

2. **Tạo migration:**

   ```bash
   alembic revision --autogenerate -m "add phone field to user"
   ```

3. **Kiểm tra migration** có đúng không

4. **Áp dụng:**
   ```bash
   alembic upgrade head
   ```

## ⚠️ Các Lỗi Thường Gặp

### ❌ Lỗi 1: "No changes detected"

**Nguyên nhân:** Model chưa được import trong `env.py`

**Giải pháp:**

```python
# Thêm vào alembic/env.py
from src.modules.your_module.models import YourModel
```

### ❌ Lỗi 2: "ModuleNotFoundError: No module named 'src'"

**Nguyên nhân:** Đường dẫn sys.path chưa được thiết lập

**Giải pháp:** (Đã được cấu hình trong env.py)

```python
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### ❌ Lỗi 3: "Database URL not configured"

**Nguyên nhân:** `settings.DATABASE_URL` không có giá trị

**Giải pháp:**

- Kiểm tra file `.env` có chứa `DATABASE_URL` không
- Kiểm tra `.env` được load đúng trong `config.py`

## 🔄 Workflow Với Git

1. **Tạo migration** → File `.py` mới trong `alembic/versions/`
2. **Commit file migration** → Phải commit vào repo
3. **Deploy:** Chạy `alembic upgrade head` trên server

⚠️ **Không bao giờ xóa file migration cũ!** Chúng lưu lịch sử thay đổi.

## 📚 Ví Dụ Hoàn Chỉnh

### Tình Huống: Thêm Trường `phone_number` cho User

**Bước 1:** Chỉnh sửa model

```python
# src/modules/auth/models.py
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)
    phone_number: str = Field(nullable=True)  # ← Thêm trường này
```

**Bước 2:** Tạo migration

```bash
alembic revision --autogenerate -m "add phone_number to user"
```

**Bước 3:** Xem file migration được tạo (auto-generated)

```python
# alembic/versions/20250116_143022_abc1234_add_phone_number_to_user.py
def upgrade() -> None:
    op.add_column('user', sa.Column('phone_number', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('user', 'phone_number')
```

**Bước 4:** Áp dụng migration

```bash
alembic upgrade head
```

**Bước 5:** Commit vào repo

```bash
git add alembic/versions/20250116_143022_abc1234_add_phone_number_to_user.py
git commit -m "migration: add phone_number to user"
```

## 🎯 Checklist Before Going Live

- ✅ Tất cả models được import trong `alembic/env.py`
- ✅ File `.env` chứa `DATABASE_URL` đúng
- ✅ Chạy `alembic upgrade head` thành công
- ✅ Kiểm tra schema database khớp với models
- ✅ Tất cả migration files được commit vào repo

---

**📖 Tài liệu tham khảo:** https://alembic.sqlalchemy.org/
