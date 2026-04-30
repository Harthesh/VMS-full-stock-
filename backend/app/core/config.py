from __future__ import annotations

from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "Visitor Management System"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    secret_key: str
    access_token_expire_minutes: int = 480
    database_url: str
    redis_url: str
    backend_cors_origins: str = ""
    storage_root: str = "./uploads"
    default_from_email: str = "no-reply@example.com"
    default_admin_email: str = "admin@vms.example.com"
    default_admin_password: str = "Admin@123"
    visitor_approval_test_email: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    smtp_timeout_seconds: int = 15
    scheduler_enabled: bool = True
    scheduler_timezone: str = "Asia/Kolkata"
    daily_digest_hour: int = 7
    unchecked_out_hour: int = 20
    no_show_hour: int = 21
    public_app_url: str = "http://localhost:5173"

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
