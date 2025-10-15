from pydantic_settings import BaseSettings, SettingsConfigDict


class UvicornSettings(BaseSettings):
    app: str = "app.main:app"
    host: str = "0.0.0.0"  # nosec  # noqa: S104
    port: int = 8200
    log_level: str = "info"
    reload: bool = True
    limit_max_requests: int | None = None

    model_config = SettingsConfigDict(
        env_prefix="uvicorn_",
        extra="ignore",
    )
