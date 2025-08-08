import psycopg2
from psycopg2.extras import execute_values
import logging

logger = logging.getLogger("db")

# 2.1 Establish a connection (you may want a pool in real use)
def get_conn():
    cfg = load_db_config()  # implement this to read your db_config.json or env
    return psycopg2.connect(
        host=cfg["host"], port=cfg["port"],
        dbname=cfg["database"],
        user=cfg["user"], password=cfg["password"]
    )

# 2.2 Fetch the last_ts for one sensor
def get_last_ts(rpi_id: str, sensor_id: str):
    sql = """
      SELECT last_ts
        FROM sensor_offsets
       WHERE rpi_id = %s
         AND sensor_id = %s
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (rpi_id, sensor_id))
        row = cur.fetchone()
        if row:
            return row[0]
        # if no entry yet, return epoch (or choose another default)
        return datetime.fromtimestamp(0)

# 2.3 Bulk upsert new offsets
def upsert_last_ts(offsets: dict):
    """
    offsets: dict[(rpi_id, sensor_id) -> last_ts]
    """
    records = [
        (rpi_id, sensor_id, ts)
        for (rpi_id, sensor_id), ts in offsets.items()
    ]
    sql = """
    INSERT INTO sensor_offsets(rpi_id, sensor_id, last_ts)
         VALUES %s
    ON CONFLICT (rpi_id, sensor_id)
      DO UPDATE SET last_ts = EXCLUDED.last_ts
    """
    with get_conn() as conn, conn.cursor() as cur:
        execute_values(cur, sql, records)
        conn.commit()
        logger.info("Upserted %d offsets", len(records))

def insert_readings(rows: list[dict]):
    """
    Bulk-insert parsed rows into sensor_readings.
    Expects each dict to have keys:
    rpi_id, sensor_id, ts, measurement, unit, value_num, value_bool
    """
    sql = """
    INSERT INTO sensor_readings
      (rpi_id, sensor_id, ts, value, value_bool, unit)
    VALUES %s
    ON CONFLICT DO NOTHING
    """
    # build a list of tuples
    records = [
        (
            row["rpi_id"],
            row["sensor_id"],
            row["ts"],
            row["value_num"],
            row["value_bool"],
            row["unit"],
        )
        for row in rows
    ]
    conn = get_conn()
    with conn, conn.cursor() as cur:
        execute_values(cur, sql, records)
