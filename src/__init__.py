# src/__init__.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.database import create_db_and_tables
from src.books.routes import book_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Hàm được gọi khi ứng dụng khởi động và tắt.
    Tạo các bảng database khi ứng dụng khởi động.
    """
    print("Creating tables..")
    create_db_and_tables()
    yield

app = FastAPI(
    title='Bookly',
    description='A RESTful API for a book review web service',
    version='v1',
    lifespan=lifespan
)

app.include_router(book_router, prefix="/api/v1/books", tags=['books'])