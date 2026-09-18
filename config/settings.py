from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Re:World"
    debug: bool = True

    database_url: str = "sqlite:///./reworld.db"

    llm_api_key: str = ""
    llm_model: str = "gpt-5.6"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()