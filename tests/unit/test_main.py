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


class TestHandleError:
    def test_exits_with_code_1(self) -> None:
        with pytest.raises(SystemExit) as exc_info:
            _handle_error(AsanaAuthError("bad token"))
        assert exc_info.value.code == 1


class TestMain:
    @patch("asanable.main._parse_args")
    @patch("asanable.main._run_digest")
    def test_calls_run_digest(self, mock_run: MagicMock, mock_args: MagicMock) -> None:
        mock_args.return_value = MagicMock(schedule=False, init=False)
        main()
        mock_run.assert_called_once()

    @patch("asanable.main._parse_args")
    @patch("asanable.main._run_scheduler")
    def test_calls_scheduler_when_flag_set(
        self, mock_sched: MagicMock, mock_args: MagicMock
    ) -> None:
        mock_args.return_value = MagicMock(schedule=True, init=False)
        main()
        mock_sched.assert_called_once()

    @patch("asanable.main._parse_args")
    @patch("asanable.main._run_init")
    def test_calls_init_when_flag_set(self, mock_init: MagicMock, mock_args: MagicMock) -> None:
        mock_args.return_value = MagicMock(init=True, schedule=False)
        main()
        mock_init.assert_called_once()

    @patch("asanable.main._parse_args")
    @patch("asanable.main._run_digest", side_effect=AsanaAuthError("token expired"))
    @patch("asanable.main._handle_error")
    def test_handles_asanable_error(
        self,
        mock_handle: MagicMock,
        _mock_run: MagicMock,
        mock_args: MagicMock,
    ) -> None:
        mock_args.return_value = MagicMock(schedule=False, init=False)
        main()
        mock_handle.assert_called_once()
