from fastapi.testclient import TestClient

import app
import database

client = TestClient(app.app)


def test_alerts_endpoint_returns_full_alert_record():
    conn = database.get_db()
    conn.execute(
        "INSERT INTO alerts VALUES (?, ?, ?, ?)",
        ("2099-01-01T00:00:00+00:00", "cpu", 99.0, "CPU is high: 99.0%"),
    )
    conn.commit()
    conn.close()

    alerts = client.get("/api/alerts").json()
    match = [a for a in alerts if a["message"] == "CPU is high: 99.0%"]

    assert match
    assert match[0]["metric"] == "cpu"
    assert match[0]["value"] == 99.0
