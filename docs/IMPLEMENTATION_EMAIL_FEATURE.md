# Triển Khai Tính Năng: Gửi Mail Xác Nhận Đăng Ký và Quên Mật khẩu

Tài liệu này mô tả quá trình triển khai tính năng gửi email xác minh cho đăng ký tài khoản mới và khôi phục mật khẩu quên.

## Các Tệp Đã Tạo/Sửa Đổi

### 1. **Tạo mới: `src/core/email.py`**

Module xử lý gửi email thông qua SMTP.

**Các hàm chính:**

- `send_email_async(to_email, subject, html_content) -> bool`: Gửi email không đồng bộ
- `send_verification_email(email, token) -> bool`: Gửi email xác minh đăng ký
- `send_password_reset_email(email, token) -> bool`: Gửi email đặt lại mật khẩu
- `_get_verification_email_template()`: HTML template cho email xác minh
- `_get_password_reset_email_template()`: HTML template cho email reset password

**Đặc điểm:**

- Template HTML có styling chuyên nghiệp
- Gửi qua SMTP với hỗ trợ SSL/TLS
- Xử lý lỗi mà không expose chi tiết SMTP

### 2. **Cập nhật: `src/core/config.py`**

Thêm các setting token expiry:

- `VERIFICATION_TOKEN_EXPIRE_HOURS`: Thời gian hết hạn token verify email (mặc định: 24 giờ)
- `RESET_TOKEN_EXPIRE_HOURS`: Thời gian hết hạn token reset password (mặc định: 1 giờ)

### 3. **Cập nhật: `src/modules/auth/models.py`**

Thêm cột `expires_at` cho các bảng:

- `VerificationToken.expires_at`: Thời điểm hết hạn token xác minh
- `ResetPasswordToken.expires_at`: Thời điểm hết hạn token reset

### 4. **Cập nhật: `src/modules/auth/crud.py`**

Cập nhật các hàm CRUD:

- `create_verification_token(db, user_id, token, expires_at)`: Tạo token xác minh với hạn hết
- `create_reset_token(db, user_id, token, expires_at)`: Tạo token reset với hạn hết
- `delete_expired_tokens(db)`: Xóa tất cả token hết hạn (trả về số lượng xóa)

Các hàm khác cũ vẫn giữ nguyên với docstring cải tiến.

### 5. **Cập nhật: `src/modules/auth/service.py`**

Triển khai logic hoàn chỉnh:

**Hàm mới:**

- `register_user(db, email, password)`: Đăng ký + tạo token xác minh + gửi email
- `initiate_email_verification(db, user_id)`: Khởi tạo lại email verification (gửi lại email)
- `confirm_email(db, token)`: Xác minh email từ token
- `initiate_password_reset(db, email)`: Tạo reset token + gửi email (chống enumeration)
- `confirm_password_reset(db, token, new_password)`: Đặt lại password từ token + revoke refresh tokens

**Hàm cũ:**

- `hash_password()`, `verify_password()`: Wrapper cho core.security
- `create_access_token_for_user()`, `login_user()`, etc.: Giữ nguyên từ plan 0001

**Tính năng bảo mật:**

- Token xác minh: TTL 24 giờ
- Token reset: TTL 1 giờ
- Delay ngẫu nhiên (1-2s) khi email không tồn tại (chống enumeration)
- Revoke tất cả refresh tokens cũ khi đặt lại password

### 6. **Cập nhật: `src/modules/auth/schemas.py`**

Thêm các schema mới:

- `VerifyEmailRequest`: Nhận token xác minh
- `ResendVerificationEmailRequest`: Placeholder cho resend email
- `PasswordResetRequest`: Nhận email để reset password
- `ConfirmPasswordResetRequest`: Nhận token + password mới
- `MessageResponse`: Response generic cho thông báo

### 7. **Cập nhật: `src/modules/auth/router.py`**

Thêm các endpoints mới:

- `POST /auth/register`: Đăng ký + gửi email xác minh
- `POST /auth/verify-email`: Xác minh email từ token
- `POST /auth/resend-verification-email`: Gửi lại email xác minh (placeholder)
- `POST /auth/password-reset`: Yêu cầu reset password (gửi email)
- `POST /auth/confirm-password-reset`: Xác nhận reset password (đặt password mới)

Các endpoint cũ:

- `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`: Giữ nguyên

### 8. **Tạo mới: `alembic/versions/20251016_add_email_tokens.py`**

Migration Alembic để thêm cột `expires_at`:

- Thêm cột vào `verificationtoken`
- Thêm cột vào `resetpasswordtoken`
- Tạo index cho `expires_at`

### 9. **Tạo mới: `src/core/background_tasks.py`**

Background task để xóa token hết hạn:

- `cleanup_expired_tokens()`: Gọi `crud.delete_expired_tokens()` và log kết quả

Có thể schedule với APScheduler hoặc Celery.

