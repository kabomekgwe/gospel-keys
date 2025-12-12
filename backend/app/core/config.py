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
    base_dir: Path = Path(__file__).parent.parent.parent
    upload_dir: Path = base_dir / "uploads"
    output_dir: Path = base_dir / "outputs"
    
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
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    def ensure_directories(self) -> None:
        """Create upload and output directories if they don't exist"""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
