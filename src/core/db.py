"""Cấu hình database (placeholder).

File này chỉ tạo engine, session factory và xuất `metadata` để
Alembic có thể import và autogenerate migrations.
Không chứa logic nghiệp vụ.
"""

import os
from sqlmodel import SQLModel, create_engine
from sqlmodel import SQLModel, create_engine, Session
from src.core.config import settings

# Đọc DATABASE_URL từ biến môi trường. Nếu không có, dùng SQLite file dev.
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL, echo=False, future=True)


# Metadata dùng bởi Alembic autogenerate
metadata = SQLModel.metadata


def get_session():
    """Cung cấp một SQLModel session cho dependency injection.

    Sử dụng context manager của SQLModel để đảm bảo session được đóng đúng cách.
    """
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()