## Luồng Sử Dụng

### Luồng 1: Đăng ký + Xác minh Email

1. **Client POST `/auth/register`** với `email` và `password`
2. Backend:
   - Validate input
   - Hash password
   - Tạo user với `is_active = False`
   - Tạo token xác minh (UUID 32 byte)
   - Lưu token với `expires_at = now + 24h`
   - Gửi email HTML chứa link: `https://frontend/auth/verify-email?token=...`
   - Return success message
3. **Client GET/POST `/auth/verify-email`** với token từ email link
4. Backend:
   - Kiểm tra token tồn tại
   - Kiểm tra token chưa hết hạn (`expires_at > now`)
   - Update user: `is_active = True`
   - Xóa token
   - Return success
5. **Client có thể POST `/auth/login`** (tài khoản đã active)

### Luồng 2: Quên Mật khẩu + Reset

1. **Client POST `/auth/password-reset`** với `email`
2. Backend:
   - Query user theo email
   - Nếu user tồn tại:
     - Tạo reset token (UUID 32 byte)
     - Lưu token với `expires_at = now + 1h`
     - Gửi email HTML chứa link: `https://frontend/auth/reset-password?token=...`
   - Nếu email không tồn tại: Delay 1-2s (chống enumeration)
   - Luôn return: "Nếu email tồn tại, email được gửi"
3. **Client POST `/auth/confirm-password-reset`** với `token` và `new_password`
4. Backend:
   - Kiểm tra token tồn tại
   - Kiểm tra token chưa hết hạn
   - Hash password mới
   - Update user: `password_hash = new_hash`
   - Revoke tất cả refresh tokens cũ
   - Xóa reset token
   - Return success
5. **Client phải POST `/auth/login`** lại với password mới

## Cấu Hình SMTP

Cần thêm vào file `.env`:

```
# Mail settings
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@spa-crm.local
MAIL_STARTTLS=true
MAIL_SSL_TLS=false

# Token expiry (giờ)
VERIFICATION_TOKEN_EXPIRE_HOURS=24
RESET_TOKEN_EXPIRE_HOURS=1
```

**Lưu ý:**

- Gmail: Dùng App Password, không phải password thường
- Hotmail: Dùng SMTP cấu hình tương tự
- AWS SES: Cầu hình khác, cần update email.py
- Mailgun, SendGrid: Dùng API wrapper khác

## Chạy Migration

```bash
# Cập nhật cơ sở dữ liệu
alembic upgrade head

# Xóa cột (nếu cần rollback)
alembic downgrade -1
```

## Chạy Background Task

**Tuỳ chọn 1: APScheduler (đơn giản)**

```python
# src/main.py
from apscheduler.schedulers.background import BackgroundScheduler
from src.core.background_tasks import cleanup_expired_tokens

scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_expired_tokens, 'interval', hours=1)  # Chạy mỗi giờ
scheduler.start()
```

**Tuỳ chọn 2: Celery (distributed)**

```python
# src/tasks.py
from celery import Celery
from src.core.background_tasks import cleanup_expired_tokens

app = Celery('spa_crm')

@app.task
def cleanup_task():
    cleanup_expired_tokens()

# Chạy: celery -A src.tasks worker --beat
```

## Testing

```bash
# 1. Đăng ký
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123"}'

# Response:
# {"message": "Đăng ký thành công. Vui lòng xác minh email", "email": "test@example.com"}

# 2. Xác minh email (dùng token từ email)
curl -X POST http://localhost:8000/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{"token":"<token-from-email>"}'

# 3. Đăng nhập
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123"}'

# 4. Quên mật khẩu
curl -X POST http://localhost:8000/auth/password-reset \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'

# 5. Confirm reset password
curl -X POST http://localhost:8000/auth/confirm-password-reset \
  -H "Content-Type: application/json" \
  -d '{"token":"<token-from-email>","new_password":"NewPass123"}'
```

## Ghi Chú Bảo Mật

1. **Token độ dài:** 32 byte (256 bit) đủ an toàn
2. **Token storage:** Không hash token trong DB (chỉ lưu plain text, vì TTL ngắn)
3. **Timing attack:** SMTP delay ngẫu nhiên chống enumeration
4. **Password hashing:** Dùng bcrypt từ core.security
5. **Session revoke:** Revoke tất cả refresh tokens khi reset password
6. **HTTPS:** Bắt buộc dùng HTTPS trong production
7. **CORS:** Cấu hình CORS chặt chẽ để chỉ FE được phép

## Tiếp Theo (TODO)

- [ ] Thêm rate limiting cho endpoints email
- [ ] Thêm dependency `get_current_user` để enable endpoint resend email
- [ ] Tích hợp APScheduler hoặc Celery cho background task
- [ ] Thêm logging chi tiết cho audit trail
- [ ] Test email templates trên nhiều email client
- [ ] Implement email preview endpoint (dev mode)
