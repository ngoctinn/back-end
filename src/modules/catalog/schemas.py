"""Các schema Pydantic cho module services (catalog)."""

from typing import List, Optional
from pydantic import BaseModel, Field

# LƯU Ý: Các schema khác sẽ được thêm vào file này trong các kế hoạch sau.

# --- Schemas cho Kế hoạch 6.1: Sản phẩm ---

# --- ProductCategory Schemas ---
class ProductCategoryBase(BaseModel):
    """Schema cơ bản cho danh mục sản phẩm."""
    name: str = Field(max_length=255, description="Tên danh mục")
    description: str = Field(default="", description="Mô tả chi tiết")

class ProductCategoryCreate(ProductCategoryBase):
    """Schema để tạo mới danh mục sản phẩm."""
    pass

class ProductCategoryUpdate(BaseModel):
    """Schema để cập nhật danh mục sản phẩm."""
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None

class ProductCategoryRead(ProductCategoryBase):
    """Schema để đọc thông tin danh mục sản phẩm."""
    id: int

    class Config:
        from_attributes = True

# --- Product Schemas ---
class ProductBase(BaseModel):
    """Schema cơ bản cho sản phẩm."""
    name: str = Field(max_length=255)
    sku: str = Field(max_length=100)
    barcode: Optional[str] = Field(default=None, max_length=100)
    brand: Optional[str] = Field(default=None, max_length=255)
    description: str = ""
    product_type: str = Field(max_length=50)
    purchase_price: float = 0.0
    price: float
    stock_unit: str = Field(max_length=50)
    stock_quantity: float = 0.0
    low_stock_threshold: float = 0.0
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    """Schema để tạo mới sản phẩm."""
    pass

class ProductUpdate(BaseModel):
    """Schema để cập nhật sản phẩm."""
    name: Optional[str] = Field(default=None, max_length=255)
    sku: Optional[str] = Field(default=None, max_length=100)
    barcode: Optional[str] = Field(default=None, max_length=100)
    brand: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    product_type: Optional[str] = Field(default=None, max_length=50)
    purchase_price: Optional[float] = None
    price: Optional[float] = None
    stock_unit: Optional[str] = Field(default=None, max_length=50)
    stock_quantity: Optional[float] = None
    low_stock_threshold: Optional[float] = None
    category_id: Optional[int] = None

class ProductRead(ProductBase):
    """Schema để đọc thông tin sản phẩm."""
    id: int
    primary_image_id: Optional[int] = None
    category: Optional[ProductCategoryRead] = None
    # Thêm trường primary_image sau khi có MediaResponse
    # primary_image: Optional[MediaResponse] = None 

    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    """Response danh sách sản phẩm."""
    products: List[ProductRead]
    total: int


# --- Schemas cho Kế hoạch 6.2: Dịch vụ ---

# --- ServiceCategory Schemas ---
class ServiceCategoryBase(BaseModel):
    """Schema cơ bản cho danh mục dịch vụ."""
    name: str = Field(max_length=255, description="Tên danh mục")
    description: str = Field(default="", description="Mô tả chi tiết")

class ServiceCategoryCreate(ServiceCategoryBase):
    """Schema để tạo mới danh mục dịch vụ."""
    pass

class ServiceCategoryUpdate(BaseModel):
    """Schema để cập nhật danh mục dịch vụ."""
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None

class ServiceCategoryRead(ServiceCategoryBase):
    """Schema để đọc thông tin danh mục dịch vụ."""
    id: int

    class Config:
        from_attributes = True

# --- Service Schemas ---
class ServiceBase(BaseModel):
    """Schema cơ bản cho dịch vụ."""
    name: str = Field(max_length=255)
    description: str = ""
    price: float
    duration_minutes: int
    buffer_time_after: int = 0
    is_bookable_online: bool = True
    color_code: str = Field(default="#FFFFFF", max_length=7)
    required_resources: List[str] = []
    required_staff_skills: List[str] = []
    category_id: Optional[int] = None

class ServiceCreate(ServiceBase):
    """Schema để tạo mới dịch vụ."""
    pass

class ServiceUpdate(BaseModel):
    """Schema để cập nhật dịch vụ."""
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = None
    duration_minutes: Optional[int] = None
    buffer_time_after: Optional[int] = None
    is_bookable_online: Optional[bool] = None
    color_code: Optional[str] = Field(default=None, max_length=7)
    required_resources: Optional[List[str]] = None
    required_staff_skills: Optional[List[str]] = None
    category_id: Optional[int] = None

class ServiceRead(ServiceBase):
    """Schema để đọc thông tin dịch vụ."""
    id: int
    primary_image_id: Optional[int] = None
    category: Optional[ServiceCategoryRead] = None
    consumptions: List["ServiceConsumptionRead"] = [] # Cập nhật để hiển thị vật tư tiêu hao

    class Config:
        from_attributes = True


# --- Schemas cho Kế hoạch 6.3: Vật tư tiêu hao ---

class ServiceConsumptionBase(BaseModel):
    """Schema cơ bản cho liên kết vật tư tiêu hao."""
    product_id: int
    consumed_quantity: float
    unit: str = Field(max_length=50)

class ServiceConsumptionCreate(ServiceConsumptionBase):
    """Schema để tạo mới một liên kết vật tư tiêu hao."""
    pass

class ServiceConsumptionRead(ServiceConsumptionBase):
    """Schema để đọc thông tin một liên kết vật tư tiêu hao."""
    service_id: int
    product: ProductRead # Lồng thông tin sản phẩm để hiển thị chi tiết

    class Config:
        from_attributes = True


# --- Schemas cho Kế hoạch 6.4: Gói liệu trình ---

# --- PackageCategory Schemas ---
class PackageCategoryBase(BaseModel):
    """Schema cơ bản cho danh mục gói liệu trình."""
    name: str = Field(max_length=255)
    description: str = ""

class PackageCategoryCreate(PackageCategoryBase):
    pass

class PackageCategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None

class PackageCategoryRead(PackageCategoryBase):
    id: int

    class Config:
        from_attributes = True

# --- ServicePackage Schemas ---
class ServicePackageBase(BaseModel):
    """Schema cơ bản cho gói liệu trình."""
    name: str = Field(max_length=255)
    description: str = ""
    total_price: float
    validity_period_days: int
    terms_and_conditions: str = ""
    category_id: Optional[int] = None

class ServicePackageCreate(ServicePackageBase):
    """Schema để tạo mới gói liệu trình, nhận vào danh sách ID của dịch vụ."""
    service_ids: List[int] = []

class ServicePackageUpdate(BaseModel):
    """Schema để cập nhật gói liệu trình."""
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    total_price: Optional[float] = None
    validity_period_days: Optional[int] = None
    terms_and_conditions: Optional[str] = None
    category_id: Optional[int] = None
    service_ids: Optional[List[int]] = None

class ServicePackageRead(ServicePackageBase):
    """Schema để đọc thông tin gói liệu trình, bao gồm các dịch vụ con."""
    id: int
    primary_image_id: Optional[int] = None
    category: Optional[PackageCategoryRead] = None
    services: List[ServiceRead] = []

    class Config:
        from_attributes = True
