"""Các model CSDL cho module catalog.

Định nghĩa các bảng cho sản phẩm, dịch vụ, gói và các danh mục liên quan.
"""

from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel, Column, JSON

# --- BƯỚC 1: ĐỊNH NGHĨA CÁC BẢNG DANH MỤC (CATEGORY TABLES) ---

class ProductCategory(SQLModel, table=True):
    """Model Danh mục sản phẩm."""
    __tablename__ = "productcategory"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    description: str = Field(default="")
    products: List["Product"] = Relationship(back_populates="category")

class ServiceCategory(SQLModel, table=True):
    """Model Danh mục dịch vụ."""
    __tablename__ = "servicecategory"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    description: str = Field(default="")
    services: List["Service"] = Relationship(back_populates="category")

class PackageCategory(SQLModel, table=True):
    """Model Danh mục Gói liệu trình."""
    __tablename__ = "packagecategory"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    description: str = Field(default="")
    packages: List["ServicePackage"] = Relationship(back_populates="category")


# --- BƯỚC 2: ĐỊNH NGHĨA CÁC BẢNG TRUNG GIAN (LINK TABLES) ---

class ServiceProductConsumption(SQLModel, table=True):
    """Bảng trung gian cho mối quan hệ Nhiều-Nhiều Service-Product."""
    service_id: Optional[int] = Field(default=None, foreign_key="service.id", primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id", primary_key=True)
    consumed_quantity: float
    unit: str = Field(max_length=50)

class PackageServiceLink(SQLModel, table=True):
    """Bảng trung gian cho mối quan hệ Nhiều-Nhiều Service-Package."""
    package_id: Optional[int] = Field(default=None, foreign_key="servicepackage.id", primary_key=True)
    service_id: Optional[int] = Field(default=None, foreign_key="service.id", primary_key=True)


# --- BƯỚC 3: ĐỊNH NGHĨA CÁC BẢNG CHÍNH (MAIN TABLES) ---

class Product(SQLModel, table=True):
    """Model Sản phẩm."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    sku: str = Field(unique=True, index=True, max_length=100)
    barcode: Optional[str] = Field(default=None, unique=True, index=True, max_length=100)
    brand: Optional[str] = Field(default=None, max_length=255)
    description: str = Field(default="")
    product_type: str = Field(index=True, max_length=50)
    purchase_price: float = Field(default=0.0)
    price: float
    stock_unit: str = Field(max_length=50)
    stock_quantity: float = Field(default=0.0)
    low_stock_threshold: float = Field(default=0.0)
    category_id: Optional[int] = Field(default=None, foreign_key="productcategory.id")
    primary_image_id: Optional[int] = Field(default=None, foreign_key="mediafile.id")
    category: Optional[ProductCategory] = Relationship(back_populates="products")
    consumed_in_services: List["Service"] = Relationship(back_populates="consumes_products", link_model=ServiceProductConsumption)

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
    category_id: Optional[int] = Field(default=None, foreign_key="servicecategory.id")
    primary_image_id: Optional[int] = Field(default=None, foreign_key="mediafile.id")
    category: Optional[ServiceCategory] = Relationship(back_populates="services")
    consumes_products: List[Product] = Relationship(back_populates="consumed_in_services", link_model=ServiceProductConsumption)
    packages: List["ServicePackage"] = Relationship(back_populates="services", link_model=PackageServiceLink)

class ServicePackage(SQLModel, table=True):
    """Model Gói liệu trình."""
    __tablename__ = "servicepackage"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    description: str = Field(default="")
    total_price: float
    validity_period_days: int
    terms_and_conditions: str = Field(default="")
    category_id: Optional[int] = Field(default=None, foreign_key="packagecategory.id")
    primary_image_id: Optional[int] = Field(default=None, foreign_key="mediafile.id")
    category: Optional[PackageCategory] = Relationship(back_populates="packages")
    services: List[Service] = Relationship(back_populates="packages", link_model=PackageServiceLink)