# Spa Customer Care Platform - Backend (skeleton)

Tài liệu này mô tả cấu trúc thư mục khởi tạo dự án.

Nội dung chính:

- `src/` : mã nguồn ứng dụng
- `src/core/` : cấu hình, security, dependencies chung
- `src/modules/` : từng module/domain (auth, customers, services, appointments, staff)
- `tests/` : unit tests cơ bản

Các bước khởi động cơ bản (local):

1. Tạo virtualenv và cài deps từ `requirements.txt`.
2. Sao chép `.env.example` -> `.env` và cập nhật biến môi trường.
3. Chạy server (sau khi cấu hình):

   uvicorn src.main:app --reload

Lưu ý: hiện tại repo chỉ là skeleton (chỉ chứa file init và đặt chỗ). Không có logic nghiệp vụ.
