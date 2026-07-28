from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    development: bool
    
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    
    redis_host: str
    redis_port: str
    redis_password: str
    redis_db: int

    init_admin_username: str
    init_admin_password: str

    access_token_expire_minutes: int
    refresh_token_expire_days: int
    secret_key: str
    algorithm: str
    cookie_secure: bool
    cookie_samesite: str

    model_config = SettingsConfigDict(env_file=BASE_DIR / "infra" / ".prod.env", env_file_encoding="utf-8", extra="ignore")

    @property
    def migration_url(self) -> str:
        return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    

@lru_cache
def get_settings():
    return Settings()