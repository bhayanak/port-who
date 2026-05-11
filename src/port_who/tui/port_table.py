from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import DataTable

if TYPE_CHECKING:
    from port_who.models import PortEntry

COLUMNS = ("Port", "Proto", "Process", "PID", "User", "CPU%", "Memory", "Status")


class PortTable(DataTable):
    """DataTable widget displaying port entries."""

    def on_mount(self) -> None:
        for col in COLUMNS:
            self.add_column(col, key=col.lower())
        self.cursor_type = "row"
        self.zebra_stripes = True

    def update_entries(self, entries: list[PortEntry]) -> None:
        self.clear()
        for entry in entries:
            mem = f"{entry.memory_mb:.1f} MB"
            self.add_row(
                str(entry.port),
                entry.protocol.value.upper(),
                entry.process_name,
                str(entry.pid),
                entry.user,
                f"{entry.cpu_percent:.1f}",
                mem,
                entry.status,
            )
