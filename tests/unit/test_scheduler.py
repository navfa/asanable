"""Tests for the scheduler module."""

from unittest.mock import MagicMock, patch

from asanable.scheduler.cron import (
    _dispatch,
    _dispatch_slack,
    _dispatch_telegram,
    _run_scheduled_digest,
)


class TestDispatch:
    @patch("asanable.renderers.cli_renderer.CliRenderer")
    def test_always_renders_to_cli(self, mock_renderer_cls: MagicMock) -> None:
        digest = MagicMock()
        settings = MagicMock()
        settings.slack_webhook_url = None
        settings.telegram_bot_token = None
        settings.telegram_chat_id = None

        _dispatch(digest, settings)

        mock_renderer_cls.return_value.render.assert_called_once_with(digest)


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


class TestRunScheduledDigest:
    @patch("asanable.scheduler.cron._dispatch")
    @patch("asanable.scheduler.cron._fetch_tasks")
    @patch("asanable.services.digest_service.build_digest")
    def test_runs_full_pipeline(
        self,
        mock_build: MagicMock,
        mock_fetch: MagicMock,
        mock_dispatch: MagicMock,
    ) -> None:
        settings = MagicMock()
        mock_fetch.return_value = []
        mock_digest = MagicMock()
        mock_build.return_value = mock_digest

        _run_scheduled_digest(settings)

        mock_fetch.assert_called_once_with(settings)
        mock_build.assert_called_once_with([])
        mock_dispatch.assert_called_once_with(mock_digest, settings)

    @patch("asanable.scheduler.cron._fetch_tasks", side_effect=RuntimeError("boom"))
    def test_logs_exception_on_failure(self, _mock_fetch: MagicMock) -> None:
        settings = MagicMock()
        _run_scheduled_digest(settings)
