"""
Application configuration using Pydantic Settings
"""
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "EduAssess API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Database — fresh SQLite file (see backend/data/ and scripts/init_database.py)
    DATABASE_URL: str = "sqlite:///./data/diagnostic_platform.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-characters-long-eduassess-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Evaluation — local AI primary (Ollama on GPU); cloud optional
    EVALUATION_PROVIDER: str = "ollama"  # ollama | mistral | rule
    USE_OLLAMA_EVALUATION: bool = True
    USE_MISTRAL_EVALUATION: bool = False
    MISTRAL_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b-instruct-q4_K_M"
    OLLAMA_EVAL_TEMPERATURE: float = 0.2
    OLLAMA_EVAL_TIMEOUT: int = 600
    DEFAULT_STUDENT_GRADE: int = 10
    EVALUATION_ALLOW_RULE_FALLBACK: bool = True

    # Dynamic question generation from templates (English grammar + Math)
    DYNAMIC_QUESTIONS_ENABLED: bool = True
    DYNAMIC_VARIANTS_PER_TEMPLATE: int = 6

    # Validate curated resource URLs before showing students (YouTube oEmbed / Khan HEAD)
    RESOURCE_URL_VALIDATION: bool = True
    
    # Email (optional)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
