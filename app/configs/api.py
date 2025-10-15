from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    public_prefix: str = "/api/g42"
    internal_prefix: str = "/api/internal"
    docs_enabled: bool = True
    docs_version: str = Field("unknown", validation_alias="VERSION")

    model_config = SettingsConfigDict(env_prefix="API__", extra="ignore")
