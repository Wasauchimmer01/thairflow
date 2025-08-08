SELECT column_name, is_nullable
FROM information_schema.columns
WHERE table_schema='public' AND table_name='sensors'
ORDER BY ordinal_position;