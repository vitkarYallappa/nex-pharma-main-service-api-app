"""
Application settings and configuration management.
Supports both local development and production environments.
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment-based configuration.
    Automatically detects credentials for EC2 production or uses env vars for local.
    """
    
    # Environment configuration
    env: str = Field(default="local", description="Environment: local or production")
    debug: bool = Field(default=True, description="Debug mode")
    
    # Database configuration
    db_host: str = Field(default="localhost", description="Database host")
    db_port: int = Field(default=5432, description="Database port")
    db_name: str = Field(default="nex_pharma", description="Database name")
    db_user: str = Field(default="postgres", description="Database user")
    db_password: str = Field(default="postgres", description="Database password")
    
    # AWS/Storage configuration
    aws_region: str = Field(default="us-east-1", description="AWS region")
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS access key (local only)")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS secret key (local only)")
    
    # MinIO configuration (local development)
    minio_endpoint: str = Field(default="localhost:9000", description="MinIO endpoint")
    minio_access_key: str = Field(default="minioadmin", description="MinIO access key")
    minio_secret_key: str = Field(default="minioadmin", description="MinIO secret key")
    minio_secure: bool = Field(default=False, description="Use HTTPS for MinIO")
    
    # Storage bucket
    storage_bucket: str = Field(default="nexpharma-storage", description="Storage bucket name")
    
    # Application configuration
    app_name: str = Field(default="NexPharma API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    
    @property
    def database_url(self) -> str:
        """
        Construct database URL from individual components.
        """
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def async_database_url(self) -> str:
        """
        Construct async database URL for SQLAlchemy async operations.
        """
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.env == "production"
    
    @property
    def is_local(self) -> bool:
        """Check if running in local development environment."""
        return self.env == "local"
    
    class Config:
        """Pydantic configuration."""
        env_file = None  # Will be set dynamically
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """
    Get application settings based on environment.
    Automatically loads the appropriate .env file.
    """
    env = os.getenv("ENV", "local")
    
    # Determine which env file to load
    if env == "production":
        env_file = "environments/.env.production"
    else:
        env_file = "environments/.env.local"
    
    # Check if env file exists
    if os.path.exists(env_file):
        return Settings(_env_file=env_file)
    else:
        # Fallback to environment variables only
        return Settings()


# Global settings instance
settings = get_settings() 