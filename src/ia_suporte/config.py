from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str
    telegram_bot_token: str
    # support_api_url: str
    # support_api_token: str
    # environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
