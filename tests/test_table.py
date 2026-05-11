from __future__ import annotations

from rich.table import Table

from pview.models import PortEntry
from pview.output.table import print_table, render_table


class TestRenderTable:
    def test_creates_rich_table(self, sample_entries: list[PortEntry]):
        table = render_table(sample_entries)
        assert isinstance(table, Table)
        assert table.row_count == 3

    def test_empty_entries(self):
        table = render_table([])
        assert table.row_count == 0

    def test_custom_title(self, sample_entries: list[PortEntry]):
        table = render_table(sample_entries, title="Custom")
        assert table.title == "Custom"


class TestPrintTable:
    def test_print_empty(self, capsys):
        # Should not raise
        print_table([])

    def test_print_entries(self, sample_entries: list[PortEntry]):
        # Should not raise
        print_table(sample_entries)
