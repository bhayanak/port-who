from __future__ import annotations

import os
import time
from enum import Enum

import typer
from rich.console import Console
from rich.live import Live

from pview import __version__
from pview.actions.exporter import to_csv, to_json
from pview.actions.killer import is_system_critical, kill_process
from pview.collectors.port_scanner import check_port, scan_ports
from pview.output.table import print_table, render_table

console = Console()
app = typer.Typer(
    name="pview",
    help="Beautiful Port Inspector TUI — see who's using your ports.",
    no_args_is_help=False,
    invoke_without_command=True,
)


class OutputFormat(str, Enum):
    table = "table"
    json = "json"
    csv = "csv"


def version_callback(value: bool) -> None:
    if value:
        console.print(f"pview {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool | None = typer.Option(  # noqa: UP007
        None,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """pview — Beautiful Port Inspector TUI."""
    if ctx.invoked_subcommand is None:
        _launch_tui()


def _launch_tui() -> None:
    """Launch the Textual TUI."""
    try:
        from pview.tui.app import PviewApp

        app_tui = PviewApp()
        app_tui.run()
    except ImportError as exc:
        console.print(
            "[red]Textual is required for TUI mode. Install with: pip install textual[/red]"
        )
        raise typer.Exit(1) from exc


@app.command("list")
def list_(
    watch: bool = typer.Option(False, "--watch", "-w", help="Live-updating view."),
    filter_: str | None = typer.Option(  # noqa: B008
        None,
        "--filter",
        "-f",
        help="Filter by process name.",
    ),
    fmt: OutputFormat = typer.Option(  # noqa: B008
        OutputFormat.table,
        "--format",
        help="Output format.",
    ),
    tcp: bool = typer.Option(True, "--tcp/--no-tcp", help="Include TCP ports."),
    udp: bool = typer.Option(True, "--udp/--no-udp", help="Include UDP ports."),
    refresh: float = typer.Option(
        2.0,
        "--refresh",
        "-r",
        help="Refresh interval for watch mode.",
    ),
) -> None:
    """List all listening ports with process details."""
    if watch and fmt != OutputFormat.table:
        console.print("[red]Watch mode only works with table format.[/red]")
        raise typer.Exit(1)

    if watch:
        _watch_mode(tcp=tcp, udp=udp, filter_name=filter_, refresh=refresh)
    else:
        entries = scan_ports(tcp=tcp, udp=udp)
        if filter_:
            entries = [e for e in entries if filter_.lower() in e.process_name.lower()]

        if fmt == OutputFormat.json:
            console.print(to_json(entries))
        elif fmt == OutputFormat.csv:
            console.print(to_csv(entries), end="")
        else:
            print_table(entries)


def _watch_mode(
    *,
    tcp: bool,
    udp: bool,
    filter_name: str | None,
    refresh: float,
) -> None:
    """Live-updating table display."""
    try:
        with Live(console=console, refresh_per_second=1) as live:
            while True:
                entries = scan_ports(tcp=tcp, udp=udp)
                if filter_name:
                    entries = [e for e in entries if filter_name.lower() in e.process_name.lower()]
                table = render_table(entries, title=f"pview (watching every {refresh}s)")
                live.update(table)
                time.sleep(refresh)
    except KeyboardInterrupt:
        console.print("\n[dim]Stopped watching.[/dim]")


@app.command()
def check(
    port: int = typer.Argument(..., help="Port number to check."),
) -> None:
    """Check if a specific port is in use."""
    entry = check_port(port)
    if entry:
        console.print(
            f"[red]Port {port}[/red]: [green]{entry.process_name}[/green] "
            f"(PID [yellow]{entry.pid}[/yellow]) — {entry.command}"
        )
    else:
        console.print(f"[green]✅ Port {port} is free.[/green]")


@app.command()
def kill(
    port: int = typer.Argument(..., help="Port number whose process to kill."),
    force: bool = typer.Option(False, "--force", "-9", help="Use SIGKILL instead of SIGTERM."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Kill the process listening on a port."""
    entry = check_port(port)
    if not entry:
        console.print(f"[green]Port {port} is not in use.[/green]")
        raise typer.Exit()

    if is_system_critical(entry.pid, entry.process_name):
        console.print(
            f"[red]⚠ {entry.process_name} (PID {entry.pid}) is system-critical. "
            f"Refusing to kill.[/red]"
        )
        raise typer.Exit(1)

    if os.getuid() == 0:
        console.print("[yellow]⚠ Running as root — be careful![/yellow]")

    if not yes:
        confirmed = typer.confirm(f"Kill {entry.process_name} (PID {entry.pid}) on port {port}?")
        if not confirmed:
            console.print("[dim]Aborted.[/dim]")
            raise typer.Exit()

    success, message = kill_process(entry.pid, force=force)
    if success:
        console.print(f"[green]✅ {message}[/green]")
    else:
        console.print(f"[red]❌ {message}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
