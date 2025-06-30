"""Tests for the init wizard."""

import json
from unittest.mock import MagicMock, patch

import pytest

from asanable.commands.init_command import (
    _fetch_workspaces,
    _verify_connection,
    _write_env_file,
)


class TestWriteEnvFile:
    def test_creates_env_file(self, tmp_path) -> None:
        env_file = tmp_path / ".env"
        console = MagicMock()
        with patch("asanable.commands.init_command.Path") as mock_path:
            mock_path.return_value = env_file
            _write_env_file(console, "tok-123", "ws-456")
        content = env_file.read_text()
        assert "ASANA_ACCESS_TOKEN=tok-123" in content
        assert "ASANA_WORKSPACE_GID=ws-456" in content

    def test_skips_if_user_declines_overwrite(self, tmp_path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("existing")
        console = MagicMock()
        console.input.return_value = "n"
        with patch("asanable.commands.init_command.Path") as mock_path:
            mock_instance = MagicMock()
            mock_instance.exists.return_value = True
            mock_path.return_value = mock_instance
            _write_env_file(console, "tok", "ws")
        assert env_file.read_text() == "existing"


class TestFetchWorkspaces:
    @patch("urllib.request.urlopen")
    def test_returns_workspace_list(self, mock_urlopen) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"data": [{"gid": "123", "name": "My WS"}]}
        ).encode()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = _fetch_workspaces("fake-token")
        assert len(result) == 1
        assert result[0]["gid"] == "123"

    @patch("urllib.request.urlopen", side_effect=Exception("timeout"))
    def test_exits_on_failure(self, _mock) -> None:
        with pytest.raises(SystemExit):
            _fetch_workspaces("bad-token")


class TestVerifyConnection:
    @patch("urllib.request.urlopen")
    def test_prints_user_info(self, mock_urlopen) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"data": {"name": "Paco", "email": "paco@test.com"}}
        ).encode()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        console = MagicMock()
        _verify_connection(console, "tok")
        assert any("Paco" in str(call) for call in console.print.call_args_list)

    @patch("urllib.request.urlopen", side_effect=Exception("fail"))
    def test_handles_failure_gracefully(self, _mock) -> None:
        console = MagicMock()
        _verify_connection(console, "tok")
        console.print.assert_called()
