# config.py - variáveis de ambiente e configurações do projeto

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    gemini_api_key: str
    gemini_model: str = "gemini-3.1-flash-lite"
    triage_analysis_llm_provider: str = "gemini"
    triage_analysis_llm_model: str | None = None
    triage_review_llm_provider: str = "gemini"
    triage_review_llm_model: str | None = None
    support_classification_llm_provider: str = "gemini"
    support_classification_llm_model: str | None = None
    support_knowledge_base_llm_provider: str = "gemini"
    support_knowledge_base_llm_model: str | None = None
    telegram_bot_token: str
    webhook_url: str
    telegram_webhook_secret: str
    # support_api_url: str
    # support_api_token: str
    # environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env")

    def model_post_init(self, __context: object) -> None:
        for field_name in (
            "triage_analysis_llm_model",
            "triage_review_llm_model",
            "support_classification_llm_model",
            "support_knowledge_base_llm_model",
        ):
            if getattr(self, field_name) is None:
                setattr(self, field_name, self.gemini_model)


settings = Settings()
