# src/books/routes.py
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from typing import List

from src.database import get_session
from src.books.schemas import Book, BookCreate, BookUpdate

book_router = APIRouter()

@book_router.get("/books", response_model=List[Book])
async def get_all_books(session: Session = Depends(get_session)):
    """Lấy tất cả sách từ database."""
    books = session.exec(select(Book)).all()
    return books

@book_router.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_a_book(book: BookCreate, session: Session = Depends(get_session)):
    """Thêm một sách mới vào database."""
    db_book = Book.model_validate(book)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book

@book_router.get("/book/{book_id}", response_model=Book)
async def get_book(book_id: int, session: Session = Depends(get_session)):
    """Tìm một sách theo ID."""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@book_router.patch("/book/{book_id}", response_model=Book)
async def update_book(book_id: int, book_update: BookUpdate, session: Session = Depends(get_session)):
    """Cập nhật thông tin sách theo ID."""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    
    update_data = book_update.model_dump(exclude_unset=True)
    book.sqlmodel_update(update_data)
    
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@book_router.delete("/book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, session: Session = Depends(get_session)):
    """Xóa một sách theo ID."""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    
    session.delete(book)
    session.commit()
    return {"message": "Book deleted successfully"}