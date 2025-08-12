import sys
import types
from datetime import datetime, timezone
from pathlib import Path

# Provide a minimal psycopg2 stub so db.py can be imported without the real dependency
psycopg2 = types.ModuleType("psycopg2")
psycopg2.connect = lambda *args, **kwargs: None
extras = types.ModuleType("extras")
extras.execute_values = lambda *args, **kwargs: None
psycopg2.extras = extras
sys.modules.setdefault("psycopg2", psycopg2)
sys.modules.setdefault("psycopg2.extras", extras)

from software.db import log_processed_file


def test_log_processed_file_writes_entry(tmp_path, monkeypatch):
    # Run in a temporary directory to avoid polluting repository root
    monkeypatch.chdir(tmp_path)
    archive_path = "archive/some_file.csv"
    ts = datetime(2025, 1, 1, tzinfo=timezone.utc)

    log_processed_file(archive_path, ts)

    log_file = Path("processed_files.log")
    assert log_file.exists()
    assert log_file.read_text() == f"{ts.isoformat()},{archive_path}\n"
