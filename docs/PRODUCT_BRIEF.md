# SPA CUSTOMER CARE PLATFORM - PRODUCT BRIEF

## 1. Tổng quan / Mô tả Dự án

**Spa Customer Care Platform** là hệ thống quản lý chăm sóc khách hàng trực tuyến (CMS) dành cho spa, nhằm số hóa toàn bộ quy trình vận hành từ quản lý khách hàng, đặt lịch hẹn, đến quản lý dịch vụ và nhân viên. Hệ thống được xây dựng như một giải pháp CRM tích hợp, giúp spa nâng cao chất lượng dịch vụ khách hàng, tối ưu hóa lịch làm việc nhân viên và quản lý nghiệp vụ hiệu quả.

## 2. Đối tượng Mục tiêu

- **Chủ spa / Quản lý:** Giám sát toàn bộ hoạt động kinh doanh, quản lý nhân viên và dịch vụ
- **Lễ tân spa:** Quản lý lịch hẹn, đăng ký khách hàng, xử lý booking
- **Chuyên viên spa:** Xem lịch làm việc cá nhân, cập nhật trạng thái dịch vụ
- **Khách hàng:** Đặt lịch hẹn trực tuyến, xem lịch sử điều trị, quản lý thông tin cá nhân

## 3. Lợi ích / Tính năng Chính

### Lợi ích Cốt lõi

- **Tự động hóa quy trình:** Giảm thiểu công việc thủ công trong quản lý lịch hẹn và khách hàng
- **Trải nghiệm khách hàng:** Cho phép khách hàng tự đặt lịch 24/7, xem lịch sử điều trị
- **Tối ưu nguồn lực:** Quản lý lịch làm việc nhân viên hiệu quả, tránh trùng lặp
- **Dữ liệu tập trung:** Lưu trữ thông tin khách hàng chi tiết phục vụ chăm sóc cá nhân hóa

### Tính năng Chính

1. **Quản lý Khách hàng (CRM)**

   - Hồ sơ khách hàng chi tiết (thông tin cá nhân, tình trạng da/sức khỏe)
   - Lịch sử điều trị và ghi chú CSKH
   - Tìm kiếm và phân loại khách hàng

2. **Quản lý Lịch hẹn**

   - Đặt lịch hẹn trực tuyến với xác nhận tự động
   - Quản lý trạng thái lịch hẹn (Đã xác nhận/Đã hủy/Hoàn thành)
   - Xem lịch làm việc theo nhân viên

3. **Quản lý Dịch vụ & Sản phẩm**

   - Danh mục dịch vụ spa (massage, chăm sóc da, ...)
   - Quản lý giá, thời lượng và mô tả dịch vụ
   - Quản lý sản phẩm bán ra

4. **Quản lý Nhân viên**

   - Phân quyền theo vai trò (Quản lý/Chuyên viên/Lễ tân)
   - Quản lý lịch làm việc và ca trực
   - Theo dõi hiệu suất phục vụ

5. **Xác thực & Bảo mật**
   - Đăng nhập/Đăng ký an toàn với JWT
   - Phân quyền chi tiết theo vai trò người dùng
   - Bảo mật thông tin khách hàng

## 4. Công nghệ / Kiến trúc Cấp cao

### Tech Stack Chính

- **Backend Framework:** FastAPI (Python 3.13.7) - RESTful API hiệu năng cao
- **Database:** PostgreSQL (Supabase) - Cơ sở dữ liệu quan hệ
- **ORM:** SQLModel - Tích hợp Pydantic và SQLAlchemy
- **Authentication:** JWT (PyJWT) - Xác thực token-based
- **Migration:** Alembic - Quản lý phiên bản database
- **Server:** Uvicorn - ASGI server cho FastAPI
- **Testing:** pytest - Framework kiểm thử

### Kiến trúc

**Modular/Domain-Driven Architecture** - Hệ thống được tổ chức theo các module nghiệp vụ độc lập:

```
src/
├── core/           # Cấu hình, bảo mật, dependencies chung
├── modules/        # Domain modules
│   ├── auth/       # Xác thực & ủy quyền
│   ├── customers/  # Quản lý khách hàng (CRM)
│   ├── services/   # Quản lý dịch vụ & sản phẩm
│   ├── appointments/ # Quản lý lịch hẹn
│   └── staff/      # Quản lý nhân viên
```

Mỗi module tuân theo cấu trúc:

- **router.py** - API endpoints
- **schemas.py** - Pydantic models (DTOs)
- **models.py** - Database models
- **service.py** - Business logic
- **crud.py** - Data access layer

---

_Tài liệu này được tạo tự động dựa trên yêu cầu nghiệp vụ và kiến trúc kỹ thuật của dự án Spa Customer Care Platform._
