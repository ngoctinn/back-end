"""Khởi tạo Supabase client và xử lý thao tác lưu trữ file.

Module này cung cấp các hàm tiện ích để tương tác với Supabase Storage,
bao gồm tải lên, xóa và lấy URL công khai của file.
"""

import logging
from typing import BinaryIO, Optional

from supabase import create_client, Client

from src.core.config import settings

logger = logging.getLogger(__name__)

# Biến toàn cục để lưu trữ client singleton
_storage_client: Optional[Client] = None


def get_storage_client() -> Client:
    """Khởi tạo và trả về Supabase client (singleton).

    Sử dụng caching để tái sử dụng client và tránh tạo lại nhiều lần.

    Returns:
        Client: Supabase client instance

    Raises:
        Exception: Nếu không thể kết nối tới Supabase
    """
    global _storage_client

    if _storage_client is None:
        try:
            _storage_client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_KEY,
            )
            logger.info("✓ Kết nối Supabase thành công")
        except Exception as e:
            logger.error(f"✗ Lỗi kết nối Supabase: {str(e)}")
            raise

    return _storage_client


def upload_file_to_storage(
    file: BinaryIO, file_path: str, content_type: Optional[str] = None
) -> str:
    """Tải file lên Supabase Storage.

    Args:
        file: File object từ UploadFile.file
        file_path: Đường dẫn đích trong bucket (ví dụ: customers/123/avatar.jpg)
        content_type: MIME type của file (tùy chọn)

    Returns:
        str: URL công khai của file vừa tải lên

    Raises:
        Exception: Nếu tải lên thất bại
    """
    try:
        client = get_storage_client()

        # Đọc nội dung file
        file_content = file.read()
        file.seek(0)  # Reset pointer để có thể đọc lại nếu cần

        # Tải lên Supabase Storage
        response = client.storage.from_(settings.SUPABASE_BUCKET_NAME).upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": content_type},
        )

        logger.info(f"✓ Tải file lên thành công: {file_path}")

        # Lấy URL công khai
        public_url = get_public_url(file_path)
        return public_url

    except Exception as e:
        logger.error(f"✗ Lỗi tải file: {str(e)}")
        raise


def delete_file_from_storage(file_path: str) -> bool:
    """Xóa file khỏi Supabase Storage.

    Args:
        file_path: Đường dẫn file trong bucket

    Returns:
        bool: True nếu xóa thành công

    Raises:
        Exception: Nếu file không tìm thấy hoặc xóa thất bại
    """
    try:
        client = get_storage_client()

        # Xóa file từ Supabase Storage
        client.storage.from_(settings.SUPABASE_BUCKET_NAME).remove([file_path])

        logger.info(f"✓ Xóa file thành công: {file_path}")
        return True

    except Exception as e:
        logger.error(f"✗ Lỗi xóa file: {str(e)}")
        raise


def get_public_url(file_path: str) -> str:
    """Lấy URL công khai của file trong Supabase Storage.

    Args:
        file_path: Đường dẫn file trong bucket

    Returns:
        str: URL công khai đầy đủ

    Raises:
        Exception: Nếu không thể tạo URL
    """
    try:
        client = get_storage_client()

        # Lấy URL công khai
        public_url = client.storage.from_(settings.SUPABASE_BUCKET_NAME).get_public_url(
            file_path
        )

        logger.info(f"✓ Lấy URL công khai: {public_url}")
        return public_url

    except Exception as e:
        logger.error(f"✗ Lỗi lấy URL: {str(e)}")
        raise
