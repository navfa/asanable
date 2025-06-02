"""Application configuration via environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Validated application settings loaded from environment."""

    # Asana
    asana_access_token: str
    asana_workspace_gid: str

    # Gmail OAuth2
    gmail_credentials_path: Path = Path("credentials.json")
    gmail_token_path: Path = Path("token.json")

    # Digest
    digest_schedule_time: str = "08:00"
    max_gmail_results: int = 20
    gmail_lookback_hours: int = 24

    slack_webhook_url: str | None = None
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
