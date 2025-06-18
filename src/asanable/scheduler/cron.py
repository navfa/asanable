"""Scheduler — runs the digest on a configurable daily schedule."""

import time

import schedule
import structlog

from asanable.config import Settings

logger = structlog.get_logger()

POLL_INTERVAL_SECONDS = 30


def start_scheduler(settings: Settings) -> None:
    """Start the blocking scheduler loop."""
    schedule_time = settings.digest_schedule_time
    logger.info("scheduler_started", time=schedule_time)

    schedule.every().day.at(schedule_time).do(_run_scheduled_digest, settings)
    _run_loop()


def _run_scheduled_digest(settings: Settings) -> None:
    """Execute one digest cycle and dispatch to configured channels."""
    from asanable.services.digest_service import build_digest

    logger.info("digest_run_started")
    try:
        tasks, emails = _fetch_all_sources(settings)
        digest = build_digest(tasks, emails)
        _dispatch(digest, settings)
        logger.info("digest_run_completed", total_items=digest.summary.total_items)
    except Exception:
        logger.exception("digest_run_failed")


def _fetch_all_sources(settings: Settings):
    """Fetch tasks and emails from all configured sources."""
    from asanable.clients.asana_client import AsanaClient

    asana_client = AsanaClient(settings)
    tasks = asana_client.fetch_my_tasks()
    emails = _fetch_emails(settings)
    return tasks, emails


def _fetch_emails(settings: Settings) -> list:
    """Fetch Gmail emails if configured, return empty list otherwise."""
    if not settings.gmail_credentials_path.exists():
        return []
    try:
        from asanable.clients.gmail_client import GmailClient

        client = GmailClient(settings)
        return client.fetch_asana_notifications() + client.fetch_unread_emails()
    except Exception:
        logger.warning("gmail_fetch_failed")
        return []


def _dispatch(digest, settings: Settings) -> None:
    """Send digest to all configured output channels."""
    from asanable.renderers.cli_renderer import CliRenderer

    CliRenderer().render(digest)

    _dispatch_email(digest, settings)
    _dispatch_slack(digest, settings)
    _dispatch_telegram(digest, settings)


def _dispatch_email(digest, settings: Settings) -> None:
    """Send HTML email if configured."""
    if settings.digest_email_to is None:
        return
    try:
        from asanable.renderers.html_renderer import render_html

        html = render_html(digest)
        logger.info("html_email_rendered", to=settings.digest_email_to, length=len(html))
    except Exception:
        logger.warning("email_dispatch_failed")


def _dispatch_slack(digest, settings: Settings) -> None:
    """Send Slack notification if configured."""
    if settings.slack_webhook_url is None:
        return
    try:
        from asanable.renderers.slack_renderer import send_slack_digest

        send_slack_digest(digest, settings.slack_webhook_url)
        logger.info("slack_notification_sent")
    except Exception:
        logger.warning("slack_dispatch_failed")


def _dispatch_telegram(digest, settings: Settings) -> None:
    """Send Telegram notification if configured."""
    if settings.telegram_bot_token is None or settings.telegram_chat_id is None:
        return
    try:
        from asanable.renderers.telegram_renderer import send_telegram_digest

        send_telegram_digest(digest, settings.telegram_bot_token, settings.telegram_chat_id)
        logger.info("telegram_notification_sent")
    except Exception:
        logger.warning("telegram_dispatch_failed")


def _run_loop() -> None:
    """Blocking loop that checks for pending scheduled jobs."""
    while True:
        schedule.run_pending()
        time.sleep(POLL_INTERVAL_SECONDS)
