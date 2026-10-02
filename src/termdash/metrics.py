"""Metrics engine: ring buffers, simulated data sources, thresholds."""

from __future__ import annotations

import random
import statistics
from collections import deque
from dataclasses import dataclass
from itertools import count


@dataclass(slots=True)
class MetricConfig:
    name: str
    unit: str
    history: int = 240
    warn_above: float | None = None
    crit_above: float | None = None


class Metric:
    """Bounded rolling time series with threshold evaluation."""

    def __init__(self, config: MetricConfig) -> None:
        self.config = config
        self._values: deque[float] = deque(maxlen=config.history)
        self._seq = count()

    def push(self, value: float) -> None:
        self._values.append(value)

    @property
    def values(self) -> list[float]:
        return list(self._values)

    @property
    def latest(self) -> float | None:
        return self._values[-1] if self._values else None

    @property
    def avg(self) -> float:
        return statistics.fmean(self._values) if self._values else 0.0

    @property
    def max(self) -> float:
        return max(self._values) if self._values else 0.0

    def level(self) -> str:
        """'ok' | 'warn' | 'crit' based on the latest value."""
        v = self.latest
        if v is None:
            return "ok"
        if self.config.crit_above is not None and v > self.config.crit_above:
            return "crit"
        if self.config.warn_above is not None and v > self.config.warn_above:
            return "warn"
        return "ok"


class SimulatedSource:
    """Generates plausible CPU / memory / network / request-rate samples."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._cpu_base = 35.0
        self._tick = 0

    def sample(self) -> dict[str, float]:
        self._tick += 1
        # Random-walk CPU with occasional spikes.
        self._cpu_base = min(95.0, max(5.0, self._cpu_base + self._rng.uniform(-6, 6)))
        cpu = self._cpu_base + (25.0 if self._rng.random() < 0.06 else 0.0)
        mem = 55 + self._rng.uniform(-5, 8) + (self._tick % 120) / 40
        net_in = max(0.0, self._rng.gauss(120, 45))
        net_out = max(0.0, self._rng.gauss(80, 30))
        rps = max(0.0, self._rng.gauss(240, 60) + (150 if cpu > 80 else 0))
        latency = max(1.0, self._rng.gauss(38 + cpu / 3, 12))
        return {
            "cpu": min(100.0, cpu),
            "mem": min(100.0, mem),
            "net_in": net_in,
            "net_out": net_out,
            "rps": rps,
            "latency": latency,
        }


def default_metrics() -> dict[str, Metric]:
    return {
        "cpu": Metric(MetricConfig("CPU", "%", warn_above=70, crit_above=90)),
        "mem": Metric(MetricConfig("Memory", "%", warn_above=75, crit_above=92)),
        "rps": Metric(MetricConfig("Requests/s", "req/s")),
        "latency": Metric(MetricConfig("Latency", "ms", warn_above=80, crit_above=150)),
        "net_in": Metric(MetricConfig("Net in", "KB/s")),
        "net_out": Metric(MetricConfig("Net out", "KB/s")),
    }
