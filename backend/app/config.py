from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-6"
    database_url: str = "sqlite:////data/app.db"
    data_dir: str = "/data"
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost"


settings = Settings()
