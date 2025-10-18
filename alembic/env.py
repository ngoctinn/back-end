from logging.config import fileConfig
import sys
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Thêm dự án vào sys.path để import các module tùy chỉnh
sys.path.insert(0, str(Path(__file__).parent.parent))

# Lấy Alembic Config object
config = context.config

# Thiết lập logging từ tệp cấu hình
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import settings và metadata từ ứng dụng FastAPI
from src.core.config import settings
from sqlmodel import SQLModel

# Import tất cả các model để Alembic có thể phát hiện chúng
# ⚠️ Khi thêm module/model mới, phải thêm import ở đây!
from src.modules.auth.models import (
    User,
    RefreshToken,
    VerificationToken,
    ResetPasswordToken,
)
from src.modules.customers.models import Customer
from src.modules.media.models import MediaFile
from src.modules.catalog import models

# Đặt target_metadata từ ứng dụng FastAPI (dùng để autogenerate)
target_metadata = SQLModel.metadata

# Đặt sqlalchemy.url từ settings (lấy từ .env)
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Chạy migrations ở chế độ 'offline' (không cần kết nối DB).

    Chế độ này chỉ cấu hình context với URL, không tạo Engine.
    Dùng để sinh ra SQL migrations mà không thực thi trực tiếp.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Chạy migrations ở chế độ 'online'.

    Trong trường hợp này, chúng tôi tạo Engine và liên kết nó với context.
    """
    # Lấy cấu hình SQLAlchemy từ tệp ini
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    # Tạo connectable từ cấu hình
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Thực hiện migrations
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # So sánh kiểu dữ liệu
            compare_server_default=True,  # So sánh server defaults
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
