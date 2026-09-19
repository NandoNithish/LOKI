from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Re:World"
    debug: bool = True

    database_url: str = "sqlite:///./reworld.db"

    openai_api_key: str = ""
    gemini_api_key: str = ""
    llm_model: str = "gemini-3.6-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()