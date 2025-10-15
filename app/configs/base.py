import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.configs.api import APISettings
from app.configs.data_normalizer import DataNormalizerSettings
from app.configs.logging import configure_logging
from app.configs.uvicorn import UvicornSettings

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


class Settings(BaseSettings):
    api: APISettings = APISettings()
    uvicorn: UvicornSettings = UvicornSettings()
    normalizer: DataNormalizerSettings = DataNormalizerSettings()

    model_config = SettingsConfigDict(env_nested_delimiter="__", extra="ignore")

    @classmethod
    def load(cls, path: Path = CONFIG_PATH) -> "Settings":
        if not path.exists():
            return cls()

        try:
            raw = path.read_text(encoding="utf-8")
            payload = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON configuration at {path}") from exc

        if not payload:
            raise ValueError("config.json was not found.")

        return cls(**payload)


settings = Settings.load()
configure_logging()
