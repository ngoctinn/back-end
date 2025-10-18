# Kế hoạch 6.1 (v4): Triển khai Sản phẩm & Danh mục Sản phẩm

## 1. Mô tả Ngữ cảnh

- **Tính năng:** Xây dựng các thành phần cơ bản để quản lý Sản phẩm và Danh mục Sản phẩm, với cấu trúc chi tiết hỗ trợ quản lý kho chuyên nghiệp.
- **Phạm vi:** Model, schema, CRUD, và API cho `Product` và `ProductCategory`.
- **Mục tiêu:** Hoàn thành chức năng CRUD cho sản phẩm, bao gồm các thuộc tính về đơn vị tính, giá vốn, và mã vạch để tạo nền tảng vững chắc cho việc quản lý kho và tính toán lợi nhuận.

## 2. Các Tệp và Hàm Liên quan

### `src/modules/services/models.py` - Định nghĩa đầy đủ và chi tiết

1.  **Model `ProductCategory(SQLModel, table=True)`**
    - `id: Optional[int]` = Field(default=None, primary_key=True)
    - `name: str` = Field(index=True)
    - `description: str`
    - `products: List["Product"]` = Relationship(back_populates="category")

2.  **Model `Product(SQLModel, table=True)`**
    - `id: Optional[int]` = Field(default=None, primary_key=True)
    - `name: str` = Field(index=True)
    - `sku: str` = Field(unique=True, index=True)
    - `barcode: Optional[str]` = Field(default=None, unique=True, index=True)
    - `brand: Optional[str]`
    - `description: str`
    - `product_type: str` = Field(index=True) (Loại: 'RETAIL' hoặc 'PROFESSIONAL')
    - `purchase_price: float` = Field(default=0.0) (Giá vốn/giá nhập)
    - `price: float` (Giá bán lẻ cho khách)
    - `stock_unit: str` (Đơn vị tính tồn kho, ví dụ: 'ml', 'g', 'item')
    - `stock_quantity: float` = Field(default=0.0)
    - `low_stock_threshold: float` = Field(default=0.0)
    - `category_id: Optional[int]` = Field(default=None, foreign_key="productcategory.id")
    - `primary_image_id: Optional[int]` = Field(default=None, foreign_key="mediafile.id")
    - `category: Optional[ProductCategory]` = Relationship(back_populates="products")

### Các tệp khác

- **`schemas.py`**: Phải tạo/cập nhật đầy đủ các schema (`ProductCreate`, `ProductRead`, `ProductUpdate`) để phản ánh tất cả các trường mới và chi tiết của model `Product`.
- **`router.py`**: Các endpoint CRUD cho `/products` phải hỗ trợ việc nhận và trả về các trường dữ liệu mới này.

## 3. Thuật toán/Logic

- **Logic Quản lý Tồn kho:**
  1.  `stock_quantity` luôn được hiểu theo đơn vị của `stock_unit`.
  2.  Khi một sản phẩm `PROFESSIONAL` được tiêu hao trong dịch vụ (logic được mô tả trong Kế hoạch 6.3), số lượng tiêu hao (ví dụ: 20ml) sẽ được trừ trực tiếp vào `stock_quantity` của sản phẩm đó.
  3.  Khi một sản phẩm `RETAIL` được bán, `stock_quantity` sẽ giảm đi một lượng tương ứng (ví dụ: giảm 1 nếu `stock_unit` là 'item').

- **Logic Cảnh báo Tồn kho:**
  - Sau mỗi lần cập nhật `stock_quantity`, hệ thống cần kiểm tra `if stock_quantity <= low_stock_threshold`. Nếu đúng, một sự kiện/thông báo cần được kích hoạt (logic chi tiết của việc gửi thông báo sẽ nằm ở module khác).

- **Logic xác thực `category_id` và `primary_image_id`:** (Giữ nguyên như các phiên bản trước).