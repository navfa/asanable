"""CLI renderer — displays the digest in the terminal using rich."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from asanable.constants import (
    COLUMN_DUE,
    COLUMN_GID,
    COLUMN_PROJECT,
    COLUMN_TITLE,
    NO_DATE_LABEL,
    NO_PROJECT_LABEL,
    SECTION_STYLES,
)
from asanable.domain.digest import Digest, DigestItem, DigestSection, DigestSummary


class CliRenderer:
    """Renders a Digest to the terminal via rich."""

    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()

    def render(self, digest: Digest) -> None:
        """Render a full digest: summary header + all sections."""
        self._render_summary(digest.summary)
        for section in digest.sections:
            self._render_section(section)

    def render_summary_only(self, digest: Digest) -> None:
        """Render only the summary header (quiet mode)."""
        self._render_summary(digest.summary)

    def _render_summary(self, summary: DigestSummary) -> None:
        """Display the digest header with counters, projects, and sections."""
        group = _build_summary_group(summary)
        panel = Panel(
            group,
            title="Daily Digest",
            subtitle=summary.generated_at.strftime("%Y-%m-%d %H:%M"),
            border_style="bold cyan",
        )
        self._console.print(panel)

    def _render_section(self, section: DigestSection) -> None:
        """Display a single section as a styled table inside a panel."""
        style = SECTION_STYLES.get(section.section_type, SECTION_STYLES["later"])
        table = _build_section_table(section, style["color"])
        panel = Panel(
            table,
            title=f"{style['icon']} {style['title']}",
            border_style=style["color"],
        )
        self._console.print(panel)


def _build_summary_group(summary: DigestSummary) -> Text:
    """Compose the full summary block."""
    text = Text()

    text.append("Tasks  ", style="bold")
    _append_counter(text, "Total", summary.total_items, "bold")
    text.append("  ")
    _append_counter(text, "Overdue", summary.overdue_count, "bold red")
    text.append("  ")
    _append_counter(text, "Today", summary.today_count, "bold yellow")
    text.append("  ")
    _append_counter(text, "This week", summary.this_week_count, "bold blue")
    text.append("  ")
    _append_counter(text, "Later", summary.later_count, "dim")
    text.append("\n\n")

    if summary.project_counts:
        text.append("Projects\n", style="bold")
        for project, count in summary.project_counts.items():
            text.append(f"  {project}: ", style="cyan")
            text.append(f"{count}\n")
        text.append("\n")

    return text


def _append_counter(text: Text, label: str, count: int, active_style: str) -> None:
    """Append a counter to a Text, styled only when non-zero."""
    style = active_style if count > 0 else "dim"
    text.append(f"{label}: {count}", style=style)


def _build_section_table(section: DigestSection, color: str) -> Table:
    """Build a rich Table for a section's items."""
    table = Table(show_header=True, header_style=f"bold {color}", box=None, pad_edge=False)
    table.add_column(COLUMN_GID, style="dim", min_width=10)
    table.add_column(COLUMN_TITLE, style="bold", min_width=30)
    table.add_column(COLUMN_PROJECT, min_width=15)
    table.add_column(COLUMN_DUE, min_width=12)

    for item in section.items:
        table.add_row(*_format_item_row(item, color))
    return table


def _format_item_row(item: DigestItem, color: str) -> tuple[str, str, str, str]:
    """Format a single item as a table row."""
    gid = item.asana_task_gid or ""
    title = _format_title(item, color)
    project = item.project_name or NO_PROJECT_LABEL
    due = _format_due_date(item)
    return (gid, title, project, due)


def _format_title(item: DigestItem, color: str) -> str:
    """Format the title with overdue marker if needed."""
    if item.is_overdue:
        return f"[bold {color}]{item.title}[/]"
    return item.title


def _format_due_date(item: DigestItem) -> str:
    """Format the due date for display."""
    if item.due_on is None:
        return NO_DATE_LABEL
    return item.due_on.strftime("%b %d")
