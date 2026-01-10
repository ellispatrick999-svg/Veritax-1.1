"""
Centralized application configuration.

DO NOT hardcode secrets anywhere else in the codebase.
All services (auth, users, tax, AI) must import from here.
"""

from pydantic import BaseSettings, Field
from typing import List

# -----------------------------------
# Base Settings
# -----------------------------------

class Settings(BaseSettings):
    # -----------------------------------
    # Application
    # -----------------------------------
    APP_NAME: str = "AI Tax Platform"
    ENVIRONMENT: str = Field("development", regex="^(development|staging|production)$")
    DEBUG: bool = True

    # -----------------------------------
    # Security / Auth
    # -----------------------------------
    SECRET_KEY: str = Field(..., description="JWT signing key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    PASSWORD_HASH_SCHEME: str = "bcrypt"
    PASSWORD_MIN_LENGTH: int = 12

    # -----------------------------------
    # Database
    # -----------------------------------
    DATABASE_URL: str = Field(
        "postgresql+psycopg2://user:password@localhost:5432/taxdb"
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # -----------------------------------
    # AI / LLM Configuration
