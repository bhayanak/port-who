from __future__ import annotations

from unittest.mock import MagicMock, patch

import psutil

from conftest import make_sconn
from port_who.collectors.port_scanner import _build_entry, check_port, scan_ports
from port_who.models import Protocol


class TestBuildEntry:
    def test_returns_none_when_process_gone(self):
        conn = make_sconn(pid=999999)
        with patch("psutil.Process", side_effect=psutil.NoSuchProcess(999999)):
            assert _build_entry(conn, 8080, Protocol.TCP, 999999) is None

    def test_builds_valid_entry(self):
        conn = make_sconn(port=8080, pid=12345)
        mock_proc = MagicMock()
        mock_proc.name.return_value = "python"
        mock_proc.cmdline.return_value = ["python", "-m", "http.server"]
        mock_proc.username.return_value = "testuser"
        mock_proc.cpu_percent.return_value = 1.5
        mock_proc.memory_info.return_value = MagicMock(rss=50 * 1024 * 1024)
        mock_proc.create_time.return_value = 1700000000.0
        mock_proc.oneshot.return_value.__enter__ = lambda s: s
        mock_proc.oneshot.return_value.__exit__ = MagicMock(return_value=False)

        with patch("psutil.Process", return_value=mock_proc):
            entry = _build_entry(conn, 8080, Protocol.TCP, 12345)

        assert entry is not None
        assert entry.port == 8080
        assert entry.process_name == "python"
        assert entry.pid == 12345
        assert entry.user == "testuser"
        assert entry.memory_bytes == 50 * 1024 * 1024

    def test_handles_access_denied_for_user(self):
        conn = make_sconn(port=8080, pid=12345)
        mock_proc = MagicMock()
        mock_proc.name.return_value = "secure_proc"
        mock_proc.cmdline.return_value = []
        mock_proc.username.side_effect = psutil.AccessDenied(12345)
        mock_proc.cpu_percent.return_value = 0.0
        mock_proc.memory_info.return_value = MagicMock(rss=0)
        mock_proc.create_time.return_value = 0.0
        mock_proc.oneshot.return_value.__enter__ = lambda s: s
        mock_proc.oneshot.return_value.__exit__ = MagicMock(return_value=False)

        with patch("psutil.Process", return_value=mock_proc):
            entry = _build_entry(conn, 8080, Protocol.TCP, 12345)

        assert entry is not None
        assert entry.user == "?"


class TestScanPorts:
    def test_filters_non_listen_tcp(self):
        conn_listen = make_sconn(port=80, status="LISTEN", pid=100)
        conn_established = make_sconn(port=81, status="ESTABLISHED", pid=101)

        mock_proc = MagicMock()
        mock_proc.name.return_value = "test"
        mock_proc.cmdline.return_value = ["test"]
        mock_proc.username.return_value = "user"
        mock_proc.cpu_percent.return_value = 0.0
        mock_proc.memory_info.return_value = MagicMock(rss=0)
        mock_proc.create_time.return_value = 0.0
        mock_proc.oneshot.return_value.__enter__ = lambda s: s
        mock_proc.oneshot.return_value.__exit__ = MagicMock(return_value=False)

        with (
            patch("psutil.net_connections", return_value=[conn_listen, conn_established]),
            patch("psutil.Process", return_value=mock_proc),
        ):
            entries = scan_ports(tcp=True, udp=False)

        assert len(entries) == 1
        assert entries[0].port == 80

    def test_handles_access_denied_falls_back(self):
        conn = make_sconn(port=80, status="LISTEN", pid=100)
        mock_proc = MagicMock()
        mock_proc.name.return_value = "test"
        mock_proc.cmdline.return_value = ["test"]
        mock_proc.username.return_value = "user"
        mock_proc.cpu_percent.return_value = 0.0
        mock_proc.memory_info.return_value = MagicMock(rss=0)
        mock_proc.create_time.return_value = 0.0
        mock_proc.oneshot.return_value.__enter__ = lambda s: s
        mock_proc.oneshot.return_value.__exit__ = MagicMock(return_value=False)
        mock_proc.net_connections.return_value = [conn]

        with (
            patch("psutil.net_connections", side_effect=psutil.AccessDenied(0)),
            patch("psutil.process_iter", return_value=[mock_proc]),
            patch("psutil.Process", return_value=mock_proc),
        ):
            entries = scan_ports()
        assert len(entries) == 1
        assert entries[0].port == 80

    def test_deduplicates_ports(self):
        conn1 = make_sconn(port=8080, pid=100)
        conn2 = make_sconn(port=8080, pid=100)

        mock_proc = MagicMock()
        mock_proc.name.return_value = "test"
        mock_proc.cmdline.return_value = ["test"]
        mock_proc.username.return_value = "user"
        mock_proc.cpu_percent.return_value = 0.0
        mock_proc.memory_info.return_value = MagicMock(rss=0)
        mock_proc.create_time.return_value = 0.0
        mock_proc.oneshot.return_value.__enter__ = lambda s: s
        mock_proc.oneshot.return_value.__exit__ = MagicMock(return_value=False)

        with (
            patch("psutil.net_connections", return_value=[conn1, conn2]),
            patch("psutil.Process", return_value=mock_proc),
        ):
            entries = scan_ports(tcp=True, udp=False)

        assert len(entries) == 1

    def test_sorted_by_port(self):
        conn1 = make_sconn(port=9000, pid=100)
        conn2 = make_sconn(port=80, pid=101)

        mock_proc = MagicMock()
        mock_proc.name.return_value = "test"
        mock_proc.cmdline.return_value = ["test"]
        mock_proc.username.return_value = "user"
        mock_proc.cpu_percent.return_value = 0.0
        mock_proc.memory_info.return_value = MagicMock(rss=0)
        mock_proc.create_time.return_value = 0.0
        mock_proc.oneshot.return_value.__enter__ = lambda s: s
        mock_proc.oneshot.return_value.__exit__ = MagicMock(return_value=False)

        with (
            patch("psutil.net_connections", return_value=[conn1, conn2]),
            patch("psutil.Process", return_value=mock_proc),
        ):
            entries = scan_ports(tcp=True, udp=False)

        assert entries[0].port < entries[1].port


class TestCheckPort:
    def test_returns_entry_when_found(self):
        conn = make_sconn(port=3000, pid=200)
        mock_proc = MagicMock()
        mock_proc.name.return_value = "node"
        mock_proc.cmdline.return_value = ["node", "server.js"]
        mock_proc.username.return_value = "user"
        mock_proc.cpu_percent.return_value = 0.0
        mock_proc.memory_info.return_value = MagicMock(rss=0)
        mock_proc.create_time.return_value = 0.0
        mock_proc.oneshot.return_value.__enter__ = lambda s: s
        mock_proc.oneshot.return_value.__exit__ = MagicMock(return_value=False)

        with (
            patch("psutil.net_connections", return_value=[conn]),
            patch("psutil.Process", return_value=mock_proc),
        ):
            entry = check_port(3000)

        assert entry is not None
        assert entry.port == 3000
        assert entry.process_name == "node"

    def test_returns_none_when_not_found(self):
        with patch("psutil.net_connections", return_value=[]):
            assert check_port(9999) is None
