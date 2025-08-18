# software/db.py
import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Tuple, List, Set

import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)

# ---------- config / connection ----------

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
    return psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        dbname=cfg["database"],
        user=cfg["user"],
        password=cfg["password"],
        connect_timeout=cfg.get("connect_timeout", 10),
    )

EPOCH = datetime.fromtimestamp(0, tz=timezone.utc)

# ---------- offsets helpers ----------

def get_offsets_for_rp_ids(rp_ids: List[int]) -> Dict[Tuple[int, str], datetime]:
    """
    Return {(rp_id, sensor_id): last_ts} for all rows in sensor_offsets
    whose rp_id is in rp_ids.
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
            cur.execute(sql, (rp_ids,))
            result = {(rp, sid): ts for (rp, sid, ts) in cur.fetchall()}
        return result
    finally:
        conn.close()

def upsert_last_ts(offsets: Dict[Tuple[int, str], datetime]) -> None:
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

# ---------- FK safety: sensors seeding ----------

def _derive_sensor_type(sensor_id: str) -> str:
    """
    From 'Base_123.Measurement' → 'Base'
    e.g. 'SFA30_93.Rh' -> 'SFA30'
         'Differenzdrucksensor_37.DifferentialPressure' -> 'Differenzdrucksensor'
         'Motionsensor/Reedsensor_72.Motion' -> 'Motionsensor/Reedsensor'
    """
    base = sensor_id.split('.', 1)[0]
    return base.split('_', 1)[0] if '_' in base else base

def ensure_sensors(sensor_ids: Set[str]) -> None:
    """
    Ensure rows exist in public.sensors to satisfy the FK on measurements.sensor_id.
    Your schema requires sensor_type NOT NULL, so we insert (sensor_id, sensor_type).
    description and unit_default are nullable and left NULL.
    """
    if not sensor_ids:
        return

    records = [(sid, _derive_sensor_type(sid)) for sid in sensor_ids]

    sql = """
        INSERT INTO sensors (sensor_id, sensor_type)
        VALUES %s
        ON CONFLICT (sensor_id) DO NOTHING
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            execute_values(cur, sql, records)
        conn.commit()
        logger.info("Ensured %d sensor ids exist in sensors", len(records))
    finally:
        conn.close()

# ---------- bulk insert measurements ----------

def insert_readings(rows: List[dict]) -> None:
    """
    Bulk insert into measurements.
    Each row must have keys: timestamp, rp_id, sensor_id, unit, value, value_name
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
