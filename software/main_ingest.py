#!/usr/bin/env python3
# software/main_ingest.py

import os
import logging
from datetime import datetime
from software.email_poller import poll_for_reports_once  # a slight helper you’ll add
from software.csv_parser     import parse_csv
from software.db             import (
    get_last_ts,
    upsert_last_ts,
    insert_readings,
)

# ───── Logging Setup ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main_ingest")

# ─────── Orchestration ──────────────────────────────────────────────────────
def main():
    # 1) Poll mailbox once, save attachments, get list of (rpi_id, file_path)
    attachments = poll_for_reports_once()
    if not attachments:
        logger.info("No new reports found. Exiting.")
        return

    # Ensure archive folder exists
    os.makedirs("archive", exist_ok=True)

    # 2) Process each downloaded CSV
    for rpi_id, csv_path in attachments:
        logger.info("Processing %s from RPi %s", csv_path, rpi_id)

        # 2a) Parse into row‐dicts
        rows = parse_csv(rpi_id, csv_path)
        if not rows:
            logger.warning("No readings parsed from %s", csv_path)
            archive(csv_path)
            continue

        # 2b) Delta‐filter and collect offset updates
        new_rows = []
        offsets: dict[(str, str), datetime] = {}
        for row in rows:
            key = (row["rpi_id"], row["sensor_id"])
            last_ts = get_last_ts(*key)
            if row["ts"] > last_ts:
                new_rows.append(row)
                offsets[key] = max(offsets.get(key, last_ts), row["ts"])

        # 2c) Insert and update offsets
        if new_rows:
            insert_readings(new_rows)
            upsert_last_ts(offsets)
            logger.info("Inserted %d new rows from %s", len(new_rows), csv_path)
        else:
            logger.info("No new data in %s", csv_path)

        # 2d) Archive the file so we don’t reprocess it
        archive(csv_path)

def archive(path: str):
    """Move a processed file into archive/"""
    dest = os.path.join("archive", os.path.basename(path))
    os.replace(path, dest)
    logger.info("Archived %s → %s", path, dest)

if __name__ == "__main__":
    main()
