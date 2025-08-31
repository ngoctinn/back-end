# src/books/schemas.py
from sqlmodel import Field, SQLModel
from typing import Optional

class BookBase(SQLModel):
    title: str = Field(index=True)
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str

class Book(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class BookCreate(BookBase):
    pass

class BookUpdate(SQLModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None