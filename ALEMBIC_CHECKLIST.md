# ✅ Alembic Configuration Checklist

## 📋 Danh Sách Kiểm Tra Cấu Hình

### Phase 1: Setup Ban Đầu

- [ ] Đã đọc `docs/ALEMBIC_SETUP_COMPLETE.md`
- [ ] File `.env` chứa `DATABASE_URL`
- [ ] Chạy được lệnh: `alembic --version`
- [ ] Chạy được lệnh: `alembic current`

### Phase 2: Tạo Migration Ban Đầu

- [ ] Chạy: `alembic revision --autogenerate -m "create initial tables"`
- [ ] Kiểm tra file được tạo trong `alembic/versions/`
- [ ] File migration chứa SQL được sinh từ models
- [ ] Chạy: `alembic upgrade head`
- [ ] Database schema được tạo thành công

### Phase 3: Testing

- [ ] Chạy: `alembic current` → Xem revision hiện tại
- [ ] Chạy: `alembic history` → Xem lịch sử
- [ ] Chạy: `alembic downgrade -1` → Hoàn tác
- [ ] Chạy: `alembic upgrade head` → Nâng cấp lại

### Phase 4: Thêm Module Mới

- [ ] Tạo folder `src/modules/{new_module}/`
- [ ] Tạo file `models.py` với SQLModel
- [ ] **Thêm import vào `alembic/env.py`**:
  ```python
  from src.modules.{new_module}.models import YourModel
  ```
- [ ] Chạy: `alembic revision --autogenerate -m "add your table"`
- [ ] Kiểm tra migration file
- [ ] Chạy: `alembic upgrade head`

### Phase 5: Git Workflow

- [ ] Commit migration files: `git add alembic/versions/`
- [ ] Không bao giờ xóa migration files cũ
- [ ] Không chỉnh sửa migration files đã commit

## 🔍 Verification Commands

```bash
# Kiểm tra Alembic đã cài
alembic --version

# Kiểm tra cấu hình đúng
alembic current

# Xem tất cả migrations
alembic history

# Xem SQL sẽ được chạy
alembic upgrade head --sql

# Xem heads (nhánh cuối)
alembic heads

# Xem branches
alembic branches
```

## 🚨 Common Mistakes to Avoid

❌ **Lỗi 1:** Quên import model mới trong `alembic/env.py`

- **Kết quả:** "No changes detected"
- **Cách khắc:** Kiểm tra `alembic/env.py` dòng import models

❌ **Lỗi 2:** Chỉnh sửa migration file sau khi đã áp dụng

- **Kết quả:** Không match giữa code và database
- **Cách khắc:** Tạo migration mới để fix lỗi

❌ **Lỗi 3:** Không commit migration files

- **Kết quả:** Khác giữa dev và production
- **Cách khắc:** Luôn `git add` file migration

❌ **Lỗi 4:** Xóa migration files cũ

- **Kết quả:** Mất lịch sử, không thể rollback
- **Cách khắc:** Bất kỳ khi nào cũng giữ nguyên

## 📊 Migration File Structure

```
alembic/versions/
├── 20250116_143022_a1b2c3d_create_user_table.py
│   ├── up(): Thay đổi khi upgrade
│   └── down(): Thay đổi khi downgrade
│
├── 20250116_150030_x9y8z7w_add_phone_to_user.py
│
└── 20250116_152145_m5n4o3p_create_appointment_table.py
```

## 🎯 Ideal Workflow

```
1. Thay đổi Model
   ↓
2. alembic revision --autogenerate
   ↓
3. Kiểm tra file migration (alembic/versions/)
   ↓
4. alembic upgrade head
   ↓
5. Test ứng dụng
   ↓
6. git add + commit
   ↓
7. Push lên repo
```

## 📞 Need Help?

- **Tài liệu chi tiết:** `docs/ALEMBIC_CONFIG.md`
- **Lệnh nhanh:** `docs/ALEMBIC_QUICK_START.md`
- **Official:** https://alembic.sqlalchemy.org/

---

✅ **Khi tất cả checkboxes được check, bạn đã sẵn sàng!**
