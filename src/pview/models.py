from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Protocol(Enum):
    TCP = "tcp"
    UDP = "udp"


@dataclass
class PortEntry:
    port: int
    protocol: Protocol
    pid: int
    process_name: str
    command: str
    user: str
    cpu_percent: float
    memory_bytes: int
    status: str
    local_address: str
    created: float = field(default=0.0)

    @property
    def memory_mb(self) -> float:
        return self.memory_bytes / (1024 * 1024)
