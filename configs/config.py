# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import Field
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.staticfiles import StaticFiles

class Settings(BaseSettings):
    db_url: str = Field(..., alias="DB_URL")
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
static_files = StaticFiles(directory=str(BASE_DIR / "static"))
