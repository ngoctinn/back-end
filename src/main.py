"""Điểm khởi tạo ứng dụng FastAPI.

Bao gồm cấu hình CORS cơ bản và gắn router của module auth.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.modules.auth.router import router as auth_router, admin_router
from src.modules.customers.router import router as customers_router
from src.modules.media.router import router as media_router
from src.modules.catalog.router import router as catalog_router


app = FastAPI(title="Spa Backend API")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def healthcheck():
    """Endpoint kiểm tra tình trạng ứng dụng."""

    return {"status": "ok"}


# Include routers
app.include_router(auth_router)
app.include_router(customers_router)
app.include_router(media_router)
app.include_router(catalog_router)
app.include_router(admin_router) # Thêm router cho admin
