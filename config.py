
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
from urllib.parse import quote_plus


class Settings(BaseSettings):
    app_name: str = "Inventory Management API"
    app_version: str = "1.0.0"
    debug: bool = False

    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: SecretStr = Field(default=SecretStr(""))
    db_name: str = "inventory_management"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def database_url(self) -> str:
        password = quote_plus(self.db_password.get_secret_value())
        username = quote_plus(self.db_user)
        return (
            f"mysql+pymysql://{username}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            "?charset=utf8mb4"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
