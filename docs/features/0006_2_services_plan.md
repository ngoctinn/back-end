# Kế hoạch 6.2 (v3): Triển khai Dịch vụ & Danh mục Dịch vụ

## 1. Mô tả Ngữ cảnh

- **Tính năng:** Xây dựng các thành phần cơ bản để quản lý Dịch vụ và Danh mục Dịch vụ, bao gồm cả ảnh đại diện.
- **Phạm vi:** Model, schema, CRUD, và API cho `Service` và `ServiceCategory`.
- **Mục tiêu:** Hoàn thành chức năng CRUD cho dịch vụ, tạo nền tảng cho các kế hoạch 6.3 và 6.4.

## 2. Các Tệp và Hàm Liên quan

### `src/modules/services/models.py` - Định nghĩa đầy đủ

1.  **Model `ServiceCategory(SQLModel, table=True)`**
    - `id: Optional[int]` = Field(default=None, primary_key=True)
    - `name: str` = Field(index=True)
    - `description: str`
    - `services: List["Service"]` = Relationship(back_populates="category")

2.  **Model `Service(SQLModel, table=True)`**
    - `id: Optional[int]` = Field(default=None, primary_key=True)
    - `name: str`
    - `description: str`
    - `price: float`
    - `duration_minutes: int`
    - `buffer_time_after: int`
    - `is_bookable_online: bool` = Field(default=True)
    - `color_code: str` = Field(default="#FFFFFF")
    - `required_resources: List[str]` = Field(sa_column=Column(JSON), default_factory=list)
    - `required_staff_skills: List[str]` = Field(sa_column=Column(JSON), default_factory=list)
    - `category_id: Optional[int]` = Field(default=None, foreign_key="servicecategory.id")
    - `primary_image_id: Optional[int]` = Field(default=None, foreign_key="mediafile.id")
    - `category: Optional[ServiceCategory]` = Relationship(back_populates="services")

### Các tệp khác

- **`schemas.py`**: Cần tạo đầy đủ các schema `ServiceCategoryCreate/Read/Update` và `ServiceCreate/Read/Update` phản ánh tất cả các trường trên. `ServiceRead` sẽ chứa thông tin ảnh chính.
- **`router.py`**: Cần tạo đầy đủ endpoint CRUD cho `/service-categories` và `/services`, cùng với endpoint `POST /services/{service_id}/set-primary-image/{media_id}`.

## 3. Thuật toán/Logic

- **Logic xác thực `category_id`:** Khi tạo/cập nhật `Service`, phải xác thực `category_id` tồn tại trong bảng `ServiceCategory`.
- **Logic thiết lập ảnh chính:** Endpoint `set-primary-image` phải xác thực `media_id` thuộc về `service_id` trước khi cập nhật trường `primary_image_id`.
