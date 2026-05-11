from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from port_who.models import PortEntry


def to_json(entries: list[PortEntry], *, indent: int = 2) -> str:
    """Export port entries to JSON string."""
    data = []
    for e in entries:
        d = asdict(e)
        d["protocol"] = e.protocol.value
        d["memory_mb"] = round(e.memory_mb, 1)
        data.append(d)
    return json.dumps(data, indent=indent)


def to_csv(entries: list[PortEntry]) -> str:
    """Export port entries to CSV string."""
    output = io.StringIO()
    fields = [
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
    ]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for e in entries:
        writer.writerow(
            {
                "port": e.port,
                "protocol": e.protocol.value,
                "pid": e.pid,
                "process_name": e.process_name,
                "command": e.command,
                "user": e.user,
                "cpu_percent": e.cpu_percent,
                "memory_mb": round(e.memory_mb, 1),
                "status": e.status,
                "local_address": e.local_address,
            }
        )
    return output.getvalue()
