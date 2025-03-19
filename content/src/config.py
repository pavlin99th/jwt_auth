from dotenv import find_dotenv
from pydantic.networks import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load and validate env settings."""

    model_config = SettingsConfigDict(env_file=find_dotenv())

    authjwt_secret_key: str = "secret"
    authjwt_validator: HttpUrl = HttpUrl("http://localhost:8000/api/v1/auth/validate")


settings = Settings()
