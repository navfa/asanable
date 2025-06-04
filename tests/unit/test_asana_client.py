"""Tests for AsanaClient — SDK interactions mocked."""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from asana.rest import ApiException

from asanable.clients.asana_client import AsanaClient
from asanable.errors import AsanaAuthError, AsanaConnectionError


@pytest.fixture()
def settings() -> MagicMock:
    mock = MagicMock()
    mock.asana_access_token = "fake-token"
    mock.asana_workspace_gid = "workspace-123"
    return mock


def _make_raw_task(
    *,
    gid: str = "99001",
    name: str = "Ship feature",
    due_on: str | None = "2025-06-15",
    project_name: str = "Backend",
    section_name: str = "To Do",
    permalink_url: str = "https://app.asana.com/0/99001",
) -> dict:
    return {
        "gid": gid,
        "name": name,
        "due_on": due_on,
        "completed": False,
        "permalink_url": permalink_url,
        "memberships": [
            {
                "project": {"name": project_name},
                "section": {"name": section_name},
            }
        ],
    }


class TestFetchMyTasks:
    @patch("asanable.clients.asana_client.asana")
    def test_returns_domain_entities(self, mock_asana_module: MagicMock, settings: MagicMock) -> None:
        raw = _make_raw_task()
        mock_tasks_api = MagicMock()
        mock_tasks_api.get_tasks.return_value = [raw]
        mock_asana_module.TasksApi.return_value = mock_tasks_api
        mock_asana_module.Configuration.return_value = MagicMock()
        mock_asana_module.ApiClient.return_value = MagicMock()

        client = AsanaClient(settings)
        tasks = client.fetch_my_tasks()

        assert len(tasks) == 1
        assert tasks[0].gid == "99001"
        assert tasks[0].name == "Ship feature"
        assert tasks[0].due_on == date(2025, 6, 15)
        assert tasks[0].project_name == "Backend"
        assert tasks[0].section_name == "To Do"

    @patch("asanable.clients.asana_client.asana")
    def test_handles_task_without_due_date(self, mock_asana_module: MagicMock, settings: MagicMock) -> None:
        raw = _make_raw_task(due_on=None)
        mock_tasks_api = MagicMock()
        mock_tasks_api.get_tasks.return_value = [raw]
        mock_asana_module.TasksApi.return_value = mock_tasks_api
        mock_asana_module.Configuration.return_value = MagicMock()
        mock_asana_module.ApiClient.return_value = MagicMock()

        client = AsanaClient(settings)
        tasks = client.fetch_my_tasks()

        assert tasks[0].due_on is None
        assert tasks[0].is_overdue is False

    @patch("asanable.clients.asana_client.asana")
    def test_handles_task_without_memberships(self, mock_asana_module: MagicMock, settings: MagicMock) -> None:
        raw = _make_raw_task()
        raw["memberships"] = []
        mock_tasks_api = MagicMock()
        mock_tasks_api.get_tasks.return_value = [raw]
        mock_asana_module.TasksApi.return_value = mock_tasks_api
        mock_asana_module.Configuration.return_value = MagicMock()
        mock_asana_module.ApiClient.return_value = MagicMock()

        client = AsanaClient(settings)
        tasks = client.fetch_my_tasks()

        assert tasks[0].project_name is None
        assert tasks[0].section_name is None

    @patch("asanable.clients.asana_client.asana")
    def test_empty_workspace_returns_empty_list(self, mock_asana_module: MagicMock, settings: MagicMock) -> None:
        mock_tasks_api = MagicMock()
        mock_tasks_api.get_tasks.return_value = []
        mock_asana_module.TasksApi.return_value = mock_tasks_api
        mock_asana_module.Configuration.return_value = MagicMock()
        mock_asana_module.ApiClient.return_value = MagicMock()

        client = AsanaClient(settings)
        tasks = client.fetch_my_tasks()

        assert tasks == []


class TestErrorHandling:
    @patch("asanable.clients.asana_client.asana")
    def test_auth_error_raises_asana_auth_error(self, mock_asana_module: MagicMock, settings: MagicMock) -> None:
        mock_tasks_api = MagicMock()
        mock_tasks_api.get_tasks.side_effect = ApiException(status=401, reason="Unauthorized")
        mock_asana_module.TasksApi.return_value = mock_tasks_api
        mock_asana_module.Configuration.return_value = MagicMock()
        mock_asana_module.ApiClient.return_value = MagicMock()

        client = AsanaClient(settings)

        with pytest.raises(AsanaAuthError, match="Authentication failed"):
            client.fetch_my_tasks()

    @patch("asanable.clients.asana_client.asana")
    def test_forbidden_raises_asana_auth_error(self, mock_asana_module: MagicMock, settings: MagicMock) -> None:
        mock_tasks_api = MagicMock()
        mock_tasks_api.get_tasks.side_effect = ApiException(status=403, reason="Forbidden")
        mock_asana_module.TasksApi.return_value = mock_tasks_api
        mock_asana_module.Configuration.return_value = MagicMock()
        mock_asana_module.ApiClient.return_value = MagicMock()

        client = AsanaClient(settings)

        with pytest.raises(AsanaAuthError):
            client.fetch_my_tasks()

    @patch("asanable.clients.asana_client.asana")
    def test_server_error_raises_connection_error(self, mock_asana_module: MagicMock, settings: MagicMock) -> None:
        mock_tasks_api = MagicMock()
        mock_tasks_api.get_tasks.side_effect = ApiException(status=500, reason="Server Error")
        mock_asana_module.TasksApi.return_value = mock_tasks_api
        mock_asana_module.Configuration.return_value = MagicMock()
        mock_asana_module.ApiClient.return_value = MagicMock()

        client = AsanaClient(settings)

        with pytest.raises(AsanaConnectionError, match="Asana API error"):
            client.fetch_my_tasks()
