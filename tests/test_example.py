"""An example to start from. Run with: uv run pytest

The raw data and the cost counters live in module-level state, so all tests in
one run share them. Compare /stats before and after a call to see what it cost.
"""

from fastapi.testclient import TestClient

from app.main import app


def test_stats_reports_rows_and_cost():
    with TestClient(app) as client:
        stats = client.get("/stats").json()
    assert stats["cost_rp"] == stats["rows_scanned"] * 0.05
