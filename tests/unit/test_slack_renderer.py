"""Tests for the Slack renderer."""

from datetime import date, datetime

from asanable.constants import DigestSectionType, ItemSource
from asanable.domain.digest import Digest, DigestItem, DigestSection, DigestSummary
from asanable.renderers.slack_renderer import _build_payload


def _make_digest(*, sections: tuple = ()) -> Digest:
    return Digest(
        summary=DigestSummary(
            total_items=3,
            overdue_count=1,
            today_count=1,
            generated_at=datetime(2025, 6, 15, 8, 30),
        ),
        sections=sections,
    )


class TestBuildPayload:
    def test_has_blocks_key(self) -> None:
        payload = _build_payload(_make_digest())
        assert "blocks" in payload

    def test_header_contains_total(self) -> None:
        payload = _build_payload(_make_digest())
        header_text = payload["blocks"][0]["text"]["text"]
        assert "*3*" in header_text

    def test_section_items_formatted(self) -> None:
        section = DigestSection(
            section_type=DigestSectionType.TODAY,
            items=(
                DigestItem(
                    title="Ship it",
                    source=ItemSource.ASANA,
                    permalink="",
                    due_on=date(2025, 6, 15),
                ),
            ),
        )
        payload = _build_payload(_make_digest(sections=(section,)))
        section_block = payload["blocks"][2]
        assert "Ship it" in section_block["text"]["text"]
        assert "Jun 15" in section_block["text"]["text"]

    def test_item_without_date_has_no_date_suffix(self) -> None:
        section = DigestSection(
            section_type=DigestSectionType.LATER,
            items=(
                DigestItem(
                    title="No deadline",
                    source=ItemSource.ASANA,
                    permalink="",
                ),
            ),
        )
        payload = _build_payload(_make_digest(sections=(section,)))
        section_text = payload["blocks"][2]["text"]["text"]
        assert "• No deadline" in section_text
