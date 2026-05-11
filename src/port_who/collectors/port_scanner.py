from __future__ import annotations

import socket

import psutil

from port_who.models import PortEntry, Protocol

# Map psutil socket families/types to our protocol enum
_TCP_TYPES = {socket.SOCK_STREAM}
_UDP_TYPES = {socket.SOCK_DGRAM}
_INET_FAMILIES = {socket.AF_INET, socket.AF_INET6}


def _conn_protocol(conn: psutil._common.sconn) -> Protocol | None:
    """Determine the protocol of a connection, or None if not inet TCP/UDP."""
    if conn.family not in _INET_FAMILIES:
        return None
    if conn.type in _TCP_TYPES:
        return Protocol.TCP
    if conn.type in _UDP_TYPES:
        return Protocol.UDP
    return None


def _is_listening(conn: psutil._common.sconn, proto: Protocol) -> bool:
    """Check whether a connection represents a listening socket."""
    if proto == Protocol.TCP:
        return conn.status == "LISTEN"
    # UDP sockets don't have a LISTEN status; they show as NONE
    return conn.status in ("NONE", "")


# Each collected item is (connection, port, protocol, pid)
_ConnTuple = tuple[object, int, Protocol, int]


def _collect_via_net_connections(
    *,
    tcp: bool,
    udp: bool,
) -> list[_ConnTuple]:
    """Try the fast path: system-wide psutil.net_connections()."""
    results: list[_ConnTuple] = []
    kinds: list[str] = []
    if tcp:
        kinds.extend(["tcp", "tcp6"])
    if udp:
        kinds.extend(["udp", "udp6"])

    for kind in kinds:
        try:
            connections = psutil.net_connections(kind=kind)
        except (psutil.AccessDenied, OSError):
            raise  # signal caller to fall back
        for conn in connections:
            proto = _conn_protocol(conn)
            if proto is None:
                continue
            if not _is_listening(conn, proto):
                continue
            if not conn.laddr:
                continue
            pid = getattr(conn, "pid", None)
            if pid is None:
                continue
            results.append((conn, conn.laddr.port, proto, pid))
    return results


def _collect_via_process_iter(
    *,
    tcp: bool,
    udp: bool,
) -> list[_ConnTuple]:
    """Slow but reliable fallback: iterate over each process's connections."""
    results: list[_ConnTuple] = []
    for proc in psutil.process_iter(["pid"]):
        try:
            pid = proc.pid
            conns = proc.net_connections(kind="inet")
        except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
            continue
        for conn in conns:
            proto = _conn_protocol(conn)
            if proto is None:
                continue
            if not tcp and proto == Protocol.TCP:
                continue
            if not udp and proto == Protocol.UDP:
                continue
            if not _is_listening(conn, proto):
                continue
            if not conn.laddr:
                continue
            results.append((conn, conn.laddr.port, proto, pid))
    return results


def _collect_connections(
    *,
    tcp: bool,
    udp: bool,
) -> list[_ConnTuple]:
    """Collect listening connections, falling back to per-process iteration."""
    try:
        return _collect_via_net_connections(tcp=tcp, udp=udp)
    except (psutil.AccessDenied, OSError):
        return _collect_via_process_iter(tcp=tcp, udp=udp)


def scan_ports(
    *,
    tcp: bool = True,
    udp: bool = True,
) -> list[PortEntry]:
    """Scan all listening ports and return enriched PortEntry objects."""
    entries: list[PortEntry] = []
    seen: set[tuple[int, str]] = set()

    for conn, port, proto, pid in _collect_connections(tcp=tcp, udp=udp):
        key = (port, proto.value)
        if key in seen:
            continue
        seen.add(key)

        entry = _build_entry(conn, port, proto, pid)
        if entry:
            entries.append(entry)

    entries.sort(key=lambda e: e.port)
    return entries


def check_port(port: int) -> PortEntry | None:
    """Check if a specific port is in use and return its entry."""
    for conn, cport, proto, pid in _collect_connections(tcp=True, udp=True):
        if cport != port:
            continue
        entry = _build_entry(conn, port, proto, pid)
        if entry:
            return entry
    return None


def _build_entry(
    conn: object, port: int, proto: Protocol, pid: int,
) -> PortEntry | None:

    try:
        proc = psutil.Process(pid)
        with proc.oneshot():
            name = proc.name()
            cmdline = proc.cmdline()
            command = " ".join(cmdline) if cmdline else name
            try:
                user = proc.username()
            except (psutil.AccessDenied, KeyError):
                user = "?"
            try:
                cpu = proc.cpu_percent(interval=0)
            except psutil.AccessDenied:
                cpu = 0.0
            try:
                mem = proc.memory_info().rss
            except psutil.AccessDenied:
                mem = 0
            try:
                created = proc.create_time()
            except psutil.AccessDenied:
                created = 0.0
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

    local_addr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else f"*:{port}"

    return PortEntry(
        port=port,
        protocol=proto,
        pid=pid,
        process_name=name,
        command=command,
        user=user,
        cpu_percent=cpu,
        memory_bytes=mem,
        status=conn.status or "LISTEN",
        local_address=local_addr,
        created=created,
    )
