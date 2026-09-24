from fastapi.testclient import TestClient
import app

client = TestClient(app.app)


def test_status_endpoint():
    response = client.get("/api/status")

    assert response.status_code == 200

    data = response.json()

    assert "cpu" in data
    assert "memory" in data
    assert "disk" in data
    assert "processes" in data
    assert "uptime" in data
    assert "status" in data


def test_metrics_endpoint():
    response = client.get("/api/metrics")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if data:
        assert "timestamp" in data[0]
        assert "cpu" in data[0]
        assert "memory" in data[0]
        assert "disk" in data[0]


def test_alerts_endpoint():
    response = client.get("/api/alerts")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if data:
        assert "timestamp" in data[0]
        assert "metric" in data[0]
        assert "value" in data[0]
        assert "message" in data[0]
