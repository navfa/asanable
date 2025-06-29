"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Validated application settings loaded from environment."""

    # Asana
    asana_access_token: str
    asana_workspace_gid: str

    # Digest
    digest_schedule_time: str = "08:00"

    slack_webhook_url: str | None = None

    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}
