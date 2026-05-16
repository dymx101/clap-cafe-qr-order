# backend/app/config.py
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Clap Cafe Ordering"
    APP_ENV: str = "development"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/clapcafe"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PAYMENT_TIMEOUT_MINUTES: int = 15

    # CORS
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:4173,http://localhost:5174"
    )

    # API Key (KDS internal auth)
    KDS_API_KEY: str = "change-me-in-production"

    # Resend (email)
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "Clap Cafe <onboarding@resend.dev>"

    # Admin JWT
    ADMIN_JWT_SECRET: str = "change-me-in-production-jwt-secret"

    @property
    def cors_origins_list(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
