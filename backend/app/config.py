from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./kishan_bari.db"
    jwt_secret: str = "development-only-change-me"
    access_token_minutes: int = 1440
    frontend_origins: str = "http://localhost:8000,http://127.0.0.1:5500"
    admin_email: str = "admin@example.com"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [item.strip() for item in self.frontend_origins.split(",") if item.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
