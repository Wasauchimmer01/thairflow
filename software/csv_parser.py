import csv
import os
from datetime import datetime
import logging

logger = logging.getLogger("csv_parser")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(name)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def parse_csv(rpi_id: str, filepath: str):
    """
    Parse a sensor CSV file into a list of reading dicts.

    Args:
        rpi_id (str): Identifier for the Raspberry Pi source.
        filepath (str): Path to the CSV file.

    Returns:
        List[dict]: Each dict has keys:
            rpi_id, sensor_id, ts, measurement, unit, value_num, value_bool
    """
    if not os.path.isfile(filepath):
        logger.error("CSV file not found: %s", filepath)
        return []

    rows = []
    with open(filepath, newline='') as csvfile:
        reader = csv.reader(csvfile)
        try:
            header1 = next(reader)
            header2 = next(reader)
            header3 = next(reader)
        except StopIteration:
            logger.error("CSV %s has insufficient header rows", filepath)
            return []

        # Build column descriptors for indices > 0
        cols = []  # list of tuples (sensor_id, measurement, unit)
        for i in range(len(header1)):
            if i == 0:
                cols.append((None, None, None))
            else:
                sensor = header1[i]
                meas   = header2[i]
                unit   = header3[i]
                cols.append((sensor, meas, unit))

        # Parse data rows
        for row in reader:
            if not row or len(row) < 2:
                continue
            try:
                ts = datetime.fromisoformat(row[0])
            except Exception as e:
                logger.error("Invalid timestamp %s in %s: %s", row[0], filepath, e)
                continue

            # For each measurement column
            for i in range(1, len(row)):
                sensor_id, measurement, unit = cols[i]
                if not sensor_id:
                    continue
                raw = row[i].strip()
                if raw == "":
                    continue

                value_num = None
                value_bool = None
                if unit.lower() == "bool":
                    value_bool = raw.lower() in ("true", "1", "yes")
                else:
                    try:
                        value_num = float(raw)
                    except ValueError:
                        logger.error("Non-numeric value %s for %s in %s", raw, sensor_id, filepath)
                        continue

                rows.append({
                    "rpi_id": rpi_id,
                    "sensor_id": sensor_id,
                    "ts": ts,
                    "measurement": measurement,
                    "unit": unit,
                    "value_num": value_num,
                    "value_bool": value_bool
                })

    logger.info("Parsed %d readings from %s", len(rows), filepath)
    return rows


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python -m software.csv_parser <rpi_id> <csv_file_path>")
        sys.exit(1)

    rpi_id = sys.argv[1]
    path = sys.argv[2]
    parsed = parse_csv(rpi_id, path)
    print(f"Parsed {len(parsed)} readings from {path}")
    # Print first few rows as sample
    for entry in parsed[:5]:
        print(entry)
