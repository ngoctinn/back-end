# Hướng dẫn sử dụng API Module Media

## 1. Giới thiệu

Module Media (`/media`) chịu trách nhiệm xử lý tất cả các hoạt động liên quan đến file, chủ yếu là hình ảnh. Nó cung cấp các API để tải file lên, truy vấn và xóa file một cách an toàn. Module này được thiết kế để phục vụ các module khác (như `Customer`, `Catalog`) một cách linh hoạt.

## 2. Mô hình Dữ liệu

Module này sử dụng một model duy nhất là `MediaFile` để lưu trữ thông tin (metadata) của mỗi file được tải lên. Mối liên kết với các đối tượng khác (khách hàng, dịch vụ...) được thực hiện thông qua hai trường:

- `related_entity_type` (string): Loại đối tượng, ví dụ: `customer`, `service`.
- `related_entity_id` (integer): ID của đối tượng cụ thể.

## 3. Danh sách API Endpoints

**Prefix chung:** `/media`

--- 

### 3.1. Tải ảnh lên

- **`POST /customers/me/avatar`**
    - **Mô tả:** Người dùng đã đăng nhập tự tải lên ảnh đại diện của chính mình.
    - **Quyền:** Yêu cầu JWT token.
    - **Body:** `multipart/form-data` với một trường `file` chứa file ảnh.

- **`POST /customers/{customer_id}/avatar`**
    - **Mô tả:** Tải lên ảnh đại diện cho một khách hàng cụ thể (thường dùng cho admin).
    - **Quyền:** Yêu cầu JWT token.
    - **Body:** `multipart/form-data` với một trường `file` chứa file ảnh.

- **`POST /services/{service_id}/images`**
    - **Mô tả:** Tải lên một ảnh cho một dịch vụ cụ thể.
    - **Quyền:** Yêu cầu JWT token.
    - **Body:** `multipart/form-data` với một trường `file` chứa file ảnh.

### 3.2. Truy vấn ảnh

- **`GET /customers/{customer_id}`**
    - **Mô tả:** Lấy danh sách tất cả các ảnh đã được tải lên cho một khách hàng cụ thể.
    - **Quyền:** Công khai.
    - **Phản hồi:** Một danh sách các đối tượng `MediaResponse`.

- **`GET /services/{service_id}`**
    - **Mô tả:** Lấy danh sách tất cả các ảnh đã được tải lên cho một dịch vụ cụ thể.
    - **Quyền:** Công khai.

### 3.3. Xóa ảnh

- **`DELETE /{media_id}`**
    - **Mô tả:** Xóa một file ảnh khỏi hệ thống (bao gồm cả trên cloud storage và trong CSDL).
    - **Quyền:** Yêu cầu JWT token.
    - **Phản hồi:** `{ "message": "Xóa ảnh thành công" }`.