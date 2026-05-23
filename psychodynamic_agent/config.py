from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model_main: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL_MAIN")
    openai_model_internal: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL_INTERNAL")
    ultimate_need_seed: str = Field(default="SEALED_ULTIMATE_NEED", alias="ULTIMATE_NEED_SEED")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def get_settings() -> Settings:
    return Settings()
