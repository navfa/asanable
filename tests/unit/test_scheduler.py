"""Tests for the scheduler module."""

from unittest.mock import MagicMock, patch

from asanable.scheduler.cron import (
    _dispatch,
    _dispatch_email,
    _dispatch_slack,
    _dispatch_telegram,
    _fetch_emails,
    _run_scheduled_digest,
)


class TestDispatch:
    @patch("asanable.renderers.cli_renderer.CliRenderer")
    def test_always_renders_to_cli(self, mock_renderer_cls: MagicMock) -> None:
        digest = MagicMock()
        settings = MagicMock()
        settings.digest_email_to = None
        settings.slack_webhook_url = None
        settings.telegram_bot_token = None
        settings.telegram_chat_id = None

        _dispatch(digest, settings)

        mock_renderer_cls.return_value.render.assert_called_once_with(digest)


class TestDispatchEmail:
    def test_skips_when_not_configured(self) -> None:
        settings = MagicMock()
        settings.digest_email_to = None
        _dispatch_email(MagicMock(), settings)

    @patch("asanable.renderers.html_renderer.render_html", return_value="<html></html>")
    def test_renders_html_when_configured(self, mock_render: MagicMock) -> None:
        settings = MagicMock()
        settings.digest_email_to = "test@example.com"
        _dispatch_email(MagicMock(), settings)
        mock_render.assert_called_once()


class TestDispatchSlack:
    def test_skips_when_not_configured(self) -> None:
        settings = MagicMock()
        settings.slack_webhook_url = None
        _dispatch_slack(MagicMock(), settings)

    @patch("asanable.renderers.slack_renderer.send_slack_digest")
    def test_sends_when_configured(self, mock_send: MagicMock) -> None:
        settings = MagicMock()
        settings.slack_webhook_url = "https://hooks.slack.com/xxx"
        digest = MagicMock()
        _dispatch_slack(digest, settings)
        mock_send.assert_called_once_with(digest, "https://hooks.slack.com/xxx")


class TestDispatchTelegram:
    def test_skips_when_token_missing(self) -> None:
        settings = MagicMock()
        settings.telegram_bot_token = None
        settings.telegram_chat_id = "123"
        _dispatch_telegram(MagicMock(), settings)

    def test_skips_when_chat_id_missing(self) -> None:
        settings = MagicMock()
        settings.telegram_bot_token = "tok"
        settings.telegram_chat_id = None
        _dispatch_telegram(MagicMock(), settings)

    @patch("asanable.renderers.telegram_renderer.send_telegram_digest")
    def test_sends_when_configured(self, mock_send: MagicMock) -> None:
        settings = MagicMock()
        settings.telegram_bot_token = "tok"
        settings.telegram_chat_id = "123"
        digest = MagicMock()
        _dispatch_telegram(digest, settings)
        mock_send.assert_called_once_with(digest, "tok", "123")


class TestFetchEmails:
    def test_returns_empty_when_no_credentials(self) -> None:
        settings = MagicMock()
        settings.gmail_credentials_path.exists.return_value = False
        assert _fetch_emails(settings) == []

    @patch("asanable.clients.gmail_client.GmailClient")
    def test_returns_combined_emails(self, mock_client_cls: MagicMock) -> None:
        settings = MagicMock()
        settings.gmail_credentials_path.exists.return_value = True
        mock_client = mock_client_cls.return_value
        mock_client.fetch_asana_notifications.return_value = ["a"]
        mock_client.fetch_unread_emails.return_value = ["b"]
        result = _fetch_emails(settings)
        assert result == ["a", "b"]


class TestRunScheduledDigest:
    @patch("asanable.scheduler.cron._dispatch")
    @patch("asanable.scheduler.cron._fetch_all_sources")
    @patch("asanable.services.digest_service.build_digest")
    def test_runs_full_pipeline(
        self,
        mock_build: MagicMock,
        mock_fetch: MagicMock,
        mock_dispatch: MagicMock,
    ) -> None:
        settings = MagicMock()
        mock_fetch.return_value = ([], [])
        mock_digest = MagicMock()
        mock_build.return_value = mock_digest

        _run_scheduled_digest(settings)

        mock_fetch.assert_called_once_with(settings)
        mock_build.assert_called_once_with([], [])
        mock_dispatch.assert_called_once_with(mock_digest, settings)

    @patch("asanable.scheduler.cron._fetch_all_sources", side_effect=RuntimeError("boom"))
    def test_logs_exception_on_failure(self, _mock_fetch: MagicMock) -> None:
        settings = MagicMock()
        _run_scheduled_digest(settings)
