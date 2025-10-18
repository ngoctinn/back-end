"""Các model CSDL cho module services (catalog).

Định nghĩa các bảng cho sản phẩm, dịch vụ, gói và các danh mục liên quan.
"""

from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel, Column, JSON

# LƯU Ý: Các model khác như Service, ServiceCategory, ServicePackage...
# sẽ được thêm vào file này trong các kế hoạch triển khai tiếp theo.

# --- Models cho Kế hoạch 6.1: Sản phẩm ---

class ProductCategory(SQLModel, table=True):
    """Model Danh mục sản phẩm."""
    __tablename__ = "productcategory"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    description: str = Field(default="")

    # Mối quan hệ một-nhiều với Product
    products: List["Product"] = Relationship(back_populates="category")


class Product(SQLModel, table=True):
    """Model Sản phẩm."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    sku: str = Field(unique=True, index=True, max_length=100)
    barcode: Optional[str] = Field(default=None, unique=True, index=True, max_length=100)
    brand: Optional[str] = Field(default=None, max_length=255)
    description: str = Field(default="")
    product_type: str = Field(index=True, max_length=50)  # 'RETAIL' hoặc 'PROFESSIONAL'
    purchase_price: float = Field(default=0.0)
    price: float
    stock_unit: str = Field(max_length=50)  # ví dụ: 'ml', 'g', 'item'
    stock_quantity: float = Field(default=0.0)
    low_stock_threshold: float = Field(default=0.0)

    # Khóa ngoại tới ProductCategory
    category_id: Optional[int] = Field(default=None, foreign_key="productcategory.id")
    
    # Khóa ngoại tới MediaFile cho ảnh chính
    primary_image_id: Optional[int] = Field(default=None, foreign_key="mediafile.id")

    # Mối quan hệ nhiều-một với ProductCategory
    category: Optional[ProductCategory] = Relationship(back_populates="products")


# --- Models cho Kế hoạch 6.2: Dịch vụ ---

class ServiceCategory(SQLModel, table=True):
    """Model Danh mục dịch vụ."""
    __tablename__ = "servicecategory"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    description: str = Field(default="")

    # Mối quan hệ một-nhiều với Service
    services: List["Service"] = Relationship(back_populates="category")


class Service(SQLModel, table=True):
    """Model Dịch vụ."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    description: str = Field(default="")
    price: float
    duration_minutes: int
    buffer_time_after: int = Field(default=0)
    is_bookable_online: bool = Field(default=True)
    color_code: str = Field(default="#FFFFFF", max_length=7)
    required_resources: List[str] = Field(sa_column=Column(JSON), default_factory=list)
    required_staff_skills: List[str] = Field(sa_column=Column(JSON), default_factory=list)

    # Khóa ngoại tới ServiceCategory
    category_id: Optional[int] = Field(default=None, foreign_key="servicecategory.id")

    # Khóa ngoại tới MediaFile cho ảnh chính
    primary_image_id: Optional[int] = Field(default=None, foreign_key="mediafile.id")

    # Mối quan hệ nhiều-một với ServiceCategory
    category: Optional[ServiceCategory] = Relationship(back_populates="services")
