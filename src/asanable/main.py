"""CLI entry point for asanable."""

import argparse
import sys

from asanable.errors import AsanableError


def main() -> None:
    """Run the asanable daily digest."""
    args = _parse_args()
    try:
        if args.schedule:
            _run_scheduler()
        else:
            _run_digest(args)
    except AsanableError as error:
        _handle_error(error)


def _run_digest(args: argparse.Namespace) -> None:
    """Fetch data, build digest, and render output."""
    from asanable.config import Settings
    from asanable.renderers.cli_renderer import CliRenderer
    from asanable.services.digest_service import build_digest

    settings = Settings()
    tasks, emails = _fetch_sources(settings)
    digest = build_digest(tasks, emails)
    renderer = CliRenderer()

    if args.quiet:
        renderer.render_summary_only(digest)
    else:
        renderer.render(digest)


def _fetch_sources(settings):
    """Fetch tasks and emails from configured sources."""
    from asanable.clients.asana_client import AsanaClient

    asana_client = AsanaClient(settings)
    tasks = asana_client.fetch_my_tasks()

    emails = _fetch_emails_if_configured(settings)
    return tasks, emails


def _fetch_emails_if_configured(settings) -> list:
    """Fetch Gmail emails only if credentials are available."""
    if not settings.gmail_credentials_path.exists():
        return []
    try:
        from asanable.clients.gmail_client import GmailClient

        gmail_client = GmailClient(settings)
        notifications = gmail_client.fetch_asana_notifications()
        unread = gmail_client.fetch_unread_emails()
        return notifications + unread
    except Exception:
        return []


def _parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="asanable",
        description="Asana + Gmail daily digest aggregator",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="show summary only",
    )
    parser.add_argument(
        "-s",
        "--schedule",
        action="store_true",
        help="run as a daily scheduler",
    )
    return parser.parse_args()


def _run_scheduler() -> None:
    """Start the daily digest scheduler."""
    from asanable.config import Settings
    from asanable.scheduler.cron import start_scheduler

    settings = Settings()
    start_scheduler(settings)


def _handle_error(error: AsanableError) -> None:
    """Display a user-friendly error and exit."""
    from rich.console import Console

    console = Console(stderr=True)
    console.print(f"[bold red]Error:[/] {error}")
    sys.exit(1)


if __name__ == "__main__":
    main()
