"""API Endpoints cho module services (catalog)."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.core.db import get_session
from src.modules.media.models import MediaFile

from . import crud, schemas

# Khởi tạo router chính cho module services
# Các router cho service, package sẽ được thêm vào sau
router = APIRouter(prefix="/catalog", tags=["Catalog"])

# === Endpoints for ProductCategory ===

@router.post(
    "/product-categories/",
    response_model=schemas.ProductCategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mới Danh mục Sản phẩm"
)
def create_product_category(
    *, session: Session = Depends(get_session), category_in: schemas.ProductCategoryCreate
):
    """Tạo một danh mục sản phẩm mới."""
    return crud.create_product_category(db=session, category_in=category_in)

@router.get(
    "/product-categories/",
    response_model=List[schemas.ProductCategoryRead],
    summary="Lấy danh sách Danh mục Sản phẩm"
)
def read_product_categories(
    *, session: Session = Depends(get_session), skip: int = 0, limit: int = 100
):
    """Lấy danh sách tất cả các danh mục sản phẩm."""
    return crud.get_all_product_categories(db=session, skip=skip, limit=limit)

@router.get(
    "/product-categories/{category_id}",
    response_model=schemas.ProductCategoryRead,
    summary="Lấy thông tin một Danh mục Sản phẩm"
)
def read_product_category(*, session: Session = Depends(get_session), category_id: int):
    """Lấy thông tin chi tiết của một danh mục sản phẩm bằng ID."""
    db_category = crud.get_product_category(db=session, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Danh mục sản phẩm không tồn tại")
    return db_category

@router.put(
    "/product-categories/{category_id}",
    response_model=schemas.ProductCategoryRead,
    summary="Cập nhật Danh mục Sản phẩm"
)
def update_product_category(
    *, session: Session = Depends(get_session), category_id: int, category_in: schemas.ProductCategoryUpdate
):
    """Cập nhật thông tin một danh mục sản phẩm."""
    db_category = crud.get_product_category(db=session, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Danh mục sản phẩm không tồn tại")
    return crud.update_product_category(db=session, db_category=db_category, category_in=category_in)

@router.delete(
    "/product-categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa Danh mục Sản phẩm"
)
def delete_product_category(*, session: Session = Depends(get_session), category_id: int):
    """Xóa một danh mục sản phẩm."""
    db_category = crud.get_product_category(db=session, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Danh mục sản phẩm không tồn tại")
    crud.delete_product_category(db=session, category_id=category_id)
    return

# === Endpoints for Product ===

@router.post(
    "/products/",
    response_model=schemas.ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mới Sản phẩm"
)
def create_product(*, session: Session = Depends(get_session), product_in: schemas.ProductCreate):
    """Tạo một sản phẩm mới."""
    # Logic xác thực category_id
    if product_in.category_id:
        category = crud.get_product_category(db=session, category_id=product_in.category_id)
        if not category:
            raise HTTPException(status_code=404, detail=f"Danh mục sản phẩm ID {product_in.category_id} không tồn tại")
    return crud.create_product(db=session, product_in=product_in)

@router.get(
    "/products/",
    response_model=List[schemas.ProductRead],
    summary="Lấy danh sách Sản phẩm"
)
def read_products(*, session: Session = Depends(get_session), skip: int = 0, limit: int = 100):
    """Lấy danh sách tất cả các sản phẩm."""
    return crud.get_all_products(db=session, skip=skip, limit=limit)

@router.get(
    "/products/{product_id}",
    response_model=schemas.ProductRead,
    summary="Lấy thông tin một Sản phẩm"
)
def read_product(*, session: Session = Depends(get_session), product_id: int):
    """Lấy thông tin chi tiết của một sản phẩm bằng ID."""
    db_product = crud.get_product(db=session, product_id=product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    return db_product

@router.put(
    "/products/{product_id}",
    response_model=schemas.ProductRead,
    summary="Cập nhật Sản phẩm"
)
def update_product(
    *, session: Session = Depends(get_session), product_id: int, product_in: schemas.ProductUpdate
):
    """Cập nhật thông tin một sản phẩm."""
    db_product = crud.get_product(db=session, product_id=product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    # Logic xác thực category_id nếu nó được cập nhật
    if product_in.category_id:
        category = crud.get_product_category(db=session, category_id=product_in.category_id)
        if not category:
            raise HTTPException(status_code=404, detail=f"Danh mục sản phẩm ID {product_in.category_id} không tồn tại")
    return crud.update_product(db=session, db_product=db_product, product_in=product_in)

@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa Sản phẩm"
)
def delete_product(*, session: Session = Depends(get_session), product_id: int):
    """Xóa một sản phẩm."""
    db_product = crud.get_product(db=session, product_id=product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    crud.delete_product(db=session, product_id=product_id)
    return

@router.post(
    "/products/{product_id}/set-primary-image/{media_id}",
    response_model=schemas.ProductRead,
    summary="Thiết lập ảnh đại diện cho sản phẩm"
)
def set_primary_image_for_product(
    *, session: Session = Depends(get_session), product_id: int, media_id: int
):
    """Thiết lập một ảnh có sẵn làm ảnh đại diện cho sản phẩm."""
    db_product = crud.get_product(db=session, product_id=product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    
    media_file = session.get(MediaFile, media_id)
    if not media_file:
        raise HTTPException(status_code=404, detail="Ảnh không tồn tại")

    # Kiểm tra xem ảnh có thuộc về sản phẩm này không
    if not (media_file.related_entity_type == 'product' and media_file.related_entity_id == product_id):
        raise HTTPException(status_code=400, detail="Ảnh không thuộc về sản phẩm này")

    return crud.set_primary_image_for_product(db=session, product=db_product, media_id=media_id)


# === Endpoints for ServiceCategory ===

@router.post(
    "/service-categories/",
    response_model=schemas.ServiceCategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mới Danh mục Dịch vụ"
)
def create_service_category(
    *, session: Session = Depends(get_session), category_in: schemas.ServiceCategoryCreate
):
    return crud.create_service_category(db=session, category_in=category_in)

@router.get(
    "/service-categories/",
    response_model=List[schemas.ServiceCategoryRead],
    summary="Lấy danh sách Danh mục Dịch vụ"
)
def read_service_categories(
    *, session: Session = Depends(get_session), skip: int = 0, limit: int = 100
):
    return crud.get_all_service_categories(db=session, skip=skip, limit=limit)

@router.get(
    "/service-categories/{category_id}",
    response_model=schemas.ServiceCategoryRead,
    summary="Lấy thông tin một Danh mục Dịch vụ"
)
def read_service_category(*, session: Session = Depends(get_session), category_id: int):
    db_category = crud.get_service_category(db=session, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Danh mục dịch vụ không tồn tại")
    return db_category

@router.put(
    "/service-categories/{category_id}",
    response_model=schemas.ServiceCategoryRead,
    summary="Cập nhật Danh mục Dịch vụ"
)
def update_service_category(
    *, session: Session = Depends(get_session), category_id: int, category_in: schemas.ServiceCategoryUpdate
):
    db_category = crud.get_service_category(db=session, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Danh mục dịch vụ không tồn tại")
    return crud.update_service_category(db=session, db_category=db_category, category_in=category_in)

@router.delete(
    "/service-categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa Danh mục Dịch vụ"
)
def delete_service_category(*, session: Session = Depends(get_session), category_id: int):
    db_category = crud.get_service_category(db=session, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Danh mục dịch vụ không tồn tại")
    crud.delete_service_category(db=session, category_id=category_id)
    return

# === Endpoints for Service ===

@router.post(
    "/services/",
    response_model=schemas.ServiceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mới Dịch vụ"
)
def create_service(*, session: Session = Depends(get_session), service_in: schemas.ServiceCreate):
    if service_in.category_id:
        category = crud.get_service_category(db=session, category_id=service_in.category_id)
        if not category:
            raise HTTPException(status_code=404, detail=f"Danh mục dịch vụ ID {service_in.category_id} không tồn tại")
    return crud.create_service(db=session, service_in=service_in)

@router.get(
    "/services/",
    response_model=List[schemas.ServiceRead],
    summary="Lấy danh sách Dịch vụ"
)
def read_services(*, session: Session = Depends(get_session), skip: int = 0, limit: int = 100):
    return crud.get_all_services(db=session, skip=skip, limit=limit)

@router.get(
    "/services/{service_id}",
    response_model=schemas.ServiceRead,
    summary="Lấy thông tin một Dịch vụ"
)
def read_service(*, session: Session = Depends(get_session), service_id: int):
    db_service = crud.get_service(db=session, service_id=service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Dịch vụ không tồn tại")
    return db_service

@router.put(
    "/services/{service_id}",
    response_model=schemas.ServiceRead,
    summary="Cập nhật Dịch vụ"
)
def update_service(
    *, session: Session = Depends(get_session), service_id: int, service_in: schemas.ServiceUpdate
):
    db_service = crud.get_service(db=session, service_id=service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Dịch vụ không tồn tại")
    if service_in.category_id:
        category = crud.get_service_category(db=session, category_id=service_in.category_id)
        if not category:
            raise HTTPException(status_code=404, detail=f"Danh mục dịch vụ ID {service_in.category_id} không tồn tại")
    return crud.update_service(db=session, db_service=db_service, service_in=service_in)

@router.delete(
    "/services/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa Dịch vụ"
)
def delete_service(*, session: Session = Depends(get_session), service_id: int):
    db_service = crud.get_service(db=session, service_id=service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Dịch vụ không tồn tại")
    crud.delete_service(db=session, service_id=service_id)
    return

@router.post(
    "/services/{service_id}/set-primary-image/{media_id}",
    response_model=schemas.ServiceRead,
    summary="Thiết lập ảnh đại diện cho dịch vụ"
)
def set_primary_image_for_service(
    *, session: Session = Depends(get_session), service_id: int, media_id: int
):
    db_service = crud.get_service(db=session, service_id=service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Dịch vụ không tồn tại")
    
    media_file = session.get(MediaFile, media_id)
    if not media_file:
        raise HTTPException(status_code=404, detail="Ảnh không tồn tại")

    if not (media_file.related_entity_type == 'service' and media_file.related_entity_id == service_id):
        raise HTTPException(status_code=400, detail="Ảnh không thuộc về dịch vụ này")

    return crud.set_primary_image_for_service(db=session, service=db_service, media_id=media_id)
