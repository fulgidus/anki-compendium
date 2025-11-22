"""
Application configuration using Pydantic Settings.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    # Environment
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Anki Compendium"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://ankiuser:changeme@localhost:5432/anki_compendium_dev"
    )

    # CORS
    CORS_ORIGINS: list[str] | str = Field(
        default="http://localhost:3000,http://localhost:5173"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Security (future)
    SECRET_KEY: str = Field(default="change-this-in-production")

    # Gemini AI (future)
    GEMINI_API_KEY: str = Field(default="")

    # MinIO (future)
    MINIO_ENDPOINT: str = Field(default="localhost:9000")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="changeme")
    MINIO_USE_SSL: bool = Field(default=False)

    # RabbitMQ (future)
    RABBITMQ_URL: str = Field(
        default="amqp://admin:changeme@localhost:5672/"
    )

    # Keycloak (future)
    KEYCLOAK_URL: str = Field(default="http://localhost:8080")
    KEYCLOAK_REALM: str = Field(default="anki-compendium")
    KEYCLOAK_CLIENT_ID: str = Field(default="anki-api")
    KEYCLOAK_CLIENT_SECRET: str = Field(default="change-me")


settings = Settings()
