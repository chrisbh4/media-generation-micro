from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Literal
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = "postgres://postgres:password@localhost:5432/media_generation"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Replicate API Configuration
    replicate_api_token: str = Field(default="", env="REPLICATE_API_TOKEN")
    
    # Storage Configuration
    storage_type: Literal["local", "s3"] = "local"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "media-generation-bucket"
    local_storage_path: str = "./storage/media"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # Job Configuration
    max_retries: int = 3
    retry_delay: int = 60
    exponential_backoff_base: int = 2
    
    @validator('replicate_api_token')
    def validate_replicate_token(cls, v):
        """Validate and provide helpful error messages for Replicate API token."""
        if not v or v in ["", "your_replicate_api_token_here", "your_actual_replicate_api_token_here"]:
            print("\n" + "="*80)
            print("⚠️  REPLICATE API TOKEN NOT CONFIGURED")
            print("="*80)
            print("Media generation will use MOCK implementation.")
            print("To use actual Replicate API:")
            print("1. Create a .env file: cp .env-example .env")
            print("2. Get your token at: https://replicate.com/account/api-tokens")
            print("3. Set REPLICATE_API_TOKEN=your_actual_token_here in .env")
            print("4. Restart the application")
            print("="*80 + "\n")
            return ""
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_prefix = ""
    
    def model_post_init(self, __context) -> None:
        """Post initialization validation and logging."""
        if self.replicate_api_token and self.replicate_api_token not in ["", "your_replicate_api_token_here", "your_actual_replicate_api_token_here"]:
            print(f"✅ Replicate API token loaded: {self.replicate_api_token[:8]}...")
        
        # Check if .env file exists
        if not os.path.exists(".env"):
            print("\n📝 Note: No .env file found. Create one with: cp .env-example .env")


# Global settings instance
settings = Settings() 