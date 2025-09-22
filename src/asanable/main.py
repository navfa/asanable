"""CLI entry point for asanable."""

import argparse
import sys

from asanable.errors import AsanableError


def main() -> None:
    """Run the asanable daily digest."""
    _configure_logging()
    args = _parse_args()
    if args.completions:
        _print_completions(args.completions)
        return

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
    if args.tag:
        tasks = _filter_by_tag(tasks, args.tag)
    digest = build_digest(tasks)
    if args.overdue or args.today or args.this_week:
        digest = _filter_sections(digest, args)
    _render_digest(digest, args)


def _resolve_tasks(settings, args: argparse.Namespace) -> list:
    """Fetch tasks from API or cache depending on flags."""
    from asanable.infrastructure.cache import load_tasks, save_tasks

    ttl = settings.cache_ttl_hours

    if args.cache:
        cached = load_tasks(ttl_hours=ttl)
        if cached is not None:
            return cached
        _print_warning("No cache available. Run without --cache first.")
        raise SystemExit(1)

    if not args.refresh:
        cached = load_tasks(ttl_hours=ttl)
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
    _add_arguments(parser)
    return parser.parse_args()


def _add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add all CLI arguments to a parser."""
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
        "-t",
        "--tag",
        type=str,
        default=None,
        help="filter tasks by tag name (case-insensitive substring match)",
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
        "--this-week",
        action="store_true",
        dest="this_week",
        help="show only tasks due this week",
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
        choices=["cli", "html", "json", "slack", "telegram"],
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
        nargs="?",
        const="__interactive__",
        default=None,
        metavar="GID",
        help="mark a task as done (interactive if no GID provided)",
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
    parser.add_argument(
        "--completions",
        choices=["bash", "zsh"],
        default=None,
        help="generate shell completions",
    )


def _render_digest(digest, args: argparse.Namespace) -> None:
    """Route digest to the appropriate renderer."""
    if args.output == "html":
        from asanable.renderers.html_renderer import render_html

        print(render_html(digest))
        return

    if args.output == "json":
        from asanable.renderers.json_renderer import render_json

        print(render_json(digest))
        return

    if args.output == "slack":
        from asanable.config import Settings
        from asanable.renderers.slack_renderer import send_slack_digest

        settings = Settings()
        if not settings.slack_webhook_url:
            _print_warning("SLACK_WEBHOOK_URL not set in .env")
            raise SystemExit(1)
        send_slack_digest(digest, settings.slack_webhook_url)
        return

    if args.output == "telegram":
        from asanable.config import Settings
        from asanable.renderers.telegram_renderer import send_telegram_digest

        settings = Settings()
        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            _print_warning("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env")
            raise SystemExit(1)
        send_telegram_digest(digest, settings.telegram_bot_token, settings.telegram_chat_id)
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
    if args.this_week:
        allowed.add(DigestSectionType.THIS_WEEK)

    filtered = tuple(s for s in digest.sections if s.section_type in allowed)
    return Digest(summary=digest.summary, sections=filtered)


def _filter_by_project(tasks: list, project_filter: str) -> list:
    """Keep only tasks whose project name matches the filter (case-insensitive)."""
    needle = project_filter.lower()
    return [t for t in tasks if t.project_name and needle in t.project_name.lower()]


def _print_completions(shell: str) -> None:
    """Generate and print shell completions."""
    import shtab

    parser = argparse.ArgumentParser(prog="asanable")
    _add_arguments(parser)
    print(shtab.complete(parser, shell))


def _filter_by_tag(tasks: list, tag_filter: str) -> list:
    """Keep only tasks that have a matching tag (case-insensitive)."""
    needle = tag_filter.lower()
    return [t for t in tasks if any(needle in tag.lower() for tag in t.tags)]


INTERACTIVE_DONE = "__interactive__"


def _mark_done(task_gid: str) -> None:
    """Mark a task as done — interactive picker if no GID provided."""
    if task_gid == INTERACTIVE_DONE:
        _interactive_done()
        return

    from rich.console import Console

    from asanable.clients.asana_client import AsanaClient
    from asanable.config import Settings

    client = AsanaClient(Settings())
    client.complete_task(task_gid)
    Console().print(f"[green]Task {task_gid} marked as done.[/]")


def _interactive_done() -> None:
    """Show numbered task list and let user pick tasks to complete."""
    from rich.console import Console

    from asanable.clients.asana_client import AsanaClient
    from asanable.config import Settings
    from asanable.infrastructure.cache import load_tasks, save_tasks

    settings = Settings()
    tasks = load_tasks(ttl_hours=settings.cache_ttl_hours)
    if tasks is None:
        tasks = AsanaClient(settings).fetch_my_tasks()
        save_tasks(tasks)

    console = Console()
    console.print("\n[bold]Tasks:[/]\n")
    for i, task in enumerate(tasks, start=1):
        due = task.due_on.strftime("%b %d") if task.due_on else ""
        style = "bold red" if task.is_overdue else ""
        console.print(f"  [{style}]{i:3}[/]  {task.name}  [dim]{due}[/]")

    console.print()
    choice = console.input("[bold]Mark as done (e.g. 1,3,5): [/]").strip()
    if not choice:
        return

    indices = _parse_indices(choice, len(tasks))
    client = AsanaClient(settings)
    for idx in indices:
        task = tasks[idx]
        client.complete_task(task.gid)
        console.print(f"  [green]Done:[/] {task.name}")


def _parse_indices(choice: str, max_count: int) -> list[int]:
    """Parse comma-separated numbers into zero-based indices."""
    indices = []
    for part in choice.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < max_count:
                indices.append(idx)
    return indices


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
