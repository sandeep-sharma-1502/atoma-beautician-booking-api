from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Atoma Beautician Booking API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # JWT Config
    SECRET_KEY: str = "change-this-to-a-long-random-secret-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database
    # Using Supabase PostgreSQL for both local and production
    DATABASE_URL: str = "postgresql://postgres.tjuejldgyatrnliyyjut:FmNsiXOWBC4Slq8Z@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

    REDIS_URL: str | None = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        """
        Ensures that any PostgreSQL URL (e.g. from Supabase/Neon) uses the asyncpg driver.
        """
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and "+asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

settings = Settings()
