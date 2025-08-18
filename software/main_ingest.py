
import os
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Tuple

from software.email_poller import poll_for_reports_once
from software.csv_parser import parse_csv
from software.db import (
    get_offsets_for_rp_ids,
    upsert_last_ts,
    insert_readings,
    ensure_sensors,      # FK safety
)
from software.archiver import archive_with_date

logger = logging.getLogger(__name__)

EPOCH = datetime.fromtimestamp(0, tz=timezone.utc)
CHUNK_SIZE = 50_000  # tweak for your DB/network


def _sleep_with_countdown(minutes: int = 15) -> None:
    for remaining in range(minutes, 0, -1):
        logger.info("Retrying in %d minute(s)...", remaining)
        time.sleep(60)


def run_forever() -> None:
    os.makedirs("archive", exist_ok=True)

    while True:
        try:
            # 1) Pull any new emails; robust to IMAP OVERQUOTA
            attachments = poll_for_reports_once()
            if not attachments:
                logger.info("No new reports found.")
                _sleep_with_countdown()
                continue

            # 2) Process each downloaded CSV independently
            for rp_id, csv_path in attachments:
                try:
                    logger.info("Processing %s from RPi %s", csv_path, rp_id)

                    rows = parse_csv(rp_id, csv_path)
                    if not rows:
                        logger.warning("No readings parsed from %s", csv_path)
                        archive_with_date(csv_path)
                        continue

                    # 3) Bulk fetch existing offsets for the rp_id(s) in this file
                    rp_ids = sorted({r["rp_id"] for r in rows})
                    offsets: Dict[Tuple[int, str], datetime] = get_offsets_for_rp_ids(
                        rp_ids
                    )

                    # 4) In-memory delta filter against offsets
                    new_rows = []
                    updated_offsets: Dict[Tuple[int, str], datetime] = {}

                    for r in rows:
                        key = (r["rp_id"], r["sensor_id"])
                        last_ts = offsets.get(key, EPOCH)
                        if r["timestamp"] > last_ts:
                            new_rows.append(r)
                            if r["timestamp"] > updated_offsets.get(key, last_ts):
                                updated_offsets[key] = r["timestamp"]

                    if new_rows:
                        # Make FK safe
                        missing_ids = {r["sensor_id"] for r in new_rows}
                        ensure_sensors(missing_ids)

                        logger.info("New rows to insert: %d", len(new_rows))

                        # 5) Insert in chunks so partial progress is still committed
                        start = 0
                        while start < len(new_rows):
                            end = min(start + CHUNK_SIZE, len(new_rows))
                            insert_readings(new_rows[start:end])
                            start = end

                        # 6) Upsert offsets once per file
                        upsert_last_ts(updated_offsets)
                    else:
                        logger.info("No new data in %s", csv_path)

                    # 7) Only archive if the file was fully handled
                    archive_with_date(csv_path)

                except Exception:
                    # If a file fails, leave it in downloads so the next run can retry
                    logger.exception(
                        "Failed while ingesting %s; leaving file for retry", csv_path
                    )
        except Exception:
            logger.exception("Error during ingestion loop")
            _sleep_with_countdown()


if __name__ == "__main__":
    from software.logging_setup import setup_logging

    setup_logging()
    run_forever()
