"""Cấu hình ứng dụng (placeholder).

Đặt các pydantic Settings và đọc từ .env ở đây khi bắt đầu cấu hình.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Awesome API"
    admin_email: str
    items_per_user: int = 50

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings() -> Settings:
    return Settings()

