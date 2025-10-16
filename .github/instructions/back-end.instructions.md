BRIEF DỰ ÁN FASTAPI: HỆ THỐNG CSKH TRỰC TUYẾN SPA (CMS)
Dự án này sẽ được tổ chức theo kiến trúc Modular/Domain-Driven, trong đó mỗi tính năng nghiệp vụ chính (Domain) sẽ là một module độc lập, giúp dự án dễ dàng mở rộng và bảo trì.

I. Cấu Trúc Thư Mục Tổng Thể
Dự án sẽ nằm trong thư mục src/ (Source), với mỗi Domain là một thư mục con riêng biệt trong src/modules/.

spa_online_crm/
├── src/
│ ├── main.py # Khởi tạo ứng dụng FastAPI, gắn các router
│ ├── core/ # Các thành phần dùng chung toàn hệ thống
│ │ ├── config.py # Cấu hình Pydantic BaseSettings (DB URL, API Keys, ...)
│ │ ├── db.py # Khởi tạo Database Engine, Session
│ │ ├── security.py # Logic bảo mật (JWT, Hashing)
│ │ └── dependencies.py # Các hàm Depends() chung (get_db, get_current_user)
│ ├── modules/ # PHÂN TÁCH THEO DOMAIN NGHIỆP VỤ
│ │ ├── auth/ # 1. Quản lý Xác thực & Ủy quyền
│ │ ├── customers/ # 2. Quản lý Khách hàng (CRM)
│ │ ├── services/ # 3. Quản lý Dịch vụ & Sản phẩm
│ │ ├── appointments/ # 4. Quản lý Lịch hẹn
│ │ └── staff/ # 5. Quản lý Nhân viên Spa
│ └── tests/ # Thư mục kiểm thử, phản ánh cấu trúc modules
├── .env # Biến môi trường
├── requirements.txt
└── README.md
II. Phân Tách Vai Trò Trong Mỗi Module
Mỗi Domain (ví dụ: customers/ hoặc appointments/) sẽ có cấu trúc nội bộ nhất quán, đảm bảo tính đóng gói (encapsulation) của logic nghiệp vụ:

src/modules/{domain}/
├── **init**.py
├── router.py # (Endpoints) Định nghĩa APIRouter và các API path operations.
├── schemas.py # (Pydantic) Định nghĩa các request/response body (DTOs).
├── models.py # (DB Models) Định nghĩa các bảng/model database (ví dụ: SQLModel/SQLAlchemy).
├── service.py # (Business Logic) Chứa logic nghiệp vụ phức tạp, gọi CRUD.
└── crud.py # (Data Access) Chỉ chứa các thao tác trực tiếp với DB (Create, Read, Update, Delete).
III. Mô Tả Chi Tiết Các Module Chính
Dựa trên mục tiêu hệ thống CSKH cho Spa, các module nghiệp vụ cần thiết bao gồm:

1. auth (Xác thực và Ủy quyền)
   Mục tiêu: Quản lý đăng ký, đăng nhập và tạo/xác thực Token JWT cho cả Khách hàng và Nhân viên.

Endpoints chính: /login, /register, /token/refresh.

Logic chính: Hash mật khẩu (service.py), xác thực token (dependencies.py trong core/).

2. customers (Quản lý Khách hàng - CRM)
   Mục tiêu: Lưu trữ và quản lý hồ sơ chi tiết của khách hàng (thông tin cá nhân, lịch sử điều trị, ghi chú).

Models chính: Customer (Họ tên, SĐT, Email, Tình trạng da/sức khỏe, Ghi chú CSKH).

Endpoints chính: /customers/{id}, /customers/search.

3. services (Quản lý Dịch vụ và Sản phẩm)
   Mục tiêu: Định nghĩa các loại dịch vụ (massage, chăm sóc da) và sản phẩm bán ra.

Models chính: Service (Tên, Mô tả, Giá, Thời lượng), Product.

Endpoints chính: /services/, /products/{id}.

4. appointments (Quản lý Lịch hẹn)
   Mục tiêu: Quản lý việc đặt lịch hẹn giữa Khách hàng và Nhân viên. Đây là module trung tâm của hệ thống.

Models chính: Appointment (Khách hàng ID, Nhân viên ID, Dịch vụ ID, Thời gian Bắt đầu/Kết thúc, Trạng thái - Đã xác nhận/Đã hủy/Hoàn thành).

Endpoints chính: /appointments/create, /appointments/staff/{staff_id}/schedule.

5. staff (Quản lý Nhân viên)
   Mục tiêu: Quản lý thông tin và vai trò của nhân viên Spa (chuyên viên, lễ tân, quản lý).

Models chính: Staff (Họ tên, Vai trò/Quyền hạn, Lịch làm việc).

Endpoints chính: /staff/, /staff/{id}/roles.

6. Công nghệ và Thư viện Sử Dụng:

- Python: 3.13.7 thống nhất dùng cú pháp mới nhất.
- FastAPI: Framework chính để xây dựng API.
- SQLModel: ORM để tương tác với cơ sở dữ liệu quan hệ (PostgreSQL trên Supabase).
- Pydantic: Để định nghĩa và xác thực dữ liệu (schemas).
- Alembic: Quản lý migration cho database.
- JWT (PyJWT): Quản lý xác thực và ủy quyền người dùng.
- Uvicorn: Server ASGI để chạy ứng dụng FastAPI.
- pytest: Framework kiểm thử.

IV. Tóm tắt Lợi ích của Kiến trúc Module
Kiến trúc này đảm bảo:

Phân tách rõ ràng: Logic nghiệp vụ, định nghĩa dữ liệu (Pydantic), và tương tác DB được giữ riêng biệt.

Khả năng mở rộng: Khi muốn thêm một tính năng mới (ví dụ: promotions - khuyến mãi), chỉ cần tạo một thư mục module mới mà không cần chỉnh sửa sâu vào các module hiện tại.

Dễ bảo trì: Các thay đổi trong logic của Khách hàng (customers/service.py) không ảnh hưởng đến logic của Lịch hẹn (appointments/service.py), miễn là giao diện dữ liệu (schemas) vẫn giữ nguyên.
