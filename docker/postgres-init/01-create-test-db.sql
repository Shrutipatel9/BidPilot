-- Runs once, on first container start, against the default POSTGRES_DB (bidpilot).
CREATE EXTENSION IF NOT EXISTS vector;

CREATE DATABASE bidpilot_test;

\c bidpilot_test
CREATE EXTENSION IF NOT EXISTS vector;
