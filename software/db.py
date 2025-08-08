# software/db.py
import os
import json
import logging
from datetime import datetime, timezone
import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger("db")
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def load_db_config(path: str = "config_private/db_config.json") -> dict:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"DB config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    required = ["host", "port", "database", "user", "password"]
    missing = [k for k in required if k not in cfg]
    if missing:
        raise KeyError(f"Missing required DB config keys: {missing}")
    return cfg

def get_conn():
    cfg = load_db_config()
    # keep a small connect timeout to fail fast if unreachable
    return psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        dbname=cfg["database"],
        user=cfg["user"],
        password=cfg["password"],
        connect_timeout=cfg.get("connect_timeout", 10),
    )

EPOCH = datetime.fromtimestamp(0, tz=timezone.utc)

def get_offsets_for_rp_ids(rp_ids: list[int]) -> dict[tuple[int, str], datetime]:
    """
    Return a dict {(rp_id, sensor_id): last_ts} for all rows in sensor_offsets
    matching any rp_id in rp_ids.
    """
    if not rp_ids:
        return {}
    sql = """
        SELECT rp_id, sensor_id, last_ts
          FROM sensor_offsets
         WHERE rp_id = ANY(%s)
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # psycopg2 will adapt Python list[int] to int[]
            cur.execute(sql, (rp_ids,))
            result = {(rp, sid): ts for (rp, sid, ts) in cur.fetchall()}
        return result
    finally:
        conn.close()

def upsert_last_ts(offsets: dict[tuple[int, str], datetime]) -> None:
    """
    Upsert sensor_offsets in bulk.
    offsets: {(rp_id, sensor_id): last_ts}
    """
    if not offsets:
        return
    records = [(rp, sid, ts) for (rp, sid), ts in offsets.items()]
    sql = """
        INSERT INTO sensor_offsets (rp_id, sensor_id, last_ts)
        VALUES %s
        ON CONFLICT (rp_id, sensor_id)
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

def insert_readings(rows: list[dict]) -> None:
    """
    Bulk insert into measurements.
    rows items must have keys: timestamp, rp_id, sensor_id, unit, value, value_name
    """
    if not rows:
        return
    sql = """
        INSERT INTO measurements
          ("timestamp", rp_id, sensor_id, unit, value, value_name)
        VALUES %s
    """
    records = [
        (r["timestamp"], r["rp_id"], r["sensor_id"], r["unit"], r["value"], r["value_name"])
        for r in rows
    ]
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            execute_values(cur, sql, records)
        conn.commit()
        logger.info("Inserted %d measurements", len(records))
    finally:
        conn.close()
