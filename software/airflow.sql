SELECT COUNT(*) FROM public.measurements;

SELECT rp_id, sensor_id,
       MIN("timestamp") AS first_ts,
       MAX("timestamp") AS last_ts,
       COUNT(*) AS rows
FROM public.measurements
GROUP BY rp_id, sensor_id
ORDER BY rp_id, sensor_id;

SELECT * FROM public.sensor_offsets ORDER BY rp_id, sensor_id LIMIT 20;