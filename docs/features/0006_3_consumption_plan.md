# Kế hoạch 6.3: Triển khai liên kết Vật tư tiêu hao cho Dịch vụ

## 1. Mô tả Ngữ cảnh

- **Tính năng:** Xây dựng chức năng để liên kết một `Product` (loại `PROFESSIONAL`) vào một `Service` như một vật tư tiêu hao.
- **Phạm vi:** Tạo model `ServiceProductConsumption` và API để quản lý liên kết này.
- **Điều kiện cần:** Kế hoạch 6.1 và 6.2 phải được hoàn thành.

## 2. Các Tệp và Hàm Liên quan

### Các tệp cần CẬP NHẬT trong `src/modules/services/`

1.  **`models.py`**
    - **Tạo Model `ServiceProductConsumption(SQLModel, table=True)`**:
        - `service_id`: Khóa ngoại tới `service.id`, primary key.
        - `product_id`: Khóa ngoại tới `product.id`, primary key.
        - `consumed_quantity`: `float`.
        - `unit`: `str` (ví dụ: 'ml', 'g').

2.  **`schemas.py`**
    - Tạo schema `ServiceConsumptionCreate` (nhận `product_id`, `consumed_quantity`, `unit`).
    - Tạo schema `ServiceConsumptionRead` để hiển thị thông tin liên kết.

3.  **`crud.py`**
    - Tạo các hàm để tạo, lấy và xóa các liên kết trong bảng `ServiceProductConsumption`.

4.  **`router.py`**
    - Tạo các endpoint mới lồng trong `services`:
        - `POST /services/{service_id}/consumptions`: Thêm một sản phẩm tiêu hao vào dịch vụ.
        - `DELETE /services/{service_id}/consumptions/{product_id}`: Xóa một sản phẩm tiêu hao khỏi dịch vụ.
        - `GET /services/{service_id}/consumptions`: Lấy danh sách các sản phẩm tiêu hao của dịch vụ.

## 3. Thuật toán/Logic (Trong phạm vi Kế hoạch này)

- **Logic của endpoint `POST /services/{service_id}/consumptions`:**
  1.  Nhận `service_id` từ path và `ServiceConsumptionCreate` schema từ body.
  2.  Kiểm tra `service_id` và `product_id` có tồn tại không.
  3.  Kiểm tra `Product` tương ứng có `product_type` là 'PROFESSIONAL' hoặc 'BOTH' không. Nếu không, trả về lỗi `HTTP 400 Bad Request`.
  4.  Tạo hoặc cập nhật bản ghi trong bảng `ServiceProductConsumption`.
