"""Utility for archiving ingestion files into date-based folders."""

import os
import re
import logging
from pathlib import Path
from typing import Union

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2}|\d{8})")
logger = logging.getLogger("archiver")


def archive_with_date(file_path: Union[str, Path]) -> Path:
    """Move *file_path* into ``archive/<date>/`` based on its name.

    A YYYY-MM-DD or YYYYMMDD substring is extracted from the filename to
    determine the subdirectory. The file is then moved using ``os.replace``
    and the final destination path is returned.
    """

    path = Path(file_path)
    match = DATE_RE.search(path.name)
    if not match:
        raise ValueError(f"No date found in filename: {path.name}")
    date_str = match.group(1)

    dest_dir = Path("archive") / date_str
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / path.name
    os.replace(path, dest)
    logger.info("Archived %s → %s", path, dest)
    return dest
