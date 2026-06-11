from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str

    # YNAB
    ynab_api_key: str = ""
    ynab_budget_id: str = ""

    # Sync
    sync_interval_hours: int = 6
    ynab_lookback_days: int = 90

    # ML
    ml_min_training_samples: int = 5
    ml_low_confidence_threshold: float = 0.6

    # App
    app_env: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()