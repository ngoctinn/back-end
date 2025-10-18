"""CRUD operations cho module services (catalog)."""

from typing import List, Optional, Type

from sqlmodel import Session, select, func

from . import models, schemas

# --- ProductCategory CRUD ---

def create_product_category(
    db: Session, *, category_in: schemas.ProductCategoryCreate
) -> models.ProductCategory:
    """Tạo mới danh mục sản phẩm."""
    db_category = models.ProductCategory.model_validate(category_in)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_product_category(db: Session, category_id: int) -> Optional[models.ProductCategory]:
    """Lấy danh mục sản phẩm theo ID."""
    return db.get(models.ProductCategory, category_id)

def get_all_product_categories(
    db: Session, *, skip: int = 0, limit: int = 100
) -> List[models.ProductCategory]:
    """Lấy tất cả danh mục sản phẩm."""
    statement = select(models.ProductCategory).offset(skip).limit(limit)
    return db.exec(statement).all()

def update_product_category(
    db: Session, *, db_category: models.ProductCategory, category_in: schemas.ProductCategoryUpdate
) -> models.ProductCategory:
    """Cập nhật danh mục sản phẩm."""
    update_data = category_in.model_dump(exclude_unset=True)
    db_category.sqlmodel_update(update_data)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_product_category(db: Session, *, category_id: int) -> None:
    """Xóa danh mục sản phẩm."""
    category = db.get(models.ProductCategory, category_id)
    if category:
        db.delete(category)
        db.commit()

# --- Product CRUD ---

def create_product(db: Session, *, product_in: schemas.ProductCreate) -> models.Product:
    """Tạo mới sản phẩm."""
    db_product = models.Product.model_validate(product_in)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    """Lấy sản phẩm theo ID."""
    return db.get(models.Product, product_id)

def get_all_products(
    db: Session, *, skip: int = 0, limit: int = 100
) -> List[models.Product]:
    """Lấy tất cả sản phẩm."""
    statement = select(models.Product).offset(skip).limit(limit)
    return db.exec(statement).all()

def update_product(
    db: Session, *, db_product: models.Product, product_in: schemas.ProductUpdate
) -> models.Product:
    """Cập nhật sản phẩm."""
    update_data = product_in.model_dump(exclude_unset=True)
    db_product.sqlmodel_update(update_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, *, product_id: int) -> None:
    """Xóa sản phẩm."""
    product = db.get(models.Product, product_id)
    if product:
        db.delete(product)
        db.commit()

def set_primary_image_for_product(
    db: Session, *, product: models.Product, media_id: int
) -> models.Product:
    """Thiết lập ảnh chính cho sản phẩm."""
    product.primary_image_id = media_id
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


# --- ServiceCategory CRUD ---

def create_service_category(
    db: Session, *, category_in: schemas.ServiceCategoryCreate
) -> models.ServiceCategory:
    """Tạo mới danh mục dịch vụ."""
    db_category = models.ServiceCategory.model_validate(category_in)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_service_category(db: Session, category_id: int) -> Optional[models.ServiceCategory]:
    """Lấy danh mục dịch vụ theo ID."""
    return db.get(models.ServiceCategory, category_id)

def get_all_service_categories(
    db: Session, *, skip: int = 0, limit: int = 100
) -> List[models.ServiceCategory]:
    """Lấy tất cả danh mục dịch vụ."""
    statement = select(models.ServiceCategory).offset(skip).limit(limit)
    return db.exec(statement).all()

def update_service_category(
    db: Session, *, db_category: models.ServiceCategory, category_in: schemas.ServiceCategoryUpdate
) -> models.ServiceCategory:
    """Cập nhật danh mục dịch vụ."""
    update_data = category_in.model_dump(exclude_unset=True)
    db_category.sqlmodel_update(update_data)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_service_category(db: Session, *, category_id: int) -> None:
    """Xóa danh mục dịch vụ."""
    category = db.get(models.ServiceCategory, category_id)
    if category:
        db.delete(category)
        db.commit()

# --- Service CRUD ---

def create_service(db: Session, *, service_in: schemas.ServiceCreate) -> models.Service:
    """Tạo mới dịch vụ."""
    db_service = models.Service.model_validate(service_in)
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def get_service(db: Session, service_id: int) -> Optional[models.Service]:
    """Lấy dịch vụ theo ID."""
    return db.get(models.Service, service_id)

def get_all_services(
    db: Session, *, skip: int = 0, limit: int = 100
) -> List[models.Service]:
    """Lấy tất cả dịch vụ."""
    statement = select(models.Service).offset(skip).limit(limit)
    return db.exec(statement).all()

