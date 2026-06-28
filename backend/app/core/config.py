from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "MUST Health Tech (MHT)"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    SECRET_KEY: str = "change-this-in-production-malawi-health"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    DATABASE_URL: str = "sqlite+aiosqlite:///./ehealth_malawi.db"
    SYNC_DATABASE_URL: str = "sqlite:///./ehealth_malawi.db"

    POSTGRES_URL: Optional[str] = None

    REDIS_URL: Optional[str] = None

    # When OFFLINE_MODE=True, use SQLite.
    # When False and POSTGRES_URL is set, use PostgreSQL.
    OFFLINE_MODE: bool = True

    OPENAI_API_KEY: Optional[str] = None
    ENABLE_AI_FEATURES: bool = False

    CORS_ORIGINS: str = "*"

    # Central server for multi-site data sync (pull/push)
    SYNC_SERVER_URL: Optional[str] = None
    SYNC_SITE_ID: str = "default-site"
    SYNC_API_KEY: str = ""

    # Notification channels
    AT_API_KEY: str = ""
    AT_USERNAME: str = "sandbox"
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_ID: str = ""

    # Email backup (used by deploy.ps1)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
