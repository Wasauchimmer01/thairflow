-- Which database am I on?
SELECT current_database();

-- Do the tables exist?
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('sensor_readings', 'sensor_offsets');

-- Peek at the columns
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'sensor_readings'
ORDER BY ordinal_position;

SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'sensor_offsets'
ORDER BY ordinal_position;

-- which DB am I in?
SELECT current_database();

-- list our two tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema='public'
  AND table_name IN ('sensor_readings','sensor_offsets');

-- describe sensor_offsets
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name='sensor_offsets'
ORDER BY ordinal_position;

-- show search_path (just in case)
SHOW search_path;
