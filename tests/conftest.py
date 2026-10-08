import tempfile
from pathlib import Path

import database

# Point the database at a throwaway file before any test module imports app.
# Importing app writes a reading at import time, so this must happen first.
_test_db_dir = tempfile.mkdtemp(prefix="monitor-tests-")
database.DB_PATH = str(Path(_test_db_dir) / "test_metrics.db")
