# termdash

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue)](.github/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Realtime operations dashboard **in your terminal**, powered by
[Textual](https://textual.textualize.io/) — live metric gauges, a streaming
log feed with level filters, and a level-count table.

![dashboard screenshot](docs/screenshot.svg)

## Features

- Rolling metric buffers with warn/crit thresholds and level-colored gauges
- Simulated metrics source (CPU, memory, request rate, latency, network) —
  swap `SimulatedSource` for real collectors (psutil, Prometheus, etc.)
- Streaming log feed: weighted level generation, bounded buffer, markup render
- Keyboard-driven: `p` pause · `l` cycle log filter · `c` clear · `q` quit

## Run

```bash
cd termdash
python -m venv .venv && source .venv/Scripts/activate
pip install -e .

termdash          # or: python -m termdash.app
```

> On Windows shells, if box-drawing characters look broken, run with `PYTHONUTF8=1`.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

## Wiring real data

Replace `SimulatedSource.sample()` with anything returning the same dict of
floats — e.g. `psutil.cpu_percent()`, `psutil.virtual_memory().percent`, or
 polled HTTP endpoints. The dashboard logic is source-agnostic.
