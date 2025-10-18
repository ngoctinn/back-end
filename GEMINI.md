# HƯỚNG DẪN DÀNH CHO GEMINI

Tài liệu này là kim chỉ nam để Gemini hỗ trợ phát triển dự án back-end cho **Hệ thống CSKH Trực Tuyến Spa (CMS)**. Vui lòng tuân thủ nghiêm ngặt các quy tắc dưới đây.

## 1. Bối Cảnh & Mục Tiêu Dự Án

- **Dự án:** Xây dựng API cho hệ thống Quản lý Quan hệ Khách hàng (CRM) và đặt lịch cho một Spa.
- **Mục tiêu của Gemini:** Hỗ trợ viết code, refactor, tạo tài liệu, và thực hiện các tác vụ lập trình khác theo các tiêu chuẩn đã định.

## 2. Công Nghệ & Kiến Trúc

Dự án được xây dựng trên một ngăn xếp công nghệ hiện đại và theo kiến trúc module hóa để dễ dàng bảo trì và mở rộng.

### 2.1. Công Nghệ Sử Dụng

- **Ngôn ngữ:** Python 3.13.7
- **Framework:** FastAPI
- **ORM:** SQLModel (tương tác với PostgreSQL)
- **Validation:** Pydantic
- **Database Migration:** Alembic
- **Authentication:** JWT (PyJWT)
- **Server:** Uvicorn
- **Testing:** Pytest

### 2.2. Kiến Trúc Module (Domain-Driven)

Dự án được tổ chức theo các **module nghiệp vụ (domain)** độc lập nằm trong `src/modules/`.

- **Cấu trúc tổng thể:**
  ```
  spa_online_crm/
  ├── src/
  │ ├── main.py           # Entrypoint, gắn kết các router
  │ ├── core/             # Các thành phần dùng chung (config, db, security)
  │ ├── modules/          # Chứa các domain nghiệp vụ
  │ │ ├── auth/
  │ │ ├── customers/
  │ │ ├── services/
  │ │ ├── appointments/
  │ │ └── staff/
  │ └── tests/            # Kiểm thử, có cấu trúc tương ứng modules
  ├── .env
  └── requirements.txt
  ```

- **Cấu trúc bên trong mỗi module:** Mỗi module (`src/modules/{domain}/`) phải tuân thủ cấu trúc sau để đảm bảo tính đóng gói:
  - `router.py`: Định nghĩa API endpoints (APIRouter).
  - `schemas.py`: Định nghĩa Pydantic models cho request/response (DTOs).
  - `models.py`: Định nghĩa models cho database (SQLModel).
  - `service.py`: Chứa logic nghiệp vụ phức tạp, điều phối hoạt động.
  - `crud.py`: Chứa các hàm truy cập dữ liệu trực tiếp (Create, Read, Update, Delete).

## 3. Tiêu Chuẩn Viết Code

**Ưu tiên hàng đầu:** Code phải **sạch, dễ đọc, và tự giải thích**.

### 3.1. Nguyên Tắc Clean Code

| Quy Tắc | Yêu Cầu Chi Tiết |
| :--- | :--- |
| **Tên Rõ Ràng** | Tên biến, hàm, lớp phải mô tả rõ mục đích. (Ví dụ: `get_customer_by_phone` thay vì `get_cust`). |
| **Hàm Ngắn Gọn (SRP)** | Mỗi hàm chỉ thực hiện **một việc duy nhất**. |
| **Không Lặp Lại (DRY)** | Tái sử dụng logic qua hàm, lớp, hoặc module. |
| **Xử Lý Lỗi** | Xử lý lỗi một cách tường minh, tránh trả về `None` một cách không rõ ràng. |
| **Định Dạng Nhất Quán** | Luôn tuân thủ định dạng code của dự án. |

### 3.2. Quy Tắc Python (PEP 8)

**BẮT BUỘC** tuân thủ nghiêm ngặt PEP 8:

- **Thụt lề:** **4 khoảng trắng**.
- **Độ dài dòng:** Tối đa **79 ký tự**.
- **Quy tắc đặt tên:**
  - `snake_case` cho biến, hàm.
  - `CapWords` (PascalCase) cho lớp.
  - `CAPS_SNAKE_CASE` cho hằng số.
- **Imports:** Sắp xếp theo thứ tự: thư viện chuẩn > bên thứ ba > cục bộ. Mỗi import trên một dòng.

### 3.3. Quy Tắc Comment (Tiếng Việt)

**Mục tiêu:** Comment để giải thích "tại sao", không phải "cái gì".

| Loại Comment | Yêu Cầu (Bằng Tiếng Việt) |
| :--- | :--- |
| **Docstring** | Mô tả **chức năng, tham số (Params), và giá trị trả về (Return)** cho hàm/lớp public. |
| **Giải Thích Logic** | Chỉ comment những đoạn code có logic phức tạp hoặc quyết định thiết kế không hiển nhiên. |
| **Định Dạng** | Comment phải **ngắn gọn, súc tích**, nằm sát dòng code liên quan. |
| **Ghi Chú Công Việc** | Dùng `# TODO:` hoặc `# FIXME:` để đánh dấu công việc cần làm. |

## 4. Luồng Làm Việc (Workflow)

Khi thực hiện các yêu cầu, hãy tuân theo luồng làm việc sau:

1.  **Phân tích yêu cầu:** Hiểu rõ yêu cầu và xác định các module bị ảnh hưởng.
2.  **Tuân thủ kiến trúc:**
    - Khi thêm tính năng mới, tạo hoặc cập nhật các file (`router.py`, `schemas.py`, `models.py`, `service.py`, `crud.py`) trong module tương ứng.
    - Tận dụng các thành phần dùng chung trong `src/core/` (ví dụ: `get_db`, `get_current_user`).
3.  **Viết code:** Áp dụng các tiêu chuẩn Clean Code, PEP 8 và quy tắc comment đã nêu.
4.  **Viết/Cập nhật kiểm thử:** Luôn viết hoặc cập nhật unit test trong thư mục `tests/` để đảm bảo chất lượng và tính đúng đắn của code mới.
5.  **Kiểm tra lại:** Trước khi hoàn thành, đảm bảo code chạy đúng, pass tất cả các bài test và không có lỗi linting.
