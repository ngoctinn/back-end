"""Cấu hình database (placeholder).

File này chỉ tạo engine, session factory và xuất `metadata` để
Alembic có thể import và autogenerate migrations.
Không chứa logic nghiệp vụ.
"""

import os
from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import sessionmaker

# Đọc DATABASE_URL từ biến môi trường. Nếu không có, dùng SQLite file dev.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./dev.db")

engine = create_engine(DATABASE_URL, echo=False, future=True)

# Session factory (sử dụng SQLAlchemy 2-style)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Metadata dùng bởi Alembic autogenerate
metadata = SQLModel.metadata


def get_session():
    """Yield một session DB. Dùng như dependency của FastAPI.

    Đây là helper nhỏ phục vụ khi bắt đầu cài đặt; không chứa logic nghiệp vụ.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
