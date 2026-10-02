"""Headless smoke test for the dashboard UI."""

from __future__ import annotations

import asyncio

from termdash.app import DashboardApp


def test_dashboard_smoke() -> None:
    async def _run() -> None:
        app = DashboardApp(tick_interval=0.05)
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            # a few ticks produced metrics + logs
            assert app.metrics["cpu"].latest is not None
            assert app.log_feed.entries
            # keyboard actions work
            await pilot.press("p")
            assert app.paused
            await pilot.press("p")
            assert not app.paused
            await pilot.press("l")
            assert app.sub_title.startswith("filter:")
            await pilot.press("c")

    asyncio.run(_run())
