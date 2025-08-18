import csv
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger("csv_parser")
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def parse_csv(rp_id: int, filepath: str):
    """
    Parse a sensor CSV file and return rows ready for the 'measurements' table.

    Returns a list of dicts with keys:
      rp_id:int, sensor_id:str (sensor.measurement), timestamp:aware-datetime (UTC),
      unit:str, value:float, value_name:Optional[str]
    """
    if not os.path.isfile(filepath):
        logger.error("CSV file not found: %s", filepath)
        return []

    rows = []
    with open(filepath, newline="") as csvfile:
        reader = csv.reader(csvfile)
        try:
            header1 = next(reader)  # sensor ids
            header2 = next(reader)  # measurement names
            header3 = next(reader)  # units
        except StopIteration:
            logger.error("CSV %s has insufficient header rows", filepath)
            return []

        # Build descriptors for measurement columns (index > 0)
        cols = []
        for i in range(len(header1)):
            if i == 0:
                cols.append((None, None, None))
            else:
                cols.append((header1[i], header2[i], header3[i]))

        for row in reader:
            if not row or len(row) < 2:
                continue
            # CSV timestamp assumed ISO without TZ; treat as UTC
            try:
                ts = datetime.fromisoformat(row[0]).replace(tzinfo=timezone.utc)
            except Exception as e:
                logger.error("Invalid timestamp %s in %s: %s", row[0], filepath, e)
                continue

            for i in range(1, len(row)):
                sensor, meas, unit = cols[i]
                if not sensor:
                    continue
                raw = row[i].strip()
                if raw == "":
                    continue

                # Combine sensor + measurement
                sensor_key = f"{sensor}.{meas}"

                # Convert to numeric and carry label for booleans
                value_name = None
                try:
                    if unit.lower() == "bool":
                        v_bool = raw.lower() in ("true", "1", "yes")
                        value = 1.0 if v_bool else 0.0
                        value_name = "True" if v_bool else "False"
                    else:
                        value = float(raw)
                except ValueError:
                    logger.error("Non-numeric value %s for %s in %s", raw, sensor_key, filepath)
                    continue

                rows.append({
                    "rp_id": int(rp_id),
                    "sensor_id": sensor_key,
                    "timestamp": ts,
                    "unit": unit,
                    "value": value,
                    "value_name": value_name
                })

    logger.info("Parsed %d readings from %s", len(rows), filepath)
    return rows


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python -m software.csv_parser <rp_id> <csv_file_path>")
        sys.exit(1)

    rp_id = int(sys.argv[1])
    path = sys.argv[2]
    parsed = parse_csv(rp_id, path)
    print(f"Parsed {len(parsed)} readings from {path}")
    for entry in parsed[:5]:
        print(entry)
