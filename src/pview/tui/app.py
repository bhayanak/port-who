from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer, Header, Input, Static

from pview.collectors.port_scanner import scan_ports
from pview.models import PortEntry
from pview.tui.confirm_dialog import KillConfirmDialog
from pview.tui.detail_panel import DetailPanel
from pview.tui.port_table import PortTable


class PviewApp(App):
    """pview — Beautiful Port Inspector TUI."""

    TITLE = "pview"
    SUB_TITLE = "Beautiful Port Inspector"
    CSS = """
    Screen {
        layout: vertical;
    }
    #filter-bar {
        dock: top;
        height: 3;
        padding: 0 1;
        background: $surface;
    }
    #filter-input {
        width: 1fr;
    }
    #main-area {
        height: 1fr;
    }
    #port-table {
        width: 3fr;
    }
    #detail-panel {
        width: 1fr;
        min-width: 30;
        border-left: tall $primary;
        padding: 1;
    }
    #status-bar {
        dock: bottom;
        height: 1;
        padding: 0 1;
        background: $accent;
        color: $text;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("k", "kill_selected", "Kill"),
        Binding("r", "refresh_data", "Refresh"),
        Binding("d", "toggle_detail", "Details"),
        Binding("/", "focus_filter", "Filter"),
        Binding("escape", "clear_filter", "Clear Filter"),
    ]

    _entries: list[PortEntry] = []
    _filtered: list[PortEntry] = []
    _show_detail: bool = True

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Input(placeholder="Filter by port or process name…", id="filter-input"),
            id="filter-bar",
        )
        yield Horizontal(
            PortTable(id="port-table"),
            DetailPanel(id="detail-panel"),
            id="main-area",
        )
        yield Static("Loading…", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self._load_data()
        self.set_interval(5, self._load_data)

    def _load_data(self) -> None:
        self._entries = scan_ports()
        self._apply_filter()

    def _apply_filter(self) -> None:
        filter_input = self.query_one("#filter-input", Input)
        query = filter_input.value.strip().lower()
        if query:
            self._filtered = [
                e for e in self._entries if query in e.process_name.lower() or query in str(e.port)
            ]
        else:
            self._filtered = list(self._entries)
        table = self.query_one(PortTable)
        table.update_entries(self._filtered)
        status = self.query_one("#status-bar", Static)
        total = len(self._entries)
        shown = len(self._filtered)
        status.update(f" {shown} ports | {total} total | Press / to filter, r to refresh")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "filter-input":
            self._apply_filter()

    def on_data_table_row_selected(self, event: PortTable.RowSelected) -> None:
        self._update_detail_for_row(event.cursor_row)

    def on_data_table_row_highlighted(self, event: PortTable.RowHighlighted) -> None:
        self._update_detail_for_row(event.cursor_row)

    def _update_detail_for_row(self, row_index: int) -> None:
        if 0 <= row_index < len(self._filtered):
            detail = self.query_one(DetailPanel)
            detail.show_entry(self._filtered[row_index])

    def action_refresh_data(self) -> None:
        self._load_data()
        self.notify("Refreshed!", timeout=1)

    def action_focus_filter(self) -> None:
        self.query_one("#filter-input", Input).focus()

    def action_clear_filter(self) -> None:
        filter_input = self.query_one("#filter-input", Input)
        filter_input.value = ""
        self.query_one(PortTable).focus()

    def action_toggle_detail(self) -> None:
        panel = self.query_one("#detail-panel")
        self._show_detail = not self._show_detail
        panel.display = self._show_detail

    def action_kill_selected(self) -> None:
        table = self.query_one(PortTable)
        row_index = table.cursor_row
        if 0 <= row_index < len(self._filtered):
            entry = self._filtered[row_index]
            self.push_screen(KillConfirmDialog(entry), self._on_kill_result)

    def _on_kill_result(self, result: bool) -> None:
        if result:
            self._load_data()
            self.notify("Process killed.", severity="warning", timeout=2)