def update_service(
    db: Session, *, db_service: models.Service, service_in: schemas.ServiceUpdate
) -> models.Service:
    """Cập nhật dịch vụ."""
    update_data = service_in.model_dump(exclude_unset=True)
    db_service.sqlmodel_update(update_data)
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def delete_service(db: Session, *, service_id: int) -> None:
    """Xóa dịch vụ."""
    service = db.get(models.Service, service_id)
    if service:
        db.delete(service)
        db.commit()

def set_primary_image_for_service(
    db: Session, *, service: models.Service, media_id: int
) -> models.Service:
    """Thiết lập ảnh chính cho dịch vụ."""
    service.primary_image_id = media_id
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


# --- ServiceProductConsumption CRUD ---

def get_consumption_link(
    db: Session, *, service_id: int, product_id: int
) -> Optional[models.ServiceProductConsumption]:
    """Lấy một liên kết vật tư tiêu hao cụ thể."""
    return db.get(models.ServiceProductConsumption, (service_id, product_id))

def add_consumption_to_service(
    db: Session, *, service: models.Service, consumption_in: schemas.ServiceConsumptionCreate
) -> models.Service:
    """Thêm hoặc cập nhật một sản phẩm tiêu hao cho dịch vụ."""
    # Kiểm tra xem liên kết đã tồn tại chưa
    link = get_consumption_link(db, service_id=service.id, product_id=consumption_in.product_id)
    if link:
        # Cập nhật nếu đã tồn tại
        link.consumed_quantity = consumption_in.consumed_quantity
        link.unit = consumption_in.unit
    else:
        # Tạo mới nếu chưa tồn tại
        link = models.ServiceProductConsumption.model_validate(consumption_in, update={"service_id": service.id})
    
    db.add(link)
    db.commit()
    db.refresh(service) # Refresh service để thấy thay đổi trong relationship
    return service

def remove_consumption_from_service(
    db: Session, *, service: models.Service, product_id: int
) -> models.Service:
    """Xóa một sản phẩm tiêu hao khỏi dịch vụ."""
    link = get_consumption_link(db, service_id=service.id, product_id=product_id)
    if link:
        db.delete(link)
        db.commit()
        db.refresh(service)
    return service

def get_consumptions_for_service(
    db: Session, *, service_id: int
) -> List[models.ServiceProductConsumption]:
    """Lấy danh sách tất cả vật tư tiêu hao của một dịch vụ."""
    statement = select(models.ServiceProductConsumption).where(models.ServiceProductConsumption.service_id == service_id)
    return db.exec(statement).all()


# --- PackageCategory CRUD ---

def create_package_category(
    db: Session, *, category_in: schemas.PackageCategoryCreate
) -> models.PackageCategory:
    db_category = models.PackageCategory.model_validate(category_in)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_package_category(db: Session, category_id: int) -> Optional[models.PackageCategory]:
    return db.get(models.PackageCategory, category_id)

# --- ServicePackage CRUD ---

def create_service_package(
    db: Session, *, package_in: schemas.ServicePackageCreate
) -> models.ServicePackage:
    """Tạo mới gói liệu trình và liên kết các dịch vụ."""
    package_data = package_in.model_dump(exclude={"service_ids"})
    db_package = models.ServicePackage.model_validate(package_data)

    # Tìm và liên kết các dịch vụ
    if package_in.service_ids:
        services = db.exec(select(models.Service).where(models.Service.id.in_(package_in.service_ids))).all()
        if len(services) != len(package_in.service_ids):
            raise ValueError("Một hoặc nhiều ID dịch vụ không hợp lệ")
        db_package.services = services

    db.add(db_package)
    db.commit()
    db.refresh(db_package)
    return db_package

def get_service_package(db: Session, package_id: int) -> Optional[models.ServicePackage]:
    """Lấy gói liệu trình theo ID."""
    return db.get(models.ServicePackage, package_id)

def update_service_package(
    db: Session, *, db_package: models.ServicePackage, package_in: schemas.ServicePackageUpdate
) -> models.ServicePackage:
    """Cập nhật gói liệu trình, bao gồm cả danh sách dịch vụ."""
    update_data = package_in.model_dump(exclude_unset=True, exclude={"service_ids"})
    db_package.sqlmodel_update(update_data)

    # Cập nhật danh sách dịch vụ nếu được cung cấp
    if package_in.service_ids is not None:
        services = db.exec(select(models.Service).where(models.Service.id.in_(package_in.service_ids))).all()
        if len(services) != len(package_in.service_ids):
            raise ValueError("Một hoặc nhiều ID dịch vụ không hợp lệ")
        db_package.services = services

    db.add(db_package)
    db.commit()
    db.refresh(db_package)
    return db_package

def set_primary_image_for_service_package(
    db: Session, *, package: models.ServicePackage, media_id: int
) -> models.ServicePackage:
    """Thiết lập ảnh chính cho gói liệu trình."""
    package.primary_image_id = media_id
    db.add(package)
    db.commit()
    db.refresh(package)
    return package
