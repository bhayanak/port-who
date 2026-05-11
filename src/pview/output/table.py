from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from pview.models import PortEntry


def render_table(entries: list[PortEntry], *, title: str = "pview") -> Table:
    """Build a Rich table from port entries."""
    table = Table(title=title, show_lines=False, expand=True)
    table.add_column("Port", style="cyan bold", justify="right", width=7)
    table.add_column("Proto", style="dim", width=5)
    table.add_column("Process", style="green bold", min_width=10)
    table.add_column("PID", style="yellow", justify="right", width=8)
    table.add_column("User", style="magenta", min_width=8)
    table.add_column("CPU%", justify="right", width=6)
    table.add_column("Memory", justify="right", min_width=10)
    table.add_column("Status", style="dim", width=12)
    table.add_column("Address", style="dim")

    for e in entries:
        cpu_style = "red bold" if e.cpu_percent > 50 else "yellow" if e.cpu_percent > 10 else ""
        mem = f"{e.memory_mb:.1f} MB"

        table.add_row(
            str(e.port),
            e.protocol.value.upper(),
            e.process_name,
            str(e.pid),
            e.user,
            f"{e.cpu_percent:.1f}",
            mem,
            e.status,
            e.local_address,
            style=cpu_style if cpu_style else None,
        )

    return table


def print_table(entries: list[PortEntry], *, title: str = "pview") -> None:
    """Print a Rich table of port entries to the console."""
    console = Console()
    if not entries:
        console.print("[yellow]No listening ports found.[/yellow]")
        return
    table = render_table(entries, title=title)
    console.print(table)
