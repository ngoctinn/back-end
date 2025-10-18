"""Xác thực rằng module media đã được triển khai thành công."""

from src.modules.media import models, schemas, crud, service, router
from src.core import storage


def test_all_modules_imported():
    """Kiểm tra tất cả module media có thể import được."""
    assert models is not None
    assert schemas is not None
    assert crud is not None
    assert service is not None
    assert router is not None
    assert storage is not None


def test_models_exist():
    """Kiểm tra các model được định nghĩa."""
    assert hasattr(models, "MediaFile")


def test_schemas_exist():
    """Kiểm tra các schema được định nghĩa."""
    assert hasattr(schemas, "MediaResponse")
    assert hasattr(schemas, "MediaListResponse")
    assert hasattr(schemas, "DeleteMessageResponse")


def test_crud_functions_exist():
    """Kiểm tra các hàm CRUD được định nghĩa."""
    assert hasattr(crud, "create_media_record")
    assert hasattr(crud, "get_media_by_id")
    assert hasattr(crud, "get_media_list_by_entity")
    assert hasattr(crud, "delete_media_record")


def test_service_functions_exist():
    """Kiểm tra các hàm service được định nghĩa."""
    assert hasattr(service, "upload_avatar_for_customer")
    assert hasattr(service, "upload_image_for_service")
    assert hasattr(service, "delete_media_file")
    assert hasattr(service, "get_media_for_entity")


def test_router_endpoints_exist():
    """Kiểm tra các endpoint được định nghĩa."""
    assert hasattr(router, "router")


def test_storage_functions_exist():
    """Kiểm tra các hàm storage được định nghĩa."""
    assert hasattr(storage, "get_storage_client")
    assert hasattr(storage, "upload_file_to_storage")
    assert hasattr(storage, "delete_file_from_storage")
    assert hasattr(storage, "get_public_url")
