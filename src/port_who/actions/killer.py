from __future__ import annotations

import os
import signal

import psutil

SYSTEM_PID_THRESHOLD = 100
PROTECTED_NAMES = frozenset(
    {
        "init",
        "systemd",
        "launchd",
        "kernel",
        "kthreadd",
        "sshd",
        "loginwindow",
        "WindowServer",
    }
)


def is_system_critical(pid: int, name: str) -> bool:
    """Check if a process is system-critical and should not be killed."""
    if pid < SYSTEM_PID_THRESHOLD:
        return True
    return name.lower() in {n.lower() for n in PROTECTED_NAMES}


def is_owned_by_current_user(pid: int) -> bool:
    """Check if the process is owned by the current user."""
    try:
        proc = psutil.Process(pid)
        return proc.uids().real == os.getuid()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def kill_process(pid: int, *, force: bool = False) -> tuple[bool, str]:
    """Kill a process by PID.

    Returns (success, message).
    Uses SIGTERM by default, SIGKILL with force=True.
    """
    try:
        proc = psutil.Process(pid)
        name = proc.name()
    except psutil.NoSuchProcess:
        return False, f"Process {pid} no longer exists"

    if is_system_critical(pid, name):
        return False, f"Refusing to kill system-critical process: {name} (PID {pid})"

    sig = signal.SIGKILL if force else signal.SIGTERM
    try:
        proc.send_signal(sig)
        proc.wait(timeout=5)
        return True, f"Killed {name} (PID {pid}) with {sig.name}"
    except psutil.TimeoutExpired:
        if not force:
            return False, f"{name} (PID {pid}) did not terminate; retry with --force"
        return False, f"{name} (PID {pid}) did not respond to {sig.name}"
    except psutil.AccessDenied:
        return False, f"Permission denied killing {name} (PID {pid}). Try with sudo."
    except psutil.NoSuchProcess:
        return True, f"Process {pid} already exited"
