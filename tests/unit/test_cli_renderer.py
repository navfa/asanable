"""Tests for the CLI renderer — verifies rich output content."""

from datetime import date, datetime, timedelta

from rich.console import Console

from asanable.constants import DigestSectionType, ItemSource
from asanable.domain.digest import Digest, DigestItem, DigestSection, DigestSummary
from asanable.renderers.cli_renderer import (
    CliRenderer,
    _build_summary_group,
    _format_due_date,
    _format_item_row,
)


def _make_summary(
    *,
    total: int = 5,
    overdue: int = 1,
    today: int = 2,
) -> DigestSummary:
    return DigestSummary(
        total_items=total,
        overdue_count=overdue,
        today_count=today,
        generated_at=datetime(2025, 6, 15, 8, 30),
    )


def _make_item(
    *,
    title: str = "Fix login bug",
    due_on: date | None = None,
    project_name: str | None = "Backend",
    source: ItemSource = ItemSource.ASANA,
    is_overdue: bool = False,
) -> DigestItem:
    return DigestItem(
        title=title,
        source=source,
        permalink="https://app.asana.com/0/1/2",
        due_on=due_on,
        project_name=project_name,
        is_overdue=is_overdue,
    )


def _make_section(items: list[DigestItem]) -> DigestSection:
    return DigestSection(
        section_type=DigestSectionType.TODAY,
        items=tuple(items),
    )


def _capture_output(digest: Digest) -> str:
    console = Console(file=None, force_terminal=True, width=120)
    renderer = CliRenderer(console=console)
    with console.capture() as capture:
        renderer.render(digest)
    return capture.get()


class TestFormatDueDate:
    def test_formats_date(self) -> None:
        item = _make_item(due_on=date(2025, 6, 15))
        assert _format_due_date(item) == "Jun 15"

    def test_no_date_shows_dash(self) -> None:
        item = _make_item(due_on=None)
        assert _format_due_date(item) == "-"


class TestFormatItemRow:
    def test_row_contains_title_project_due_source(self) -> None:
        item = _make_item(
            title="Ship feature",
            project_name="Backend",
            due_on=date(2025, 6, 20),
        )
        row = _format_item_row(item, "yellow")
        assert row[0] == "Ship feature"
        assert row[1] == "Backend"
        assert row[2] == "Jun 20"
        assert row[3] == "Asana"

    def test_overdue_item_has_styled_title(self) -> None:
        item = _make_item(title="Late task", is_overdue=True)
        row = _format_item_row(item, "red")
        assert "[bold red]" in row[0]
        assert "Late task" in row[0]

    def test_missing_project_shows_dash(self) -> None:
        item = _make_item(project_name=None)
        row = _format_item_row(item, "blue")
        assert row[1] == "-"


class TestBuildSummaryLines:
    def test_contains_total_count(self) -> None:
        summary = _make_summary(total=10)
        text = _build_summary_group(summary)
        assert "10" in text.plain

    def test_contains_overdue_count(self) -> None:
        summary = _make_summary(overdue=3)
        text = _build_summary_group(summary)
        assert "Overdue: 3" in text.plain

    def test_contains_today_count(self) -> None:
        summary = _make_summary(today=4)
        text = _build_summary_group(summary)
        assert "Today: 4" in text.plain


class TestCliRendererIntegration:
    def test_render_outputs_section_titles(self) -> None:
        item = _make_item(title="Test task", due_on=date.today())
        section = DigestSection(
            section_type=DigestSectionType.TODAY,
            items=(item,),
        )
        digest = Digest(
            summary=_make_summary(),
            sections=(section,),
        )
        output = _capture_output(digest)
        assert "Today" in output
        assert "Test task" in output

    def test_render_summary_only_no_sections(self) -> None:
        digest = Digest(
            summary=_make_summary(),
            sections=(),
        )
        console = Console(file=None, force_terminal=True, width=120)
        renderer = CliRenderer(console=console)
        with console.capture() as capture:
            renderer.render_summary_only(digest)
        output = capture.get()
        assert "Daily Digest" in output

    def test_empty_digest_renders_without_error(self) -> None:
        digest = Digest(
            summary=DigestSummary(
                total_items=0,
                overdue_count=0,
                today_count=0,
                generated_at=datetime(2025, 6, 15, 8, 0),
            ),
            sections=(),
        )
        output = _capture_output(digest)
        assert "Total: 0" in output

    def test_multiple_sections_all_rendered(self) -> None:
        overdue_item = _make_item(
            title="Overdue task",
            is_overdue=True,
            due_on=date.today() - timedelta(days=1),
        )
        today_item = _make_item(title="Today task", due_on=date.today())
        digest = Digest(
            summary=_make_summary(),
            sections=(
                DigestSection(
                    section_type=DigestSectionType.OVERDUE,
                    items=(overdue_item,),
                ),
                DigestSection(
                    section_type=DigestSectionType.TODAY,
                    items=(today_item,),
                ),
            ),
        )
        output = _capture_output(digest)
        assert "Overdue" in output
        assert "Today" in output
