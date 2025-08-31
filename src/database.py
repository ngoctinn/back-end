# src/database.py
from sqlmodel import create_engine, SQLModel, Session
from typing import Generator
import os
from dotenv import load_dotenv  # Thêm dòng này

# Tải các biến môi trường từ file .env
load_dotenv()

# Lấy đường dẫn database từ biến môi trường
DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL) # type: ignore

def create_db_and_tables():
    """Tạo các bảng trong cơ sở dữ liệu."""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator:
    """Tạo và đóng session database sau mỗi request."""
    with Session(engine) as session:
        yield session