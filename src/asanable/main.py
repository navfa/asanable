"""CLI entry point for asanable."""

import argparse
import sys

from asanable.errors import AsanableError


def main() -> None:
    """Run the asanable daily digest."""
    _configure_logging()
    args = _parse_args()
    try:
        if args.init:
            _run_init()
        elif args.done:
            _mark_done(args.done)
        elif args.open:
            _open_task(args.open)
        elif args.schedule:
            _run_scheduler()
        else:
            _run_digest(args)
    except AsanableError as error:
        _handle_error(error)


def _run_digest(args: argparse.Namespace) -> None:
    """Fetch data, build digest, and render output."""
    from asanable.config import Settings
    from asanable.services.digest_service import build_digest

    settings = Settings()
    tasks = _resolve_tasks(settings, args)
    if args.project:
        tasks = _filter_by_project(tasks, args.project)
    digest = build_digest(tasks)
    if args.overdue or args.today:
        digest = _filter_sections(digest, args)
    _render_digest(digest, args)


def _resolve_tasks(settings, args: argparse.Namespace) -> list:
    """Fetch tasks from API or cache depending on flags."""
    from asanable.infrastructure.cache import load_tasks, save_tasks

    if args.cache:
        cached = load_tasks()
        if cached is not None:
            return cached
        _print_warning("No cache available. Run without --cache first.")
        raise SystemExit(1)

    if not args.refresh:
        cached = load_tasks()
        if cached is not None:
            return cached

    tasks = _fetch_tasks_from_api(settings)
    save_tasks(tasks)
    return tasks


def _fetch_tasks_from_api(settings) -> list:
    """Fetch tasks from Asana API."""
    from asanable.clients.asana_client import AsanaClient

    return AsanaClient(settings).fetch_my_tasks()


def _print_warning(message: str) -> None:
    """Print a warning to stderr."""
    from rich.console import Console

    Console(stderr=True).print(f"[yellow]{message}[/]")


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
        "--overdue",
        action="store_true",
        help="show only overdue tasks",
    )
    parser.add_argument(
        "--today",
        action="store_true",
        help="show only tasks due today",
    )
    parser.add_argument(
        "-c",
        "--cache",
        action="store_true",
        help="use cached data only (no API call)",
    )
    parser.add_argument(
        "-r",
        "--refresh",
        action="store_true",
        help="force API refresh (ignore cache)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        choices=["cli", "html"],
        default="cli",
        help="output format (default: cli)",
    )
    parser.add_argument(
        "-s",
        "--schedule",
        action="store_true",
        help="run as a daily scheduler",
    )
    parser.add_argument(
        "-d",
        "--done",
        type=str,
        metavar="GID",
        default=None,
        help="mark a task as completed by its Asana GID",
    )
    parser.add_argument(
        "--open",
        type=str,
        metavar="GID",
        default=None,
        help="open a task in the browser by its Asana GID",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="run interactive setup wizard",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {_get_version()}",
    )
    return parser.parse_args()


def _render_digest(digest, args: argparse.Namespace) -> None:
    """Route digest to the appropriate renderer."""
    if args.output == "html":
        from asanable.renderers.html_renderer import render_html

        print(render_html(digest))
        return

    from asanable.renderers.cli_renderer import CliRenderer

    renderer = CliRenderer()
    if args.quiet:
        renderer.render_summary_only(digest)
    else:
        renderer.render(digest)


def _get_version() -> str:
    """Read version from package metadata."""
    from asanable import __version__

    return __version__


def _filter_sections(digest, args: argparse.Namespace):
    """Keep only the requested sections."""
    from asanable.constants import DigestSectionType
    from asanable.domain.digest import Digest

    allowed = set()
    if args.overdue:
        allowed.add(DigestSectionType.OVERDUE)
    if args.today:
        allowed.add(DigestSectionType.TODAY)

    filtered = tuple(s for s in digest.sections if s.section_type in allowed)
    return Digest(summary=digest.summary, sections=filtered)


def _filter_by_project(tasks: list, project_filter: str) -> list:
    """Keep only tasks whose project name matches the filter (case-insensitive)."""
    needle = project_filter.lower()
    return [t for t in tasks if t.project_name and needle in t.project_name.lower()]


def _mark_done(task_gid: str) -> None:
    """Mark a task as completed in Asana."""
    from rich.console import Console

    from asanable.clients.asana_client import AsanaClient
    from asanable.config import Settings

    client = AsanaClient(Settings())
    client.complete_task(task_gid)
    Console().print(f"[green]Task {task_gid} marked as done.[/]")


def _open_task(task_gid: str) -> None:
    """Open a task's permalink in the default browser."""
    import webbrowser

    url = f"https://app.asana.com/0/0/{task_gid}/f"
    webbrowser.open(url)


def _configure_logging() -> None:
    """Set up structlog for CLI output."""
    import logging

    import structlog

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.WARNING),
        processors=[
            structlog.processors.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
    )


def _run_init() -> None:
    """Launch the interactive setup wizard."""
    from asanable.commands.init_command import run_init

    run_init()


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
