from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="KEYED_",
        extra="ignore",
        frozen=True,
    )

    database_url: str
    log_level: str = "INFO"
