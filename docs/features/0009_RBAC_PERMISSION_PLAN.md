# Kế hoạch 9: Hoàn thiện API Quản lý Phân quyền (RBAC)

## 1. Mô tả Ngữ cảnh

- **Tính năng:** Bổ sung các API endpoint còn thiếu để hoàn thiện chức năng quản lý hệ thống phân quyền, cho phép admin quản lý `Permission` (Quyền hạn) và gán chúng cho các `Role` (Vai trò).
- **Mục tiêu:** Cung cấp một bộ API đầy đủ cho phép quản trị viên có thể cấu hình động toàn bộ hệ thống RBAC.
- **Yêu cầu bảo mật:** Tất cả các endpoint mới sẽ được bảo vệ bởi dependency `get_admin_user` đã có.

## 2. Các Tệp và Hàm Liên quan

### `src/modules/auth/crud.py`

- **Các hàm đã có và sẽ được sử dụng:**
  - `create_permission`, `get_permission`, `get_all_permissions`.
  - `add_permission_to_role`, `remove_permission_from_role`.
  - `get_role`.
- **Hàm cần bổ sung (nếu chưa có):**
  - `update_permission`, `delete_permission` để hoàn thiện CRUD.

### `src/modules/auth/router.py`

- **Cập nhật `admin_router`:** Thêm các nhóm endpoint mới.

  - **Nhóm Quản lý Permissions (`/permissions`):**
    - `POST /permissions`: Tạo một quyền hạn mới.
    - `GET /permissions`: Lấy danh sách tất cả quyền hạn.
    - `GET /permissions/{permission_id}`: Lấy chi tiết một quyền hạn.
    - `PUT /permissions/{permission_id}`: Cập nhật một quyền hạn.
    - `DELETE /permissions/{permission_id}`: Xóa một quyền hạn.

  - **Nhóm Gán Quyền cho Vai trò (`/roles/{role_id}/permissions`):**
    - `POST /roles/{role_id}/permissions/{permission_id}`: Gán một quyền cho một vai trò.
    - `DELETE /roles/{role_id}/permissions/{permission_id}`: Thu hồi một quyền từ một vai trò.

### `src/modules/auth/schemas.py`

- Các schema cần thiết (`PermissionCreate`, `PermissionRead`, `RoleReadWithPermissions`) đã được định nghĩa trong lần tái cấu trúc trước. Không cần thay đổi, chỉ sử dụng lại.

## 3. Thuật toán/Logic

- **Logic cho Endpoint `POST /permissions`:**
  1.  Sử dụng `Depends(get_admin_user)` để xác thực quyền admin.
  2.  Nhận `PermissionCreate` schema từ body của request.
  3.  Kiểm tra xem quyền hạn với `name` tương tự đã tồn tại chưa để tránh trùng lặp. Nếu có, trả về lỗi `HTTP 409 Conflict`.
  4.  Gọi `crud.create_permission` để lưu vào CSDL.
  5.  Trả về thông tin quyền hạn vừa tạo.

- **Logic cho Endpoint `POST /roles/{role_id}/permissions/{permission_id}`:**
  1.  Sử dụng `Depends(get_admin_user)`.
  2.  Dùng `crud.get_role` để tìm vai trò theo `role_id`. Nếu không thấy, trả lỗi 404.
  3.  Dùng `crud.get_permission` để tìm quyền hạn theo `permission_id`. Nếu không thấy, trả lỗi 404.
  4.  Gọi `crud.add_permission_to_role` để thêm `permission` vào danh sách `role.permissions`.
  5.  Commit thay đổi và trả về thông tin `Role` đã được cập nhật (bao gồm danh sách permissions mới).
