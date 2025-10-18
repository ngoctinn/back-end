# Hướng dẫn sử dụng API Module Catalog

## 1. Giới thiệu

Module Catalog (`/catalog`) là trung tâm quản lý tất cả các sản phẩm, dịch vụ, và gói liệu trình mà spa cung cấp. API này cho phép bạn thực hiện đầy đủ các thao tác CRUD (Tạo, Đọc, Cập nhật, Xóa) trên các tài nguyên này.

## 2. Sơ đồ Dữ liệu

Module này bao gồm các model chính sau và mối quan hệ giữa chúng:

```
[ProductCategory] 1--* [Product]

[ServiceCategory] 1--* [Service]

[PackageCategory] 1--* [ServicePackage]

[Service] *--* [ServicePackage] (Gói chứa nhiều dịch vụ)
[Service] *--* [Product]      (Dịch vụ tiêu hao nhiều sản phẩm)
```

- Mỗi thực thể chính (`Product`, `Service`, `ServicePackage`) đều có thể liên kết với một danh mục tương ứng và một ảnh đại diện (`primary_image_id`).

## 3. Danh sách API Endpoints

**Prefix chung:** `/catalog`

--- 

### 3.1. Quản lý Danh mục Sản phẩm (`ProductCategory`)

- **`POST /product-categories/`**: Tạo một danh mục sản phẩm mới.
- **`GET /product-categories/`**: Lấy danh sách tất cả danh mục sản phẩm.
- **`GET /product-categories/{id}`**: Lấy thông tin chi tiết một danh mục.
- **`PUT /product-categories/{id}`**: Cập nhật một danh mục.
- **`DELETE /product-categories/{id}`**: Xóa một danh mục.

### 3.2. Quản lý Sản phẩm (`Product`)

- **`POST /products/`**: Tạo một sản phẩm mới.
    - **Payload Ví dụ:**
      ```json
      {
        "name": "Serum Vitamin C",
        "sku": "SERUM_C_30ML",
        "product_type": "RETAIL",
        "purchase_price": 250000,
        "price": 550000,
        "stock_unit": "ml",
        "stock_quantity": 1000,
        "category_id": 1
      }
      ```
- **`GET /products/`**: Lấy danh sách sản phẩm.
- **`GET /products/{id}`**: Lấy thông tin chi tiết một sản phẩm.
- **`PUT /products/{id}`**: Cập nhật một sản phẩm.
- **`DELETE /products/{id}`**: Xóa một sản phẩm.
- **`POST /products/{product_id}/set-primary-image/{media_id}`**: Thiết lập ảnh đại diện cho sản phẩm.

--- 

### 3.3. Quản lý Danh mục Dịch vụ (`ServiceCategory`)

- Tương tự như Danh mục Sản phẩm, bao gồm các endpoint `POST`, `GET`, `PUT`, `DELETE` cho `/service-categories/`.

### 3.4. Quản lý Dịch vụ (`Service`)

- **`POST /services/`**: Tạo một dịch vụ mới.
    - **Payload Ví dụ:**
      ```json
      {
        "name": "Chăm sóc da mặt chuyên sâu",
        "description": "Liệu trình 90 phút làm sạch và tái tạo da.",
        "price": 800000,
        "duration_minutes": 90,
        "buffer_time_after": 15,
        "category_id": 1
      }
      ```
- **`GET /services/`**: Lấy danh sách dịch vụ.
- **`GET /services/{id}`**: Lấy thông tin chi tiết một dịch vụ.
- **`PUT /services/{id}`**: Cập nhật một dịch vụ.
- **`DELETE /services/{id}`**: Xóa một dịch vụ.
- **`POST /services/{service_id}/set-primary-image/{media_id}`**: Thiết lập ảnh đại diện cho dịch vụ.

--- 

### 3.5. Quản lý Vật tư tiêu hao (`ServiceProductConsumption`)

- **`POST /services/{service_id}/consumptions`**: Thêm/cập nhật một sản phẩm tiêu hao cho dịch vụ.
    - **Payload Ví dụ:** (Thêm 10ml sản phẩm có ID=5 vào dịch vụ)
      ```json
      {
        "product_id": 5,
        "consumed_quantity": 10,
        "unit": "ml"
      }
      ```
- **`GET /services/{service_id}/consumptions`**: Lấy danh sách các sản phẩm bị tiêu hao bởi dịch vụ.
- **`DELETE /services/{service_id}/consumptions/{product_id}`**: Xóa một sản phẩm tiêu hao khỏi dịch vụ.

--- 

### 3.6. Quản lý Gói liệu trình (`ServicePackage`)

- **`POST /package-categories/`**: Tạo danh mục cho gói liệu trình.
- **`POST /service-packages/`**: Tạo một gói liệu trình mới.
    - **Payload Ví dụ:** (Tạo gói bao gồm dịch vụ ID 1 và 2)
      ```json
      {
        "name": "Gói Thư giãn Toàn diện",
        "total_price": 1500000,
        "validity_period_days": 90,
        "service_ids": [1, 2]
      }
      ```
- **`GET /service-packages/{id}`**: Lấy thông tin chi tiết một gói.
- **`PUT /service-packages/{id}`**: Cập nhật một gói (có thể cập nhật danh sách `service_ids`).
- **`POST /service-packages/{package_id}/set-primary-image/{media_id}`**: Thiết lập ảnh đại diện cho gói.

## 4. Luồng làm việc ví dụ

### Tạo một Dịch vụ hoàn chỉnh

1.  **Tạo danh mục (nếu chưa có):** `POST /catalog/service-categories/` với `name` là "Chăm sóc da". Lấy `id` của danh mục vừa tạo (ví dụ: `id=1`).
2.  **Tải ảnh lên:** Dùng API của module Media (`POST /media/services/{temp_id}/images`) để tải ảnh lên và lấy về `media_id` (ví dụ: `media_id=101`).
3.  **Tạo dịch vụ:** `POST /catalog/services/` với payload chứa `"category_id": 1`.
4.  **Gán ảnh đại diện:** `POST /catalog/services/{service_id}/set-primary-image/{media_id}` với ID dịch vụ vừa tạo và `media_id=101`.
5.  **Gán vật tư tiêu hao:** `POST /catalog/services/{service_id}/consumptions` để thêm các sản phẩm sẽ bị tiêu hao khi thực hiện dịch vụ này.
