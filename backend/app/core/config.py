"""Core configuration for Gospel Keys API"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # ApplicationInfo
    app_name: str = "Piano Keys API"
    version: str = "2.0.0"
    description: str = "Multi-genre piano transcription and analysis API"
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    
    # CORS settings
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # File storage
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    OUTPUTS_DIR: Path = BASE_DIR / "outputs"
    
    # File limits
    max_upload_size_mb: int = 100
    supported_audio_formats: list[str] = [
        ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"
    ]
    supported_video_formats: list[str] = [
        ".mp4", ".mkv", ".avi", ".mov", ".webm"
    ]
    
    # Processing defaults
    default_sample_rate: int = 44100
    default_channels: int = 1  # mono
    
    # Job settings
    job_cleanup_age_hours: int = 24  # Clean up old jobs after 24 hours
    
    # AI Config
    google_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Celery & Redis Config
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    redis_url: str = "redis://localhost:6379/1"  # Separate DB for caching

    # Background job settings
    audio_generation_timeout: int = 300  # 5 minutes per exercise

    # Local LLM Config (MLX)
    local_llm_model: str = "mlx-community/Phi-3.5-mini-instruct-4bit"
    force_local_llm: bool = False  # Force local LLM for all compatible tasks

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Allow extra env variables
    )
    
    def ensure_directories(self) -> None:
        """Create upload and output directories if they don't exist"""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

# IMPORTANT: Set API keys in os.environ for libraries that check it directly
import os
if settings.google_api_key and 'GOOGLE_API_KEY' not in os.environ:
    os.environ['GOOGLE_API_KEY'] = settings.google_api_key
if settings.anthropic_api_key and 'ANTHROPIC_API_KEY' not in os.environ:
    os.environ['ANTHROPIC_API_KEY'] = settings.anthropic_api_key
