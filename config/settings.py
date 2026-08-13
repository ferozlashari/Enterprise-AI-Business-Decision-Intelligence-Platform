"""
=========================================================

Enterprise AI Business Decision Intelligence Platform

Central Configuration Management

Author : Feroz Ali

=========================================================
"""


from functools import lru_cache

from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)



# =====================================================
# Project Root
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent





class Settings(BaseSettings):


    # =====================================================
    # Application
    # =====================================================

    APP_NAME: str = (
        "Enterprise AI Business Decision Intelligence Platform"
    )


    ENVIRONMENT: str = "development"


    DEBUG: bool = True


    HOST: str = "127.0.0.1"


    PORT: int = 8000





    # =====================================================
    # Security
    # =====================================================

    SECRET_KEY: str = (
        "enterprise-ai-secret-key"
    )


    ALGORITHM: str = "HS256"


    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7





    # =====================================================
    # PostgreSQL Database
    # =====================================================

    DB_HOST: str = "localhost"


    DB_PORT: int = 5432


    DB_NAME: str = "enterprise_ai"


    DB_USER: str = "postgres"


    DB_PASSWORD: str = "postgres"



    DATABASE_URL: str = (
        "postgresql://postgres:postgres@localhost:5432/enterprise_ai"
    )





    # =====================================================
    # Redis Cache
    # =====================================================

    REDIS_HOST: str = "localhost"


    REDIS_PORT: int = 6379


    REDIS_DB: int = 0


    REDIS_PASSWORD: str | None = None



    REDIS_URL: str = (
        "redis://localhost:6379/0"
    )





    # =====================================================
    # Celery
    # =====================================================

    CELERY_BROKER_URL: str = (
        "redis://localhost:6379/0"
    )


    CELERY_RESULT_BACKEND: str = (
        "redis://localhost:6379/0"
    )





    # =====================================================
    # AI / LLM Configuration
    # =====================================================

    GROQ_API_KEY: str = ""


    GROQ_MODEL: str = (
        "llama-3.1-70b-versatile"
    )


    HF_TOKEN: str | None = None


    OPENAI_API_KEY: str | None = None





    # =====================================================
    # LangChain / LangSmith
    # =====================================================

    LANGCHAIN_API_KEY: str | None = None


    LANGCHAIN_TRACING_V2: bool = False


    LANGCHAIN_PROJECT: str = (
        "Enterprise_AI"
    )





    # =====================================================
    # Vector Database
    # =====================================================

    CHROMA_DB_DIR: str = str(
        BASE_DIR / "knowledge_base" / "chroma_db"
    )





    # =====================================================
    # Storage Paths
    # =====================================================

    DATASET_DIR: str = str(
        BASE_DIR / "datasets"
    )


    UPLOAD_DIR: str = str(
        BASE_DIR / "uploads"
    )


    REPORT_DIR: str = str(
        BASE_DIR / "reports"
    )


    OUTPUT_DIR: str = str(
        BASE_DIR / "outputs"
    )


    MODEL_DIR: str = str(
        BASE_DIR / "saved_models"
    )


    FIGURE_DIR: str = str(
        BASE_DIR / "figures"
    )


    LOG_DIR: str = str(
        BASE_DIR / "logs"
    )





    # =====================================================
    # Logging
    # =====================================================

    LOG_LEVEL: str = "INFO"





    # =====================================================
    # Frontend
    # =====================================================

    FRONTEND_URL: str = (
        "http://localhost:5173"
    )





    # =====================================================
    # Email Configuration
    # =====================================================

    SMTP_SERVER: str | None = None


    SMTP_PORT: int | None = None


    SMTP_USERNAME: str | None = None


    SMTP_PASSWORD: str | None = None


    SMTP_FROM: str | None = None





    # =====================================================
    # Pydantic Settings
    # =====================================================

    model_config = SettingsConfigDict(

        env_file=str(
            BASE_DIR / ".env"
        ),

        case_sensitive=True,

        extra="ignore"

    )






# =====================================================
# Cached Settings Object
# =====================================================

@lru_cache()
def get_settings():

    return Settings()



settings = get_settings()





# =====================================================
# Machine Learning Configuration
# =====================================================

RANDOM_STATE = 42


TEST_SIZE = 0.20


N_CLUSTERS = 5


CV_FOLDS = 5


TARGET_COLUMN = "Sales"


MODEL_VERSION = "1.0.0"


AUTHOR = "Feroz Ali"


PROJECT = (
    "Enterprise AI Business Decision Intelligence"
)