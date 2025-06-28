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
    tasks = _fetch_tasks(settings)
    if args.project:
        tasks = _filter_by_project(tasks, args.project)
    digest = build_digest(tasks)
    renderer = CliRenderer()

    if args.quiet:
        renderer.render_summary_only(digest)
    else:
        renderer.render(digest)


def _fetch_tasks(settings) -> list:
    """Fetch tasks from Asana."""
    from asanable.clients.asana_client import AsanaClient

    asana_client = AsanaClient(settings)
    return asana_client.fetch_my_tasks()


def _parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="asanable",
        description="Asana daily digest aggregator",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="show summary only",
    )
    parser.add_argument(
        "-p",
        "--project",
        type=str,
        default=None,
        help="filter tasks by project name (case-insensitive substring match)",
    )
    parser.add_argument(
        "-s",
        "--schedule",
        action="store_true",
        help="run as a daily scheduler",
    )
    return parser.parse_args()


def _filter_by_project(tasks: list, project_filter: str) -> list:
    """Keep only tasks whose project name matches the filter (case-insensitive)."""
    needle = project_filter.lower()
    return [t for t in tasks if t.project_name and needle in t.project_name.lower()]


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
