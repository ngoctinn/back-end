# Kế hoạch 8: API Quản lý Hệ thống Phân quyền (RBAC)

## 1. Mô tả Ngữ cảnh

- **Tính năng:** Xây dựng các API endpoint cho phép người dùng có vai trò `admin` quản lý toàn bộ hệ thống phân quyền.
- **Phạm vi:** Bao gồm việc tạo, sửa, xóa, và gán các `Role` (Vai trò) và `Permission` (Quyền hạn).
- **Mục tiêu:** Cung cấp cho quản trị viên khả năng cấu hình động các vai trò và quyền hạn trong hệ thống thông qua API, thay vì phải thay đổi trực tiếp trong CSDL.
- **Yêu cầu bảo mật:** Tất cả các endpoint trong kế hoạch này phải được bảo vệ và chỉ cho phép người dùng có vai trò `admin` truy cập.

## 2. Các Tệp và Hàm Liên quan

### `src/core/dependencies.py`

- **Tạo Dependency mới `get_admin_user`:**
  - Dependency này sẽ tái sử dụng `get_current_user` để lấy thông tin người dùng từ JWT token.
  - Sau đó, nó sẽ kiểm tra xem chuỗi `"admin"` có nằm trong danh sách `roles` của người dùng hay không.
  - Nếu không, nó sẽ trả về lỗi `HTTPException 403 Forbidden`.

### `src/modules/auth/schemas.py`

- **Thêm Schemas cho `Role`:**
  - `RoleCreate(BaseModel)`: `name: str`, `description: str`.
  - `RoleUpdate(BaseModel)`: `name: Optional[str]`, `description: Optional[str]`.
  - `RoleRead(RoleCreate)`: Thêm `id: int`.
  - `RoleReadWithPermissions(RoleRead)`: Thêm `permissions: List[PermissionRead]`.

- **Thêm Schemas cho `Permission`:**
  - `PermissionCreate(BaseModel)`: `name: str`, `description: str`.
  - `PermissionUpdate(BaseModel)`: `name: Optional[str]`, `description: Optional[str]`.
  - `PermissionRead(PermissionCreate)`: Thêm `id: int`.

- **Cập nhật `UserResponse`:**
  - Đảm bảo schema này trả về danh sách các `RoleRead` thay vì chỉ tên vai trò để có thông tin chi tiết hơn.

### `src/modules/auth/crud.py`

- **Thêm CRUD cho `Role`:**
  - `create_role`, `get_role`, `get_all_roles`, `update_role`, `delete_role`.
- **Thêm CRUD cho `Permission`:**
  - `create_permission`, `get_permission`, `get_all_permissions`, `update_permission`, `delete_permission`.
- **Thêm/Cập nhật các hàm quản lý mối quan hệ:**
  - `get_user_by_id(db, user_id)`: Hàm mới để lấy user theo ID.
  - `add_permission_to_role(db, role, permission)`.
  - `remove_permission_from_role(db, role, permission)`.
  - `revoke_role_from_user(db, user, role)`: Hàm mới để thu hồi vai trò từ người dùng.

### `src/modules/auth/router.py`

- **Thêm các nhóm Endpoint mới (yêu cầu quyền admin):**

  - **Quản lý Roles:**
    - `POST /roles`
    - `GET /roles`
    - `GET /roles/{role_id}`
    - `PUT /roles/{role_id}`
    - `DELETE /roles/{role_id}`

  - **Quản lý Permissions:**
    - `POST /permissions`
    - `GET /permissions`
    - `GET /permissions/{permission_id}`

  - **Gán Quyền cho Vai trò:**
    - `POST /roles/{role_id}/permissions/{permission_id}`
    - `DELETE /roles/{role_id}/permissions/{permission_id}`

  - **Gán Vai trò cho Người dùng:**
    - `POST /users/{user_id}/roles/{role_id}`
    - `DELETE /users/{user_id}/roles/{role_id}`

## 3. Thuật toán/Logic

- **Logic của Dependency `get_admin_user`:**
  1.  Gọi `get_current_user` để lấy `user` object.
  2.  Kiểm tra `if "admin" not in [role.name for role in user.roles]:`.
  3.  Nếu điều kiện đúng, `raise HTTPException(status_code=403, detail="Yêu cầu quyền admin")`.
  4.  Nếu không, trả về `user` object.

- **Logic của Endpoint gán quyền (`POST /roles/{role_id}/permissions/{permission_id}`):**
  1.  Sử dụng `Depends(get_admin_user)` để bảo vệ endpoint.
  2.  Dùng `crud.get_role` để tìm vai trò theo `role_id`. Nếu không thấy, trả lỗi 404.
  3.  Dùng `crud.get_permission` để tìm quyền hạn theo `permission_id`. Nếu không thấy, trả lỗi 404.
  4.  Kiểm tra xem quyền đã được gán cho vai trò chưa để tránh trùng lặp.
  5.  Gọi `crud.add_permission_to_role` để thêm `permission` vào `role.permissions`.
  6.  Commit thay đổi và trả về thông tin vai trò đã được cập nhật.

- **Logic của Endpoint gán vai trò (`POST /users/{user_id}/roles/{role_id}`):**
  1.  Sử dụng `Depends(get_admin_user)`.
  2.  Dùng `crud.get_user_by_id` để tìm người dùng. Nếu không thấy, trả lỗi 404.
  3.  Dùng `crud.get_role` để tìm vai trò. Nếu không thấy, trả lỗi 404.
  4.  Gọi `crud.assign_role_to_user`.
  5.  Commit và trả về thông tin người dùng đã được cập nhật.
