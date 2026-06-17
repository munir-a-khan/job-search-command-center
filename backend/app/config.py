from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Look for .env in current dir first, then one level up (handles backend/ subdir runs)
    model_config = SettingsConfigDict(
        env_file=[".env", "../.env"],
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-6"
    database_url: str = "sqlite:////data/app.db"
    data_dir: str = "/data"
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost"
    api_key: str = ""  # if empty, auth is disabled


settings = Settings()
