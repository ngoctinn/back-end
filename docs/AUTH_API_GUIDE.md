# Hướng dẫn API Module Xác thực & Phân quyền (v2.1)

**Phiên bản:** 2.1 (RBAC)
**Cập nhật:** 2025-10-18

## 1. Tổng Quan

Module này cung cấp một hệ thống xác thực và ủy quyền hoàn chỉnh, sử dụng JWT (Access Token), Refresh Token, và mô hình Role-Based Access Control (RBAC) để phân quyền chi tiết.

## 2. Mô hình & Luồng Token

### Sơ đồ Dữ liệu Phân quyền (RBAC)

```
[User] *---* [Role] *---* [Permission]
  (user_roles)   (role_permissions)
```

- **User**: Tài khoản người dùng.
- **Role**: Vai trò trong hệ thống (ví dụ: `user`, `admin`).
- **Permission**: Quyền hạn cụ thể (ví dụ: `products:create`).

### Luồng Access Token & Refresh Token

1.  **Đăng nhập:** Client gửi email/password, server trả về `access_token` (ngắn hạn, 15 phút) và set một `refresh_token` (dài hạn, 7 ngày) vào `HttpOnly` cookie.
2.  **Gọi API:** Client gửi `access_token` trong header `Authorization: Bearer <token>`.
3.  **Token hết hạn:** Khi API trả về lỗi `401 Unauthorized`, client tự động gọi endpoint `/auth/refresh`.
4.  **Làm mới:** Server xác thực `refresh_token` từ cookie, tạo một `access_token` mới và trả về cho client.
5.  **Thử lại:** Client dùng `access_token` mới để gọi lại API đã thất bại trước đó.

### Cấu trúc Access Token (JWT)

```json
{
  "sub": "1", // User ID
  "roles": ["user", "staff"], // Danh sách tên các vai trò
  "iat": 1697520000, // Thời điểm cấp
  "exp": 1697520900  // Thời điểm hết hạn
}
```

---

## 3. Chi tiết API Endpoints

### 3.1. Endpoints Xác thực Chung (`/auth`)

#### **`POST /auth/register`**

- **Mô tả:** Đăng ký tài khoản mới. Hệ thống sẽ tự động tạo một hồ sơ `Customer` "chờ" và gán vai trò `user` mặc định. Một email xác minh sẽ được gửi đi.
- **Request Body:**
  ```json
  {
    "email": "new.user@example.com",
    "password": "SecurePassword123"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "message": "Đăng ký thành công. Vui lòng xác minh email",
    "email": "new.user@example.com"
  }
  ```
- **Lỗi:** `400` (Email đã tồn tại), `422` (Dữ liệu không hợp lệ).

#### **`POST /auth/verify-email`**

- **Mô tả:** Xác minh email của người dùng bằng token nhận được từ email.
- **Request Body:**
  ```json
  {
    "token": "<token_from_email_link>"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "message": "Email xác minh thành công",
    "email": "new.user@example.com"
  }
  ```
- **Lỗi:** `400` (Token không hợp lệ hoặc đã hết hạn).

#### **`POST /auth/login`**

- **Mô tả:** Đăng nhập vào hệ thống. Trả về `access_token` và set `refresh_token` vào cookie.
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "access_token": "<jwt_access_token>",
    "token_type": "bearer"
  }
  ```
- **Lỗi:** `401` (Thông tin không hợp lệ), `403` (Tài khoản chưa kích hoạt).

#### **`POST /auth/refresh`**

- **Mô tả:** Làm mới `access_token` đã hết hạn bằng `refresh_token` trong cookie.
- **Request:** Không có body. Client phải đảm bảo gửi kèm cookie.
- **Response (200 OK):**
  ```json
  {
    "access_token": "<new_jwt_access_token>",
    "token_type": "bearer"
  }
  ```
- **Lỗi:** `401` (Refresh token không hợp lệ hoặc bị thiếu).

#### **`POST /auth/logout`**

- **Mô tả:** Đăng xuất khỏi hệ thống. Server sẽ thu hồi `refresh_token` và xóa cookie.
- **Request:** Không có body. Client phải đảm bảo gửi kèm cookie.
- **Response (200 OK):**
  ```json
  {
    "message": "Đã đăng xuất"
  }
  ```

#### **`GET /auth/me`**

- **Mô tả:** Lấy thông tin chi tiết của người dùng đang đăng nhập.
- **Yêu cầu:** `Authorization: Bearer <access_token>`.
- **Response (200 OK):**
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "roles": [
      {
        "name": "user",
        "description": "Vai trò người dùng cơ bản",
        "id": 1
      }
    ],
    "is_active": true
  }
  ```
- **Lỗi:** `401` (Token không hợp lệ hoặc hết hạn).

*(Các endpoint khác như `/password-reset`, `/confirm-password-reset` hoạt động tương tự luồng verify-email)*

---

### 3.2. Endpoints Quản lý Phân quyền (`/admin`)

**Lưu ý:** Tất cả các endpoint dưới đây đều yêu cầu quyền `admin`.

#### Quản lý Vai trò (Roles)

- **`POST /admin/roles`**: Tạo một vai trò mới.
  - **Body:** `{"name": "staff", "description": "Nhân viên spa"}`
  - **Response:** `RoleRead`

- **`GET /admin/roles`**: Lấy danh sách tất cả các vai trò.
  - **Response:** `List[RoleRead]`

- **`PUT /admin/roles/{role_id}`**: Cập nhật một vai trò.

- **`DELETE /admin/roles/{role_id}`**: Xóa một vai trò.

#### Quản lý Quyền hạn (Permissions)

- **`POST /admin/permissions`**: Tạo một quyền hạn mới.
  - **Body:** `{"name": "catalog:read", "description": "Quyền xem thông tin trong catalog"}`
  - **Response:** `PermissionRead`

- **`GET /admin/permissions`**: Lấy danh sách tất cả các quyền hạn.
  - **Response:** `List[PermissionRead]`

- **`PUT /admin/permissions/{permission_id}`**: Cập nhật một quyền hạn.

- **`DELETE /admin/permissions/{permission_id}`**: Xóa một quyền hạn.

#### Quản lý Mối quan hệ

- **`POST /admin/users/{user_id}/roles/{role_id}`**: Gán vai trò cho người dùng.
  - **Response:** `UserResponse`

- **`DELETE /admin/users/{user_id}/roles/{role_id}`**: Thu hồi vai trò từ người dùng.
  - **Response:** `UserResponse`

- **`POST /admin/roles/{role_id}/permissions/{permission_id}`**: Gán quyền cho vai trò.
  - **Response:** `RoleReadWithPermissions`

- **`DELETE /admin/roles/{role_id}/permissions/{permission_id}`**: Thu hồi quyền từ vai trò.
  - **Response:** `RoleReadWithPermissions`
