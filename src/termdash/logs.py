"""Log feed with level filters and bounded buffer."""

from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime

LEVELS = ("DEBUG", "INFO", "WARN", "ERROR")


@dataclass(slots=True)
class LogEntry:
    ts: datetime
    level: str
    service: str
    message: str

    def render(self) -> str:
        colors = {"DEBUG": "dim", "INFO": "cyan", "WARN": "yellow", "ERROR": "bold red"}
        color = colors[self.level]
        ts = self.ts.strftime("%H:%M:%S")
        return (
            f"[dim]{ts}[/] [{color}]{self.level:<5}[/] "
            f"[magenta]{self.service:<10}[/] {self.message}"
        )


class LogFeed:
    """Simulated service log generator with a bounded buffer."""

    SERVICES = ("api", "worker", "auth", "db", "cache")
    MESSAGES = {
        "DEBUG": [
            "cache hit ratio {pct}%",
            "pool size {n}, idle {n2}",
            "gc pause {ms:.1f}ms",
            "schedule tick {n}",
        ],
        "INFO": [
            "request served in {ms:.0f}ms",
            "job {n} completed",
            "deployment v1.{n}.0 rolled out",
            "health check passed",
        ],
        "WARN": [
            "retries exceeded for job {n}",
            "slow query: {ms:.0f}ms",
            "memory pressure {pct}%",
            "connection pool nearly exhausted",
        ],
        "ERROR": [
            "upstream timeout after {ms:.0f}ms",
            "job {n} failed: connection refused",
            "unhandled exception in worker-{n}",
            "disk usage {pct}% on /dev/sda1",
        ],
    }

    def __init__(self, buffer_size: int = 500, seed: int | None = None) -> None:
        self._buffer: deque[LogEntry] = deque(maxlen=buffer_size)
        self._rng = random.Random(seed)

    @property
    def entries(self) -> list[LogEntry]:
        return list(self._buffer)

    def generate(self) -> LogEntry:
        # Weighted levels: mostly info/debug, occasional problems.
        level = self._rng.choices(LEVELS, weights=[30, 50, 13, 7], k=1)[0]
        template = self._rng.choice(self.MESSAGES[level])
        message = template.format(
            pct=round(self._rng.uniform(50, 99)),
            n=self._rng.randint(1, 999),
            n2=self._rng.randint(0, 32),
            ms=self._rng.uniform(5, 900),
        )
        entry = LogEntry(
            ts=datetime.now(UTC),
            level=level,
            service=self._rng.choice(self.SERVICES),
            message=message,
        )
        self._buffer.append(entry)
        return entry

    def level_stats(self) -> dict[str, int]:
        stats = {level: 0 for level in LEVELS}
        for e in self._buffer:
            stats[e.level] += 1
        return stats
