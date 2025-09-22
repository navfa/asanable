"""Tests for the CLI entry point."""

from unittest.mock import MagicMock, patch

import pytest

from asanable.errors import AsanaAuthError
from asanable.main import _handle_error, _parse_args, main


class TestParseArgs:
    def test_default_args(self) -> None:
        with patch("sys.argv", ["asanable"]):
            args = _parse_args()
        assert args.quiet is False
        assert args.schedule is False
        assert args.cache is False
        assert args.refresh is False
        assert args.overdue is False
        assert args.today is False
        assert args.output == "cli"
        assert args.project is None

    def test_quiet_flag(self) -> None:
        with patch("sys.argv", ["asanable", "--quiet"]):
            args = _parse_args()
        assert args.quiet is True

    def test_short_quiet_flag(self) -> None:
        with patch("sys.argv", ["asanable", "-q"]):
            args = _parse_args()
        assert args.quiet is True

    def test_schedule_flag(self) -> None:
        with patch("sys.argv", ["asanable", "--schedule"]):
            args = _parse_args()
        assert args.schedule is True

    def test_cache_flag(self) -> None:
        with patch("sys.argv", ["asanable", "--cache"]):
            args = _parse_args()
        assert args.cache is True

    def test_refresh_flag(self) -> None:
        with patch("sys.argv", ["asanable", "--refresh"]):
            args = _parse_args()
        assert args.refresh is True

    def test_overdue_flag(self) -> None:
        with patch("sys.argv", ["asanable", "--overdue"]):
            args = _parse_args()
        assert args.overdue is True

    def test_today_flag(self) -> None:
        with patch("sys.argv", ["asanable", "--today"]):
            args = _parse_args()
        assert args.today is True

    def test_output_html(self) -> None:
        with patch("sys.argv", ["asanable", "-o", "html"]):
            args = _parse_args()
        assert args.output == "html"

    def test_project_flag(self) -> None:
        with patch("sys.argv", ["asanable", "-p", "Mobile"]):
            args = _parse_args()
        assert args.project == "Mobile"

    def test_init_flag(self) -> None:
        with patch("sys.argv", ["asanable", "--init"]):
            args = _parse_args()
        assert args.init is True


class TestHandleError:
    def test_exits_with_code_1(self) -> None:
        with pytest.raises(SystemExit) as exc_info:
            _handle_error(AsanaAuthError("bad token"))
        assert exc_info.value.code == 1


class TestMain:
    @patch("asanable.main._parse_args")
    @patch("asanable.main._run_digest")
    def test_calls_run_digest(self, mock_run: MagicMock, mock_args: MagicMock) -> None:
        mock_args.return_value = MagicMock(
            schedule=False, init=False, done=None, open=None, completions=None
        )
        main()
        mock_run.assert_called_once()

    @patch("asanable.main._parse_args")
    @patch("asanable.main._run_scheduler")
    def test_calls_scheduler_when_flag_set(
        self, mock_sched: MagicMock, mock_args: MagicMock
    ) -> None:
        mock_args.return_value = MagicMock(
            schedule=True, init=False, done=None, open=None, completions=None
        )
        main()
        mock_sched.assert_called_once()

    @patch("asanable.main._parse_args")
    @patch("asanable.main._run_init")
    def test_calls_init_when_flag_set(self, mock_init: MagicMock, mock_args: MagicMock) -> None:
        mock_args.return_value = MagicMock(
            init=True, schedule=False, done=None, open=None, completions=None
        )
        main()
        mock_init.assert_called_once()

    @patch("asanable.main._parse_args")
    @patch("asanable.main._mark_done")
    def test_calls_mark_done(self, mock_done: MagicMock, mock_args: MagicMock) -> None:
        mock_args.return_value = MagicMock(
            init=False, schedule=False, done="12345", open=None, completions=None
        )
        main()
        mock_done.assert_called_once_with("12345")

    @patch("asanable.main._parse_args")
    @patch("asanable.main._open_task")
    def test_calls_open_task(self, mock_open: MagicMock, mock_args: MagicMock) -> None:
        mock_args.return_value = MagicMock(
            init=False, schedule=False, done=None, open="67890", completions=None
        )
        main()
        mock_open.assert_called_once_with("67890")

    @patch("asanable.main._parse_args")
    @patch("asanable.main._run_digest", side_effect=AsanaAuthError("token expired"))
    @patch("asanable.main._handle_error")
    def test_handles_asanable_error(
        self,
        mock_handle: MagicMock,
        _mock_run: MagicMock,
        mock_args: MagicMock,
    ) -> None:
        mock_args.return_value = MagicMock(
            schedule=False, init=False, done=None, open=None, completions=None
        )
        main()
        mock_handle.assert_called_once()
