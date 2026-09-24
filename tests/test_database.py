import database


def test_database_creates_tables(tmp_path):
    original_db_path = database.DB_PATH

    try:
        database.DB_PATH = str(tmp_path / "test_metrics.db")

        conn = database.get_db()

        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }

        conn.close()

        assert "metrics" in tables
        assert "alerts" in tables

    finally:
        database.DB_PATH = original_db_path


def test_metric_can_be_stored(tmp_path):
    original_db_path = database.DB_PATH

    try:
        database.DB_PATH = str(tmp_path / "test_metrics.db")

        conn = database.get_db()

        conn.execute(
            """
            INSERT INTO metrics
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ("2026-09-24T12:00:00", 50.0, 40.0, 20.0, 100.0, 200.0, 10),
        )
        conn.commit()

        row = conn.execute(
            "SELECT cpu, memory, disk, processes FROM metrics"
        ).fetchone()

        conn.close()

        assert row == (50.0, 40.0, 20.0, 10)

    finally:
        database.DB_PATH = original_db_path
