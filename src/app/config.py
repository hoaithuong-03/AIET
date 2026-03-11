from typing import Literal
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
 
 
class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
 
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # ignore phan biet hoa thuong. ex: ABC = abc
        extra="ignore",  # ignote unknown environment variables
    )
 
    app_name: str = "Data Processing Service"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, description="Enable or disables debug mode")
    environment: Literal["development", "staging", "production"] = "development"
 
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
 
    # Logging
    log_level: Literal["debug", "info", "warning", "error", "critical"] = "info"
    log_format: Literal["console", "json"] = "console"
    
    #Base URL
    base_url: str = "https://truyenfull.vision/"
    
    # Cấu hình thời gian chờ cho crawling
    crawl_timeout_seconds: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Timeout for crawling operations in seconds",
    )
 
    @computed_field
    def is_development(self) -> bool:
        """Check if the application is running in development mode."""
        return self.environment == "development"
 
 
def get_settings() -> Settings:
    """Retrieve the application settings."""
    return Settings()
 
# Singleton instance of settings
settings = get_settings()