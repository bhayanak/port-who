from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from pview.cli import app
from pview.models import PortEntry, Protocol

runner = CliRunner()


def _mock_entry(port: int = 8080, name: str = "python", pid: int = 12345) -> PortEntry:
    return PortEntry(
        port=port,
        protocol=Protocol.TCP,
        pid=pid,
        process_name=name,
        command=f"{name} server",
        user="testuser",
        cpu_percent=1.0,
        memory_bytes=50 * 1024 * 1024,
        status="LISTEN",
        local_address=f"0.0.0.0:{port}",
        created=1700000000.0,
    )


class TestVersion:
    def test_version_flag(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.stdout


class TestListCommand:
    @patch("pview.cli.scan_ports")
    def test_list_table(self, mock_scan: MagicMock):
        mock_scan.return_value = [_mock_entry()]
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "python" in result.stdout

    @patch("pview.cli.scan_ports")
    def test_list_json(self, mock_scan: MagicMock):
        mock_scan.return_value = [_mock_entry()]
        result = runner.invoke(app, ["list", "--format", "json"])
        assert result.exit_code == 0
        assert '"port": 8080' in result.stdout

    @patch("pview.cli.scan_ports")
    def test_list_csv(self, mock_scan: MagicMock):
        mock_scan.return_value = [_mock_entry()]
        result = runner.invoke(app, ["list", "--format", "csv"])
        assert result.exit_code == 0
        assert "port,protocol" in result.stdout

    @patch("pview.cli.scan_ports")
    def test_list_filter(self, mock_scan: MagicMock):
        mock_scan.return_value = [_mock_entry(name="node"), _mock_entry(name="python", port=9090)]
        result = runner.invoke(app, ["list", "--filter", "node"])
        assert result.exit_code == 0
        assert "node" in result.stdout

    @patch("pview.cli.scan_ports")
    def test_list_no_ports(self, mock_scan: MagicMock):
        mock_scan.return_value = []
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No listening ports" in result.stdout

    def test_watch_json_error(self):
        result = runner.invoke(app, ["list", "--watch", "--format", "json"])
        assert result.exit_code == 1


class TestCheckCommand:
    @patch("pview.cli.check_port")
    def test_port_in_use(self, mock_check: MagicMock):
        mock_check.return_value = _mock_entry(port=3000, name="node")
        result = runner.invoke(app, ["check", "3000"])
        assert result.exit_code == 0
        assert "node" in result.stdout
        assert "3000" in result.stdout

    @patch("pview.cli.check_port")
    def test_port_free(self, mock_check: MagicMock):
        mock_check.return_value = None
        result = runner.invoke(app, ["check", "9999"])
        assert result.exit_code == 0
        assert "free" in result.stdout


class TestKillCommand:
    @patch("pview.cli.kill_process")
    @patch("pview.cli.check_port")
    def test_kill_success(self, mock_check: MagicMock, mock_kill: MagicMock):
        mock_check.return_value = _mock_entry(port=3000, name="node", pid=555)
        mock_kill.return_value = (True, "Killed node (PID 555)")
        result = runner.invoke(app, ["kill", "3000", "--yes"])
        assert result.exit_code == 0
        assert "Killed" in result.stdout

    @patch("pview.cli.check_port")
    def test_kill_port_not_in_use(self, mock_check: MagicMock):
        mock_check.return_value = None
        result = runner.invoke(app, ["kill", "9999"])
        assert result.exit_code == 0
        assert "not in use" in result.stdout

    @patch("pview.cli.check_port")
    def test_kill_system_critical(self, mock_check: MagicMock):
        entry = _mock_entry(port=22, name="sshd", pid=5000)
        mock_check.return_value = entry
        result = runner.invoke(app, ["kill", "22", "--yes"])
        assert result.exit_code == 1
        assert "system-critical" in result.stdout

    @patch("pview.cli.check_port")
    def test_kill_abort(self, mock_check: MagicMock):
        mock_check.return_value = _mock_entry(port=3000, name="node")
        result = runner.invoke(app, ["kill", "3000"], input="n\n")
        assert "Aborted" in result.stdout
