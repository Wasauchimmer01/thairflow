"""Utility functions for archiving processed files."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import shutil


def archive_with_date(file_path: str) -> Path:
    """Move *file_path* into the ``archive`` directory with a timestamped name.

    Parameters
    ----------
    file_path:
        Path to the file that should be archived.

    Returns
    -------
    Path
        The destination path of the archived file.
    """
    src = Path(file_path)
    archive_dir = Path("archive")
    archive_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    dest = archive_dir / f"{src.stem}_{timestamp}{src.suffix}"
    shutil.move(str(src), dest)
    return dest
