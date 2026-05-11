from __future__ import annotations

import pytest

from pview.models import PortEntry, Protocol


class TestPortEntry:
    def test_memory_mb(self, sample_entry: PortEntry):
        assert sample_entry.memory_mb == pytest.approx(50.0, abs=0.1)

    def test_protocol_values(self):
        assert Protocol.TCP.value == "tcp"
        assert Protocol.UDP.value == "udp"

    def test_default_created(self):
        entry = PortEntry(
            port=80,
            protocol=Protocol.TCP,
            pid=1,
            process_name="test",
            command="test",
            user="root",
            cpu_percent=0.0,
            memory_bytes=0,
            status="LISTEN",
            local_address="0.0.0.0:80",
        )
        assert entry.created == 0.0
