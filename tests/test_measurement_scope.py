from fastapi.testclient import TestClient

import app

client = TestClient(app.app)


def test_status_declares_scope_of_each_measurement():
    scope = client.get("/api/status").json()["scope"]

    assert scope["cpu"] == "host"
    assert scope["memory"] == "host"
    assert scope["disk"] == "host"
    assert scope["processes"] == "container"


def test_dashboard_labels_process_count_with_its_scope():
    html = client.get("/").text

    assert "Processes (${d.scope.processes})" in html
