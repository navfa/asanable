"""Tests for GmailClient — helper functions unit tested."""

import base64
from datetime import UTC, datetime

from asanable.clients.gmail_client import (
    _extract_asana_task_gid,
    _extract_body_text,
    _extract_headers,
    _parse_internal_date,
)


class TestExtractHeaders:
    def test_extracts_subject_and_from(self) -> None:
        raw = {
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "New task assigned"},
                    {"name": "From", "value": "notifications@asana.com"},
                ]
            }
        }
        headers = _extract_headers(raw)
        assert headers["Subject"] == "New task assigned"
        assert headers["From"] == "notifications@asana.com"

    def test_empty_headers_returns_empty_dict(self) -> None:
        raw = {"payload": {"headers": []}}
        assert _extract_headers(raw) == {}

    def test_missing_payload_returns_empty_dict(self) -> None:
        assert _extract_headers({}) == {}


class TestExtractBodyText:
    def test_extracts_plain_text_from_parts(self) -> None:
        text = "Check out https://app.asana.com/0/12345/67890"
        encoded = base64.urlsafe_b64encode(text.encode()).decode()
        raw = {
            "payload": {
                "parts": [
                    {"mimeType": "text/plain", "body": {"data": encoded}},
                ]
            }
        }
        assert _extract_body_text(raw) == text

    def test_extracts_from_body_when_no_parts(self) -> None:
        text = "Simple body"
        encoded = base64.urlsafe_b64encode(text.encode()).decode()
        raw = {"payload": {"body": {"data": encoded}}}
        assert _extract_body_text(raw) == text

    def test_empty_message_returns_empty_string(self) -> None:
        assert _extract_body_text({}) == ""


class TestExtractAsanaTaskGid:
    def test_extracts_gid_from_asana_url(self) -> None:
        body = "View task: https://app.asana.com/0/12345/67890/f"
        assert _extract_asana_task_gid(body) == "67890"

    def test_returns_none_when_no_asana_url(self) -> None:
        body = "Just a regular email body"
        assert _extract_asana_task_gid(body) is None

    def test_extracts_first_match(self) -> None:
        body = "https://app.asana.com/0/111/222 and https://app.asana.com/0/333/444"
        assert _extract_asana_task_gid(body) == "222"


class TestParseInternalDate:
    def test_converts_epoch_ms_to_datetime(self) -> None:
        timestamp_ms = "1718012400000"
        result = _parse_internal_date(timestamp_ms)
        expected = datetime(2024, 6, 10, 9, 40, 0, tzinfo=UTC)
        assert result == expected

    def test_zero_returns_epoch(self) -> None:
        result = _parse_internal_date("0")
        assert result == datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
