-- 1) duplicates? (should return 0 rows)
SELECT rp_id, sensor_id, "timestamp", COUNT(*) AS c
FROM public.measurements
GROUP BY rp_id, sensor_id, "timestamp"
HAVING COUNT(*) > 1
LIMIT 20;

-- 2) max ts per (rp_id, sensor_id) vs offsets (should be equal for all)
WITH m AS (
  SELECT rp_id, sensor_id, MAX("timestamp") AS max_ts
  FROM public.measurements
  GROUP BY rp_id, sensor_id
)
SELECT m.rp_id, m.sensor_id, m.max_ts, o.last_ts, (m.max_ts = o.last_ts) AS in_sync
FROM m
JOIN public.sensor_offsets o USING (rp_id, sensor_id)
ORDER BY m.rp_id, m.sensor_id
LIMIT 50;

-- 3) row counts by sensor (spot check data distribution)
SELECT rp_id, sensor_id, COUNT(*) AS rows,
       MIN("timestamp") AS first_ts, MAX("timestamp") AS last_ts
FROM public.measurements
GROUP BY rp_id, sensor_id
ORDER BY rp_id, sensor_id
LIMIT 50;

-- 4) how many sensors are registered
SELECT COUNT(*) FROM public.sensors;
