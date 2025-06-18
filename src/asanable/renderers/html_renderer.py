"""HTML renderer — produces an HTML string from a Digest."""

from asanable.constants import NO_DATE_LABEL, NO_PROJECT_LABEL, SECTION_STYLES
from asanable.domain.digest import Digest, DigestItem, DigestSection

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>
body {{ font-family: -apple-system, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px; }}
.summary {{ background: #f0f4f8; border-radius: 8px; padding: 16px; margin-bottom: 24px; }}
.summary h2 {{ margin: 0 0 8px; }}
.counter {{ display: inline-block; margin-right: 16px; font-weight: 600; }}
.counter.zero {{ color: #999; }}
.section {{ margin-bottom: 24px; }}
.section h3 {{ border-left: 4px solid; padding-left: 12px; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ text-align: left; padding: 6px 12px; border-bottom: 1px solid #eee; }}
th {{ font-size: 0.85em; text-transform: uppercase; color: #666; }}
.overdue {{ color: #e53e3e; font-weight: 600; }}
</style></head>
<body>
{summary}
{sections}
</body>
</html>"""


def render_html(digest: Digest) -> str:
    """Render a complete Digest to an HTML string."""
    summary_html = _render_summary(digest.summary)
    sections_html = "\n".join(_render_section(s) for s in digest.sections)
    return HTML_TEMPLATE.format(summary=summary_html, sections=sections_html)


def _render_summary(summary) -> str:
    """Render the summary header block."""
    overdue_cls = "" if summary.overdue_count > 0 else " zero"
    today_cls = "" if summary.today_count > 0 else " zero"
    return (
        '<div class="summary">'
        f"<h2>Daily Digest &mdash; {summary.generated_at:%Y-%m-%d}</h2>"
        f'<span class="counter">Total: {summary.total_items}</span>'
        f'<span class="counter{overdue_cls}">Overdue: {summary.overdue_count}</span>'
        f'<span class="counter{today_cls}">Today: {summary.today_count}</span>'
        "</div>"
    )


def _render_section(section: DigestSection) -> str:
    """Render a single section with its items table."""
    style = SECTION_STYLES.get(section.section_type, SECTION_STYLES["later"])
    color = _css_color(style["color"])
    rows = "\n".join(_render_row(item) for item in section.items)
    return (
        f'<div class="section">'
        f'<h3 style="border-color: {color};">{style["icon"]} {style["title"]}</h3>'
        f"<table><thead><tr>"
        f"<th>Title</th><th>Project</th><th>Due</th><th>Source</th>"
        f"</tr></thead><tbody>\n{rows}\n</tbody></table></div>"
    )


def _render_row(item: DigestItem) -> str:
    """Render a single item as a table row."""
    title = _format_title(item)
    project = item.project_name or NO_PROJECT_LABEL
    due = item.due_on.strftime("%b %d") if item.due_on else NO_DATE_LABEL
    source = item.source.value.capitalize()
    return f"<tr><td>{title}</td><td>{project}</td><td>{due}</td><td>{source}</td></tr>"


def _format_title(item: DigestItem) -> str:
    """Format title with overdue styling if needed."""
    if item.is_overdue:
        return f'<span class="overdue">{item.title}</span>'
    if item.permalink:
        return f'<a href="{item.permalink}">{item.title}</a>'
    return item.title


CSS_COLOR_MAP = {
    "red": "#e53e3e",
    "yellow": "#d69e2e",
    "blue": "#3182ce",
    "dim": "#a0aec0",
    "green": "#38a169",
}


def _css_color(rich_color: str) -> str:
    """Convert a rich color name to a CSS hex color."""
    return CSS_COLOR_MAP.get(rich_color, "#a0aec0")
