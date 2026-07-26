-- Runs once on first container start (mounted into /docker-entrypoint-initdb.d/).
-- The database/user themselves are already created by the postgres image
-- using POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD env vars; this file
-- is a place for any extensions or extra bootstrapping CareerRadar needs.

CREATE EXTENSION IF NOT EXISTS pg_trgm;
