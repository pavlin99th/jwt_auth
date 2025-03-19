from dotenv import find_dotenv
from pydantic.types import PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load and validate env settings."""

    model_config = SettingsConfigDict(env_file=find_dotenv())

    redis_host: str = "127.0.0.1"
    redis_port: PositiveInt = 6379

    authjwt_secret_key: str
    authjwt_access_token_expires: PositiveInt = 600
    authjwt_refresh_token_expires: PositiveInt = 10 * 24 * 3600
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set[str] = {"access", "refresh"}


settings = Settings()
