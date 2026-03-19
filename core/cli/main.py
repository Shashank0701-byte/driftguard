import typer
from rich.console import Console
from rich.table import Table
from rich import box
from pathlib import Path
import sys, os

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.engine.parser import parse_compose
from core.engine.snapshotter import snapshot_live
from core.engine.differ import diff, Severity
from core.engine.scorer import score
from core.config import settings

app     = typer.Typer(help="DriftGuard — infrastructure drift detection engine")
console = Console()

SEVERITY_COLORS = {
    Severity.HIGH:   "bold red",
    Severity.MEDIUM: "bold yellow",
    Severity.LOW:    "dim white",
}

@app.command()
def scan(
    compose: str = typer.Option(settings.compose_file_path, help="Path to docker-compose.yml"),
):
    """Scan live Docker state against docker-compose.yml."""
    console.print("\n[bold]DriftGuard[/bold] — scanning...\n")

    try:
        desired = parse_compose(compose)
        actual  = snapshot_live(settings.docker_socket)
        drifts  = diff(desired, actual)
        risk    = score(drifts)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    if not drifts:
        console.print("[bold green]✓ No drift detected. All services match.[/bold green]\n")
        return

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold")
    table.add_column("Service",  style="cyan")
    table.add_column("Field",    style="white")
    table.add_column("Status")
    table.add_column("Expected", style="green")
    table.add_column("Actual",   style="red")
    table.add_column("Severity")

    for d in drifts:
        table.add_row(
            d.service,
            d.field,
            "DRIFT",
            str(d.expected or "—"),
            str(d.actual   or "—"),
            f"[{SEVERITY_COLORS[d.severity]}]{d.severity.value}[/]"
        )

    console.print(table)
    console.print(f"\n[bold]{len(drifts)} drift(s) detected.[/bold] Risk score: [bold red]{risk}[/bold red]")
    console.print("Run [bold]driftguard reconcile --service <name>[/bold] to fix.\n")

@app.command()
def reconcile(
    service: str  = typer.Argument(..., help="Service name to reconcile"),
    compose: str  = typer.Option(settings.compose_file_path, help="Path to docker-compose.yml"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview only, don't apply"),
):
    """Reconcile a drifted service back to desired state."""
    import docker as dk
    console.print(f"\n[bold]Reconciling[/bold] [cyan]{service}[/cyan]...\n")

    try:
        desired  = parse_compose(compose)
        if service not in desired:
            console.print(f"[red]Error:[/red] '{service}' not found in docker-compose.yml")
            raise typer.Exit(1)

        target = desired[service]
        client = dk.DockerClient(base_url=settings.docker_socket)

        if dry_run:
            console.print(f"[yellow]Dry run:[/yellow] would pull {target['image']} and restart {service}")
            return

        console.print(f"Pulling [green]{target['image']}[/green]...")
        client.images.pull(target["image"])

        # Find and stop existing container
        containers = client.containers.list(filters={"label": f"com.docker.compose.service={service}"})
        for c in containers:
            console.print(f"Stopping container [dim]{c.short_id}[/dim]...")
            c.stop()
            c.remove()

        console.print(f"[bold green]✓ Reconciled {service}.[/bold green] Re-run docker-compose up to restart.\n")
        client.close()

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()