import psycopg2
from psycopg2.extras import execute_values
import logging
import json
import os
from datetime import datetime

# ── Logging ──────────────────────────────────────────────────────────────
logger = logging.getLogger("db")
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

# ── Config loader ────────────────────────────────────────────────────────
def load_db_config(path: str = "config_private/db_config.json") -> dict:
    """
    Load database configuration JSON with keys:
    host, port, database, user, password
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"DB config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    required = ["host", "port", "database", "user", "password"]
    missing = [k for k in required if k not in cfg]
    if missing:
        raise KeyError(f"Missing required DB config keys: {missing}")

    return cfg

# ── Connection helper ───────────────────────────────────────────────────
def get_conn():
    cfg = load_db_config()
    return psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        dbname=cfg["database"],
        user=cfg["user"],
        password=cfg["password"],
    )

# ── Offsets API ─────────────────────────────────────────────────────────
def get_last_ts(rpi_id: str, sensor_id: str) -> datetime:
    """
    Return last_ts for (rpi_id, sensor_id) from sensor_offsets,
    or epoch if no row exists yet.
    """
    sql = """
        SELECT last_ts
          FROM sensor_offsets
         WHERE rpi_id = %s AND sensor_id = %s
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (rpi_id, sensor_id))
            row = cur.fetchone()
            if row:
                return row[0]
            return datetime.fromtimestamp(0)
    finally:
        conn.close()

def upsert_last_ts(offsets: dict):
    """
    Bulk upsert last_ts values into sensor_offsets.
    offsets: dict { (rpi_id, sensor_id): datetime }
    """
    if not offsets:
        return

    records = [
        (rpi_id, sensor_id, ts)
        for (rpi_id, sensor_id), ts in offsets.items()
    ]
    sql = """
    INSERT INTO sensor_offsets (rpi_id, sensor_id, last_ts)
    VALUES %s
    ON CONFLICT (rpi_id, sensor_id)
      DO UPDATE SET last_ts = EXCLUDED.last_ts
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            execute_values(cur, sql, records)
        conn.commit()
        logger.info("Upserted %d offsets", len(records))
    finally:
        conn.close()

# ── Readings insert ─────────────────────────────────────────────────────
def insert_readings(rows: list):
    """
    Bulk insert sensor reading rows into sensor_readings.
    Each dict in rows must have keys:
      rpi_id, sensor_id, ts, value_num, value_bool, unit
    """
    if not rows:
        return

    sql = """
    INSERT INTO sensor_readings
      (rpi_id, sensor_id, ts, value, value_bool, unit)
    VALUES %s
    ON CONFLICT DO NOTHING
    """
    records = [
        (
            row["rpi_id"],
            row["sensor_id"],
            row["ts"],
            row.get("value_num"),
            row.get("value_bool"),
            row["unit"],
        )
        for row in rows
    ]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            execute_values(cur, sql, records)
        conn.commit()
        logger.info("Inserted %d readings", len(records))
    finally:
        conn.close()
