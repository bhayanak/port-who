from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label

from port_who.actions.killer import is_system_critical, kill_process

if TYPE_CHECKING:
    from port_who.models import PortEntry


class KillConfirmDialog(ModalScreen[bool]):
    """Modal dialog to confirm killing a process."""

    CSS = """
    KillConfirmDialog {
        align: center middle;
    }
    #kill-dialog {
        width: 60;
        height: auto;
        max-height: 16;
        border: thick $error;
        background: $surface;
        padding: 1 2;
    }
    #kill-dialog Label {
        margin: 1 0;
        width: 100%;
    }
    #kill-buttons {
        layout: horizontal;
        height: 3;
        margin-top: 1;
    }
    #kill-buttons Button {
        width: 1fr;
        margin: 0 1;
    }
    """

    def __init__(self, entry: PortEntry) -> None:
        super().__init__()
        self.entry = entry

    def compose(self) -> ComposeResult:
        e = self.entry
        warning = ""
        if is_system_critical(e.pid, e.process_name):
            warning = "\n[bold red]⚠ This is a system-critical process![/bold red]"

        with Vertical(id="kill-dialog"):
            yield Label(f"[bold]Kill process?[/bold]{warning}")
            yield Label(
                f"[cyan]{e.process_name}[/cyan] (PID {e.pid}) on port {e.port}\n"
                f"User: {e.user} | CPU: {e.cpu_percent:.1f}% | Mem: {e.memory_mb:.1f} MB"
            )
            with Vertical(id="kill-buttons"):
                yield Button("Kill (SIGTERM)", variant="error", id="btn-kill")
                yield Button("Cancel", variant="primary", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-kill":
            success, message = kill_process(self.entry.pid)
            if success:
                self.app.notify(message, severity="warning")
            else:
                self.app.notify(message, severity="error")
            self.dismiss(success)
        else:
            self.dismiss(False)
