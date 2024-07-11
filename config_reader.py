from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    weather_token: SecretStr

    model_config = SettingsConfigDict(env_file=None)


config: Settings = Settings()
