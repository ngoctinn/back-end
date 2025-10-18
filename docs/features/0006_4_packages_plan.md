# Kế hoạch 6.4 (v3): Triển khai Gói liệu trình & Danh mục Gói

## 1. Mô tả Ngữ cảnh

- **Tính năng:** Xây dựng chức năng để tạo và quản lý các Gói liệu trình, bao gồm cả ảnh đại diện.
- **Phạm vi:** `ServicePackage`, `PackageCategory`, và bảng liên kết `PackageServiceLink`.
- **Điều kiện cần:** Kế hoạch 6.2 phải được hoàn thành.

## 2. Các Tệp và Hàm Liên quan

### `src/modules/services/models.py` - Định nghĩa đầy đủ

1.  **Model `PackageCategory(SQLModel, table=True)`**
    - `id: Optional[int]` = Field(default=None, primary_key=True)
    - `name: str` = Field(index=True)
    - `description: str`
    - `packages: List["ServicePackage"]` = Relationship(back_populates="category")

2.  **Model `PackageServiceLink(SQLModel, table=True)`**
    - `package_id: Optional[int]` = Field(default=None, foreign_key="servicepackage.id", primary_key=True)
    - `service_id: Optional[int]` = Field(default=None, foreign_key="service.id", primary_key=True)

3.  **Model `ServicePackage(SQLModel, table=True)`**
    - `id: Optional[int]` = Field(default=None, primary_key=True)
    - `name: str`
    - `description: str`
    - `total_price: float`
    - `validity_period_days: int`
    - `terms_and_conditions: str`
    - `category_id: Optional[int]` = Field(default=None, foreign_key="packagecategory.id")
    - `primary_image_id: Optional[int]` = Field(default=None, foreign_key="mediafile.id")
    - `category: Optional[PackageCategory]` = Relationship(back_populates="packages")
    - `services: List[Service]` = Relationship(back_populates="packages", link_model=PackageServiceLink)

### Các tệp khác

- **`schemas.py`**: Cần tạo đầy đủ các schema cho các model trên. `ServicePackageCreate` sẽ nhận một danh sách `service_ids`. `ServicePackageRead` sẽ chứa thông tin ảnh chính và danh sách dịch vụ chi tiết.
- **`router.py`**: Cần tạo đầy đủ endpoint CRUD cho `/package-categories` và `/service-packages`, cùng với endpoint `POST /service-packages/{package_id}/set-primary-image/{media_id}`.

## 3. Thuật toán/Logic

- **Logic tạo/cập nhật `ServicePackage`:** Khi tạo/cập nhật, phải xác thực `category_id` (nếu có) và tất cả `service_ids` trong danh sách đều hợp lệ.
- **Logic thiết lập ảnh chính:** Endpoint `set-primary-image` phải xác thực `media_id` thuộc về `package_id` trước khi cập nhật trường `primary_image_id`.
