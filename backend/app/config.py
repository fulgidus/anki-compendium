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

    # Security
    SECRET_KEY: str = Field(default="change-this-in-production-must-be-32-chars-minimum!")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Gemini AI Configuration
    GEMINI_API_KEY: str = Field(
        default="",
        description="Google Gemini API key for RAG pipeline. Get from https://makersuite.google.com/app/apikey"
    )
    GEMINI_MODEL_DEFAULT: str = Field(
        default="gemini-2.0-flash-exp",
        description="Default Gemini model for LLM operations"
    )
    
    def model_post_init(self, __context) -> None:
        """Post-initialization: Set GOOGLE_API_KEY environment variable for LangChain."""
        import os
        
        # LangChain's Google Generative AI uses GOOGLE_API_KEY by default
        # Set it from our GEMINI_API_KEY if not already set
        if self.GEMINI_API_KEY and not os.environ.get("GOOGLE_API_KEY"):
            os.environ["GOOGLE_API_KEY"] = self.GEMINI_API_KEY

    # MinIO (S3-compatible storage)
    MINIO_ENDPOINT: str = Field(default="localhost:9000")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="changeme123")
    MINIO_USE_SSL: bool = Field(default=False)
    MINIO_BUCKET_PDFS: str = Field(default="pdfs")
    MINIO_BUCKET_DECKS: str = Field(default="decks")

    # RabbitMQ
    RABBITMQ_URL: str = Field(
        default="amqp://admin:changeme@localhost:5672/"
    )
    RABBITMQ_QUEUE_PDF_PROCESSING: str = Field(default="pdf_processing")
    RABBITMQ_QUEUE_CARD_GENERATION: str = Field(default="card_generation")
    RABBITMQ_QUEUE_NOTIFICATIONS: str = Field(default="notifications")

    # Keycloak OAuth2/OIDC
    KEYCLOAK_URL: str = Field(default="http://localhost:8080")
    KEYCLOAK_REALM: str = Field(default="anki-compendium")
    KEYCLOAK_CLIENT_ID: str = Field(default="anki-api")
    KEYCLOAK_CLIENT_SECRET: str = Field(default="change-me")
    KEYCLOAK_ADMIN_USERNAME: str = Field(default="admin")
    KEYCLOAK_ADMIN_PASSWORD: str = Field(default="changeme")

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = Field(default=100)
    ALLOWED_FILE_EXTENSIONS: list[str] = Field(
        default=[".pdf"]
    )

    # Celery (Worker Configuration)
    CELERY_BROKER_URL: str = Field(
        default="amqp://admin:changeme@localhost:5672/"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/0"
    )

    # Subscription Tiers
    FREE_TIER_CARD_LIMIT: int = Field(default=30)
    PREMIUM_TIER_CARD_LIMIT: int = Field(default=1000)


settings = Settings()
