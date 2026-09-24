import sqlite3

DB_PATH = "metrics.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            timestamp TEXT,
            cpu REAL,
            memory REAL,
            disk REAL,
            net_sent REAL,
            net_recv REAL,
            processes INTEGER
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            timestamp TEXT,
            metric TEXT,
            value REAL,
            message TEXT
        )
    """)

    return conn
