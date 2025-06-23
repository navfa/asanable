"""Asana API client — encapsulates the SDK and returns domain entities."""

from datetime import date

import asana
from asana.rest import ApiException

from asanable.config import Settings
from asanable.domain.task import AsanaTask
from asanable.errors import AsanaAuthError, AsanaConnectionError

TASK_OPT_FIELDS = [
    "name",
    "due_on",
    "completed",
    "permalink_url",
    "memberships.section.name",
    "memberships.project.name",
]

ASSIGNEE_ME = "me"
COMPLETED_SINCE_NOW = "now"


class AsanaClient:
    """Fetches assigned tasks from the Asana API."""

    def __init__(self, settings: Settings) -> None:
        self._workspace_gid = settings.asana_workspace_gid
        self._api_client = self._build_api_client(settings.asana_access_token)

    def fetch_my_tasks(self) -> list[AsanaTask]:
        """Retrieve all incomplete tasks assigned to the authenticated user."""
        raw_tasks = self._request_assigned_tasks()
        return [self._to_domain(task) for task in raw_tasks]

    def _request_assigned_tasks(self) -> list[dict]:
        """Call the Asana API to get assigned incomplete tasks."""
        tasks_api = asana.TasksApi(self._api_client)
        try:
            response = tasks_api.get_tasks(
                {
                    "assignee": ASSIGNEE_ME,
                    "workspace": self._workspace_gid,
                    "completed_since": COMPLETED_SINCE_NOW,
                    "opt_fields": ",".join(TASK_OPT_FIELDS),
                    "limit": 100,
                },
            )
            return list(response)
        except ApiException as error:
            raise self._classify_api_error(error) from error

    def _to_domain(self, raw: dict) -> AsanaTask:
        """Map a raw Asana API response dict to a domain entity."""
        project_name = self._extract_project_name(raw)
        section_name = self._extract_section_name(raw)
        due_on = self._parse_due_date(raw.get("due_on"))

        return AsanaTask(
            gid=raw["gid"],
            name=raw["name"],
            due_on=due_on,
            project_name=project_name,
            section_name=section_name,
            permalink_url=raw.get("permalink_url", ""),
        )

    @staticmethod
    def _build_api_client(access_token: str) -> asana.ApiClient:
        """Create a configured Asana API client."""
        configuration = asana.Configuration()
        configuration.access_token = access_token
        return asana.ApiClient(configuration)

    @staticmethod
    def _extract_project_name(raw: dict) -> str | None:
        """Extract the first project name from task memberships."""
        memberships = raw.get("memberships", [])
        if not memberships:
            return None
        project = memberships[0].get("project", {})
        return project.get("name")

    @staticmethod
    def _extract_section_name(raw: dict) -> str | None:
        """Extract the first section name from task memberships."""
        memberships = raw.get("memberships", [])
        if not memberships:
            return None
        section = memberships[0].get("section", {})
        return section.get("name")

    @staticmethod
    def _parse_due_date(due_on_str: str | None) -> date | None:
        """Parse a YYYY-MM-DD string into a date object."""
        if due_on_str is None:
            return None
        return date.fromisoformat(due_on_str)

    @staticmethod
    def _classify_api_error(error: ApiException) -> AsanaAuthError | AsanaConnectionError:
        """Convert an Asana SDK exception to a domain-specific error."""
        if error.status in (401, 403):
            return AsanaAuthError(f"Authentication failed: {error.reason}")
        return AsanaConnectionError(f"Asana API error ({error.status}): {error.reason}")
