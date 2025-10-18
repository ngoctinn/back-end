"""Test cases cho module quản lý ảnh."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from src.main import app
from src.core.db import get_session
from src.modules.media.models import MediaFile


# Tạo in-memory database cho testing
@pytest.fixture(name="session")
def session_fixture():
    """Tạo database session cho test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Tạo bảng
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Tạo test client với session."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_media_models_created(session: Session):
    """Kiểm tra model MediaFile có thể tạo được."""
    media = MediaFile(
        file_path="test/image.jpg",
        public_url="https://example.com/test/image.jpg",
        file_type="image/jpeg",
        file_size=1024,
        related_entity_type="customer",
        related_entity_id=1,
    )
    session.add(media)
    session.commit()
    session.refresh(media)

    assert media.id is not None
    assert media.file_path == "test/image.jpg"
    assert media.public_url == "https://example.com/test/image.jpg"


def test_media_file_path_unique(session: Session):
    """Kiểm tra file_path là unique."""
    media1 = MediaFile(
        file_path="test/duplicate.jpg",
        public_url="https://example.com/test/duplicate1.jpg",
        file_type="image/jpeg",
        file_size=1024,
        related_entity_type="customer",
        related_entity_id=1,
    )
    session.add(media1)
    session.commit()

    # Cố gắng tạo với cùng file_path
    media2 = MediaFile(
        file_path="test/duplicate.jpg",
        public_url="https://example.com/test/duplicate2.jpg",
        file_type="image/jpeg",
        file_size=1024,
        related_entity_type="customer",
        related_entity_id=2,
    )
    session.add(media2)

    with pytest.raises(Exception):  # Should raise IntegrityError
        session.commit()


def test_health_check(client: TestClient):
    """Kiểm tra endpoint /health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
