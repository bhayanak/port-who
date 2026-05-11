from __future__ import annotations

import signal
from unittest.mock import MagicMock, patch

import psutil

from pview.actions.killer import (
    is_owned_by_current_user,
    is_system_critical,
    kill_process,
)


class TestIsSystemCritical:
    def test_low_pid(self):
        assert is_system_critical(1, "init") is True
        assert is_system_critical(99, "anything") is True

    def test_high_pid_not_critical(self):
        assert is_system_critical(5000, "myapp") is False

    def test_protected_name(self):
        assert is_system_critical(5000, "sshd") is True
        assert is_system_critical(5000, "launchd") is True
        assert is_system_critical(5000, "systemd") is True

    def test_case_insensitive(self):
        assert is_system_critical(5000, "SSHD") is True
        assert is_system_critical(5000, "Launchd") is True


class TestIsOwnedByCurrentUser:
    def test_process_not_found(self):
        with patch("psutil.Process", side_effect=psutil.NoSuchProcess(99999)):
            assert is_owned_by_current_user(99999) is False

    def test_access_denied(self):
        with patch("psutil.Process", side_effect=psutil.AccessDenied(99999)):
            assert is_owned_by_current_user(99999) is False


class TestKillProcess:
    def test_process_not_found(self):
        with patch("psutil.Process", side_effect=psutil.NoSuchProcess(99999)):
            success, msg = kill_process(99999)
        assert success is False
        assert "no longer exists" in msg

    def test_system_critical_refused(self):
        mock_proc = MagicMock()
        mock_proc.name.return_value = "sshd"
        with patch("psutil.Process", return_value=mock_proc):
            success, msg = kill_process(5000)
        assert success is False
        assert "system-critical" in msg

    def test_successful_kill(self):
        mock_proc = MagicMock()
        mock_proc.name.return_value = "myapp"
        mock_proc.send_signal.return_value = None
        mock_proc.wait.return_value = None
        with patch("psutil.Process", return_value=mock_proc):
            success, msg = kill_process(5000)
        assert success is True
        assert "Killed" in msg
        mock_proc.send_signal.assert_called_once_with(signal.SIGTERM)

    def test_force_kill(self):
        mock_proc = MagicMock()
        mock_proc.name.return_value = "stubborn"
        mock_proc.send_signal.return_value = None
        mock_proc.wait.return_value = None
        with patch("psutil.Process", return_value=mock_proc):
            success, msg = kill_process(5000, force=True)
        assert success is True
        mock_proc.send_signal.assert_called_once_with(signal.SIGKILL)

    def test_access_denied(self):
        mock_proc = MagicMock()
        mock_proc.name.return_value = "privileged"
        mock_proc.send_signal.side_effect = psutil.AccessDenied(5000)
        with patch("psutil.Process", return_value=mock_proc):
            success, msg = kill_process(5000)
        assert success is False
        assert "Permission denied" in msg

    def test_timeout_without_force(self):
        mock_proc = MagicMock()
        mock_proc.name.return_value = "hanging"
        mock_proc.send_signal.return_value = None
        mock_proc.wait.side_effect = psutil.TimeoutExpired(5)
        with patch("psutil.Process", return_value=mock_proc):
            success, msg = kill_process(5000)
        assert success is False
        assert "--force" in msg

    def test_already_exited(self):
        mock_proc = MagicMock()
        mock_proc.name.return_value = "gone"
        mock_proc.send_signal.side_effect = psutil.NoSuchProcess(5000)
        with patch("psutil.Process", return_value=mock_proc):
            success, msg = kill_process(5000)
        assert success is True
        assert "already exited" in msg
