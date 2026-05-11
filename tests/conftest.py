from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from port_who.models import PortEntry, Protocol


@pytest.fixture
def sample_entry() -> PortEntry:
    return PortEntry(
        port=8080,
        protocol=Protocol.TCP,
        pid=12345,
        process_name="python",
        command="python -m http.server 8080",
        user="testuser",
        cpu_percent=1.5,
        memory_bytes=50 * 1024 * 1024,
        status="LISTEN",
        local_address="127.0.0.1:8080",
        created=1700000000.0,
    )


@pytest.fixture
def sample_entries(sample_entry: PortEntry) -> list[PortEntry]:
    return [
        sample_entry,
        PortEntry(
            port=3000,
            protocol=Protocol.TCP,
            pid=54321,
            process_name="node",
            command="node server.js",
            user="testuser",
            cpu_percent=3.2,
            memory_bytes=85 * 1024 * 1024,
            status="LISTEN",
            local_address="0.0.0.0:3000",
            created=1700000100.0,
        ),
        PortEntry(
            port=5432,
            protocol=Protocol.TCP,
            pid=99999,
            process_name="postgres",
            command="/usr/bin/postgres -D /var/lib/pgsql/data",
            user="postgres",
            cpu_percent=0.8,
            memory_bytes=156 * 1024 * 1024,
            status="LISTEN",
            local_address="0.0.0.0:5432",
            created=1700000200.0,
        ),
    ]


@pytest.fixture
def mock_psutil_connections(monkeypatch: pytest.MonkeyPatch):
    """Fixture that patches psutil.net_connections to return mock data."""

    def _setup(connections):
        monkeypatch.setattr("psutil.net_connections", lambda kind: connections.get(kind, []))

    return _setup


def make_sconn(
    *,
    ip: str = "0.0.0.0",  # noqa: S104
    port: int = 8080,
    status: str = "LISTEN",
    pid: int = 12345,
    family: int | None = None,
    sock_type: int | None = None,
):
    """Create a mock psutil connection."""
    import socket

    conn = MagicMock()
    conn.laddr = MagicMock()
    conn.laddr.ip = ip
    conn.laddr.port = port
    conn.status = status
    conn.pid = pid
    conn.family = family if family is not None else socket.AF_INET
    conn.type = sock_type if sock_type is not None else socket.SOCK_STREAM
    conn.pid = pid
    return conn
