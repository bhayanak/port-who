from __future__ import annotations

import csv
import io
import json

from port_who.actions.exporter import to_csv, to_json
from port_who.models import PortEntry


class TestToJson:
    def test_empty_list(self):
        result = to_json([])
        assert json.loads(result) == []

    def test_serializes_entries(self, sample_entries: list[PortEntry]):
        result = to_json(sample_entries)
        data = json.loads(result)
        assert len(data) == 3
        assert data[0]["port"] == 8080
        assert data[0]["protocol"] == "tcp"
        assert "memory_mb" in data[0]

    def test_protocol_is_string(self, sample_entry: PortEntry):
        result = to_json([sample_entry])
        data = json.loads(result)
        assert data[0]["protocol"] == "tcp"


class TestToCsv:
    def test_empty_list(self):
        result = to_csv([])
        reader = csv.reader(io.StringIO(result))
        rows = list(reader)
        assert len(rows) == 1  # header only

    def test_serializes_entries(self, sample_entries: list[PortEntry]):
        result = to_csv(sample_entries)
        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)
        assert len(rows) == 3
        assert rows[0]["port"] == "8080"
        assert rows[0]["protocol"] == "tcp"
        assert rows[0]["process_name"] == "python"

    def test_has_correct_headers(self, sample_entry: PortEntry):
        result = to_csv([sample_entry])
        reader = csv.DictReader(io.StringIO(result))
        expected = {
            "port",
            "protocol",
            "pid",
            "process_name",
            "command",
            "user",
            "cpu_percent",
            "memory_mb",
            "status",
            "local_address",
        }
        assert set(reader.fieldnames or []) == expected
