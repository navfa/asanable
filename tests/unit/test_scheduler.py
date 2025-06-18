"""Tests for the scheduler module."""

from unittest.mock import MagicMock, patch

from asanable.scheduler.cron import _dispatch, _run_scheduled_digest


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

    @patch("asanable.renderers.cli_renderer.CliRenderer")
    def test_dispatches_all_channels(self, _mock_renderer_cls: MagicMock) -> None:
        digest = MagicMock()
        settings = MagicMock()
        settings.digest_email_to = None
        settings.slack_webhook_url = None
        settings.telegram_bot_token = None
        settings.telegram_chat_id = None

        _dispatch(digest, settings)

        _mock_renderer_cls.return_value.render.assert_called_once()


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
