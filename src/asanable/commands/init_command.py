"""Interactive setup wizard for asanable."""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel

DEVELOPER_CONSOLE_URL = "https://app.asana.com/0/developer-console"
ENV_FILE_NAME = ".env"


def run_init() -> None:
    """Run the interactive init wizard."""
    console = Console()
    console.print(Panel("asanable setup wizard", style="bold cyan"))

    token = _ask_token(console)
    workspace_gid = _select_workspace(console, token)
    _write_env_file(console, token, workspace_gid)
    _verify_connection(console, token)


def _ask_token(console: Console) -> str:
    """Prompt for the Asana personal access token."""
    console.print(f"\n1. Create a Personal Access Token at: [link]{DEVELOPER_CONSOLE_URL}[/link]")
    console.print("2. Copy the token and paste it below.\n")
    token = console.input("[bold]Asana token: [/]").strip()
    if not token:
        console.print("[red]Token cannot be empty.[/]")
        raise SystemExit(1)
    return token


def _select_workspace(console: Console, token: str) -> str:
    """List workspaces and let the user pick one."""
    workspaces = _fetch_workspaces(token)
    if not workspaces:
        console.print("[red]No workspaces found for this token.[/]")
        raise SystemExit(1)

    if len(workspaces) == 1:
        ws = workspaces[0]
        console.print(f"\nWorkspace: [bold]{ws['name']}[/] ({ws['gid']})")
        return ws["gid"]

    console.print("\nAvailable workspaces:")
    for i, ws in enumerate(workspaces, start=1):
        console.print(f"  [cyan]{i}[/]. {ws['name']} ({ws['gid']})")

    choice = console.input("\n[bold]Choose a workspace (number): [/]").strip()
    try:
        index = int(choice) - 1
        return workspaces[index]["gid"]
    except (ValueError, IndexError) as error:
        console.print("[red]Invalid choice.[/]")
        raise SystemExit(1) from error


def _fetch_workspaces(token: str) -> list[dict]:
    """Fetch workspaces from Asana API using the token."""
    import json
    import urllib.request

    request = urllib.request.Request(
        "https://app.asana.com/api/1.0/workspaces",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        response = urllib.request.urlopen(request, timeout=10)
        data = json.loads(response.read().decode())
        return data.get("data", [])
    except Exception as error:
        from rich.console import Console

        Console(stderr=True).print(f"[red]Failed to connect to Asana: {error}[/]")
        raise SystemExit(1) from error


def _write_env_file(console: Console, token: str, workspace_gid: str) -> None:
    """Generate the .env file."""
    env_path = Path(ENV_FILE_NAME)
    if env_path.exists():
        overwrite = (
            console.input(f"\n[yellow]{ENV_FILE_NAME} already exists. Overwrite? (y/N): [/]")
            .strip()
            .lower()
        )
        if overwrite != "y":
            console.print("Skipped.")
            return

    content = (
        f"ASANA_ACCESS_TOKEN={token}\n"
        f"ASANA_WORKSPACE_GID={workspace_gid}\n"
        f"DIGEST_SCHEDULE_TIME=08:00\n"
    )
    env_path.write_text(content)
    console.print(f"\n[green]{ENV_FILE_NAME} created.[/]")


def _verify_connection(console: Console, token: str) -> None:
    """Quick sanity check — fetch user info and task count."""
    import json
    import urllib.request

    request = urllib.request.Request(
        "https://app.asana.com/api/1.0/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        response = urllib.request.urlopen(request, timeout=10)
        user = json.loads(response.read().decode()).get("data", {})
        console.print(
            f"\nConnected as: [bold]{user.get('name', 'unknown')}[/] ({user.get('email', '')})"
        )
        console.print("\n[green bold]Setup complete. Run `asanable` to see your digest.[/]")
    except Exception:
        console.print(
            "[yellow]Connection check failed, but .env was created. Try running `asanable`.[/]"
        )
