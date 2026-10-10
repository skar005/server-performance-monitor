import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_db_path_is_configurable_by_environment():
    env = dict(os.environ, MONITOR_DB_PATH="/data/metrics.db")
    result = subprocess.run(
        [sys.executable, "-c", "import database; print(database.DB_PATH)"],
        cwd=ROOT, env=env, capture_output=True, text=True, check=True,
    )
    assert result.stdout.strip() == "/data/metrics.db"
