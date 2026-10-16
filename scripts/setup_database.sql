-- Local development database setup. Run with:
-- psql -d postgres -f scripts/setup_database.sql

-- macOS Homebrew installations may not have a `postgres` user account yet,
-- while the Windows installer creates one during setup. Create it only when
-- it is absent.
SELECT 'CREATE ROLE postgres WITH LOGIN PASSWORD ''postgres'''
WHERE NOT EXISTS (
  SELECT 1 FROM pg_roles WHERE rolname = 'postgres'
)
\gexec

-- Leave an existing database in place so the script can be rerun safely
-- without deleting data.
SELECT 'CREATE DATABASE library_management OWNER postgres'
WHERE NOT EXISTS (
  SELECT 1 FROM pg_database WHERE datname = 'library_management'
)
\gexec
