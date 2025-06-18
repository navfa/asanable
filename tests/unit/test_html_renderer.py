"""Tests for the HTML renderer."""

from datetime import date, datetime

from asanable.constants import DigestSectionType, ItemSource
from asanable.domain.digest import Digest, DigestItem, DigestSection, DigestSummary
from asanable.renderers.html_renderer import render_html


def _make_digest(*, sections: tuple = (), total: int = 2, overdue: int = 1) -> Digest:
    return Digest(
        summary=DigestSummary(
            total_items=total,
            overdue_count=overdue,
            today_count=0,
            generated_at=datetime(2025, 6, 15, 8, 30),
        ),
        sections=sections,
    )


def _make_item(**overrides) -> DigestItem:
    defaults = {
        "title": "Fix bug",
        "source": ItemSource.ASANA,
        "permalink": "https://app.asana.com/0/1/2",
        "due_on": date(2025, 6, 20),
        "project_name": "Backend",
        "is_overdue": False,
    }
    defaults.update(overrides)
    return DigestItem(**defaults)


class TestRenderHtml:
    def test_contains_doctype(self) -> None:
        html = render_html(_make_digest())
        assert "<!DOCTYPE html>" in html

    def test_summary_shows_total(self) -> None:
        html = render_html(_make_digest(total=7))
        assert "Total: 7" in html

    def test_summary_shows_date(self) -> None:
        html = render_html(_make_digest())
        assert "2025-06-15" in html

    def test_section_title_rendered(self) -> None:
        section = DigestSection(
            section_type=DigestSectionType.TODAY,
            items=(_make_item(),),
        )
        html = render_html(_make_digest(sections=(section,)))
        assert "Today" in html

    def test_item_title_in_output(self) -> None:
        section = DigestSection(
            section_type=DigestSectionType.TODAY,
            items=(_make_item(title="Deploy v2"),),
        )
        html = render_html(_make_digest(sections=(section,)))
        assert "Deploy v2" in html

    def test_overdue_item_has_overdue_class(self) -> None:
        section = DigestSection(
            section_type=DigestSectionType.OVERDUE,
            items=(_make_item(title="Late", is_overdue=True),),
        )
        html = render_html(_make_digest(sections=(section,)))
        assert 'class="overdue"' in html

    def test_item_with_permalink_has_link(self) -> None:
        section = DigestSection(
            section_type=DigestSectionType.TODAY,
            items=(_make_item(permalink="https://example.com"),),
        )
        html = render_html(_make_digest(sections=(section,)))
        assert 'href="https://example.com"' in html

    def test_empty_digest_renders(self) -> None:
        html = render_html(_make_digest(total=0, overdue=0))
        assert "Total: 0" in html
