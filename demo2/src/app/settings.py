from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str | None = None
    openai_model: str = "gpt-5.2"
    openai_structured_model: str = "gpt-4o-2024-08-06"

    request_timeout_s: float = 30.0
    max_tool_iters: int = 3

    files_dir: str = "./data"


settings = Settings()
