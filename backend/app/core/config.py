"""
Application configuration using Pydantic Settings.
Loads environment variables for Azure services and database connections.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application settings
    APP_NAME: str = "Managed Container Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Frontend URL for CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Azure SQL Database settings
    AZURE_SQL_SERVER: str = ""
    AZURE_SQL_DATABASE: str = ""
    AZURE_SQL_USERNAME: str = ""
    AZURE_SQL_PASSWORD: str = ""
    AZURE_SQL_DRIVER: str = "ODBC Driver 18 for SQL Server"

    # Azure Monitor Application Insights
    APPLICATIONINSIGHTS_CONNECTION_STRING: str = ""

    # LLM API Configuration
    LLM_API_ENDPOINT: str = "https://api.openai.com/v1/chat/completions"
    LLM_API_KEY: str = ""
    LLM_MODEL_NAME: str = "gpt-3.5-turbo"
    LLM_MAX_TOKENS: int = 500
    LLM_TEMPERATURE: float = 0.7

    # Authentication
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    @property
    def DATABASE_URL(self) -> str:
        """Construct the database URL for Azure SQL."""
        if not all([self.AZURE_SQL_SERVER, self.AZURE_SQL_DATABASE]):
            return "sqlite+aiosqlite:///:memory:"
        return (
            f"mssql+pyodbc://{self.AZURE_SQL_USERNAME}:{self.AZURE_SQL_PASSWORD}"
            f"@{self.AZURE_SQL_SERVER}/{self.AZURE_SQL_DATABASE}"
            f"?driver={self.AZURE_SQL_DRIVER}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()