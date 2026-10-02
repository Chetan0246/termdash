"""Tests for termdash metrics engine and log feed."""

from __future__ import annotations

from termdash.logs import LogFeed
from termdash.metrics import Metric, MetricConfig, SimulatedSource, default_metrics


def test_metric_ring_buffer_and_stats() -> None:
    m = Metric(MetricConfig("cpu", "%", history=5))
    for v in (10, 20, 30, 40, 50, 60):
        m.push(v)
    assert len(m.values) == 5  # bounded
    assert m.latest == 60
    assert m.avg == 40.0
    assert m.max == 60.0


def test_metric_threshold_levels() -> None:
    m = Metric(MetricConfig("cpu", "%", warn_above=70, crit_above=90))
    m.push(50)
    assert m.level() == "ok"
    m.push(75)
    assert m.level() == "warn"
    m.push(95)
    assert m.level() == "crit"


def test_simulated_source_sample_shape() -> None:
    src = SimulatedSource(seed=1)
    sample = src.sample()
    assert set(sample) == {"cpu", "mem", "net_in", "net_out", "rps", "latency"}
    assert 0 <= sample["cpu"] <= 100
    assert sample["net_in"] >= 0
    # deterministic with seed
    a = SimulatedSource(seed=3).sample()
    b = SimulatedSource(seed=3).sample()
    assert a == b


def test_default_metrics_registry() -> None:
    metrics = default_metrics()
    assert set(metrics) == {"cpu", "mem", "rps", "latency", "net_in", "net_out"}


def test_log_feed_generates_and_counts() -> None:
    feed = LogFeed(buffer_size=10, seed=5)
    for _ in range(25):
        entry = feed.generate()
        assert entry.level in ("DEBUG", "INFO", "WARN", "ERROR")
        assert entry.service in feed.SERVICES
        assert entry.message
    stats = feed.level_stats()
    assert sum(stats.values()) == 10  # bounded buffer
    assert all(v >= 0 for v in stats.values())


def test_log_entry_render_contains_fields() -> None:
    feed = LogFeed(buffer_size=5, seed=2)
    entry = feed.generate()
    rendered = entry.render()
    assert entry.level in rendered
    assert entry.service in rendered
