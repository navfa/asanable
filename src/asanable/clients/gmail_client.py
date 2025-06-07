"""Gmail API client — handles OAuth2 and returns domain entities."""

import re
from datetime import UTC, datetime
from pathlib import Path

from asanable.config import Settings
from asanable.constants import (
    ASANA_NOTIFICATION_SENDER,
    ASANA_TASK_URL_PATTERN,
    GMAIL_FORMAT_FULL,
    GMAIL_LABEL_UNREAD,
    GMAIL_SCOPE_READONLY,
    GMAIL_USER_ME,
)
from asanable.domain.email import GmailMessage
from asanable.errors import GmailAuthError, GmailConnectionError


class GmailClient:
    """Fetches emails from Gmail via the official Google API."""

    def __init__(self, settings: Settings) -> None:
        self._max_results = settings.max_gmail_results
        self._lookback_hours = settings.gmail_lookback_hours
        self._service = self._build_service(
            settings.gmail_credentials_path,
            settings.gmail_token_path,
        )

    def fetch_asana_notifications(self) -> list[GmailMessage]:
        """Retrieve recent Asana notification emails."""
        query = self._build_asana_query()
        return self._fetch_messages(query)

    def fetch_unread_emails(self) -> list[GmailMessage]:
        """Retrieve recent unread emails."""
        query = self._build_unread_query()
        return self._fetch_messages(query)

    def _fetch_messages(self, query: str) -> list[GmailMessage]:
        """Execute a Gmail search and map results to domain entities."""
        raw_list = self._list_messages(query)
        return [self._get_and_map(entry["id"]) for entry in raw_list]

    def _list_messages(self, query: str) -> list[dict]:
        """Call Gmail API to list message IDs matching a query."""
        try:
            response = (
                self._service.users()
                .messages()
                .list(
                    userId=GMAIL_USER_ME,
                    q=query,
                    maxResults=self._max_results,
                )
                .execute()
            )
        except Exception as error:
            raise GmailConnectionError(f"Failed to list messages: {error}") from error
        return response.get("messages", [])

    def _get_and_map(self, message_id: str) -> GmailMessage:
        """Fetch full message detail and convert to domain entity."""
        raw = self._get_message(message_id)
        return self._to_domain(raw)

    def _get_message(self, message_id: str) -> dict:
        """Fetch a single message by ID."""
        try:
            return (
                self._service.users()
                .messages()
                .get(
                    userId=GMAIL_USER_ME,
                    id=message_id,
                    format=GMAIL_FORMAT_FULL,
                )
                .execute()
            )
        except Exception as error:
            raise GmailConnectionError(f"Failed to get message {message_id}: {error}") from error

    def _build_asana_query(self) -> str:
        """Build Gmail search query for Asana notification emails."""
        return f"from:{ASANA_NOTIFICATION_SENDER} newer_than:{self._lookback_hours}h"

    def _build_unread_query(self) -> str:
        """Build Gmail search query for unread emails."""
        return f"is:unread newer_than:{self._lookback_hours}h"

    @staticmethod
    def _to_domain(raw: dict) -> GmailMessage:
        """Map a raw Gmail API response to a domain entity."""
        headers = _extract_headers(raw)
        body_text = _extract_body_text(raw)
        asana_gid = _extract_asana_task_gid(body_text)
        label_ids = raw.get("labelIds", [])

        return GmailMessage(
            message_id=raw["id"],
            subject=headers.get("Subject", ""),
            sender=headers.get("From", ""),
            snippet=raw.get("snippet", ""),
            received_at=_parse_internal_date(raw.get("internalDate", "0")),
            is_unread=GMAIL_LABEL_UNREAD in label_ids,
            asana_task_gid=asana_gid,
        )

    @staticmethod
    def _build_service(credentials_path: Path, token_path: Path):
        """Authenticate and build the Gmail API service."""
        from googleapiclient.discovery import build

        creds = _load_or_refresh_credentials(token_path)
        if creds is None:
            creds = _run_oauth_flow(credentials_path, token_path)
        return build("gmail", "v1", credentials=creds)


def _load_or_refresh_credentials(token_path: Path):
    """Load existing credentials and refresh if expired."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    if not token_path.exists():
        return None

    creds = Credentials.from_authorized_user_file(str(token_path), [GMAIL_SCOPE_READONLY])
    if creds.valid:
        return creds
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            token_path.write_text(creds.to_json())
            return creds
        except Exception as error:
            raise GmailAuthError(f"Token refresh failed: {error}") from error
    return None


def _run_oauth_flow(credentials_path: Path, token_path: Path):
    """Run the interactive OAuth2 flow and persist the token."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    if not credentials_path.exists():
        raise GmailAuthError(f"Credentials file not found: {credentials_path}")
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path),
            [GMAIL_SCOPE_READONLY],
        )
        creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())
        return creds
    except Exception as error:
        raise GmailAuthError(f"OAuth2 flow failed: {error}") from error


def _extract_headers(raw: dict) -> dict[str, str]:
    """Extract headers as a flat dict from the Gmail payload."""
    payload = raw.get("payload", {})
    headers = payload.get("headers", [])
    return {h["name"]: h["value"] for h in headers}


def _extract_body_text(raw: dict) -> str:
    """Extract the plain text body from a Gmail message."""
    import base64

    payload = raw.get("payload", {})
    parts = payload.get("parts", [])
    for part in parts:
        if part.get("mimeType") == "text/plain":
            data = part.get("body", {}).get("data", "")
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    body_data = payload.get("body", {}).get("data", "")
    if body_data:
        return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="replace")
    return ""


def _extract_asana_task_gid(body_text: str) -> str | None:
    """Extract Asana task GID from email body links."""
    match = re.search(ASANA_TASK_URL_PATTERN, body_text)
    if match:
        return match.group(1)
    return None


def _parse_internal_date(timestamp_ms: str) -> datetime:
    """Convert Gmail internalDate (epoch ms) to a datetime."""
    epoch_seconds = int(timestamp_ms) / 1000
    return datetime.fromtimestamp(epoch_seconds, tz=UTC)
