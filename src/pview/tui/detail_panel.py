from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from textual.widgets import Static

if TYPE_CHECKING:
    from pview.models import PortEntry


class DetailPanel(Static):
    """Sidebar panel showing details of the selected port entry."""

    def on_mount(self) -> None:
        self.update("[dim]Select a row to see details[/dim]")

    def show_entry(self, entry: PortEntry) -> None:
        created_str = (
            datetime.datetime.fromtimestamp(entry.created).strftime("%Y-%m-%d %H:%M:%S")
            if entry.created
            else "unknown"
        )
        text = (
            f"[bold cyan]Port {entry.port}[/bold cyan] ({entry.protocol.value.upper()})\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"[bold]Process:[/bold]  {entry.process_name}\n"
            f"[bold]PID:[/bold]      {entry.pid}\n"
            f"[bold]User:[/bold]     {entry.user}\n"
            f"[bold]CPU:[/bold]      {entry.cpu_percent:.1f}%\n"
            f"[bold]Memory:[/bold]   {entry.memory_mb:.1f} MB\n"
            f"[bold]Status:[/bold]   {entry.status}\n"
            f"[bold]Address:[/bold]  {entry.local_address}\n"
            f"[bold]Started:[/bold]  {created_str}\n\n"
            f"[dim]Command:[/dim]\n{entry.command}\n\n"
            f"[dim]Press [bold]k[/bold] to kill, [bold]r[/bold] to refresh[/dim]"
        )
        self.update(text)
