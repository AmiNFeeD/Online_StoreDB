
\echo '== ProjectShop: setup_all starting =='
\set ON_ERROR_STOP on

\c postgres

\echo '== Terminating existing connections =='
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'online_store_db';

\echo '== Recreating database =='
DROP DATABASE IF EXISTS online_store_db;
CREATE DATABASE online_store_db;

\echo '== Ensuring application role exists =='
SELECT 'CREATE ROLE projectshop_app LOGIN PASSWORD ''projectshop123'''
WHERE NOT EXISTS (
    SELECT 1 FROM pg_roles WHERE rolname = 'projectshop_app'
)\gexec

GRANT ALL PRIVILEGES ON DATABASE online_store_db TO projectshop_app;

\c online_store_db

\echo '== Resetting schema =='
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;

GRANT ALL ON SCHEMA public TO projectshop_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO projectshop_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON SEQUENCES TO projectshop_app;

\echo '== 1) schema.sql =='
\i db/schema.sql

\echo '== 2) seed.sql =='
\i db/seed.sql

\echo '== 3) views.sql =='
\i db/views.sql

\echo '== 4) indexes.sql =='
\i db/indexes.sql

\echo '== Setup complete ✅ =='
