import pytest
from fastapi.testclient import TestClient

import alerting
import app
import database

client = TestClient(app.app)
_seq = 0


def seed_latest(cpu, memory, disk):
    global _seq
    _seq += 1
    conn = database.get_db()
    conn.execute(
        "INSERT INTO metrics VALUES (?, ?, ?, ?, ?, ?, ?)",
        (f"2099-02-{_seq:02d}T00:00:00+00:00", cpu, memory, disk, 0.0, 0.0, 1),
    )
    conn.commit()
    conn.close()


@pytest.mark.parametrize(
    "cpu, memory, disk, expected",
    [
        (75.0, 10.0, 10.0, "healthy"),
        (10.0, 75.0, 10.0, "healthy"),
        (10.0, 10.0, 90.0, "healthy"),
        (75.1, 10.0, 10.0, "warning"),
        (10.0, 75.1, 10.0, "warning"),
        (10.0, 10.0, 90.1, "warning"),
    ],
)
def test_status_agrees_with_alerting_rule(cpu, memory, disk, expected):
    seed_latest(cpu, memory, disk)
    status = client.get("/api/status").json()["status"]
    readings = (("cpu", cpu), ("memory", memory), ("disk", disk))
    alert_raised = any(alerting.check_threshold(m, v) for m, v in readings)

    assert status == expected
    assert (status == "warning") == alert_raised


def test_thresholds_are_defined_in_one_place():
    assert app.THRESHOLDS is alerting.THRESHOLDS
