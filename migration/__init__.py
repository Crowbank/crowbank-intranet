"""Data-migration helpers for Crowbank Intranet

This package contains reusable utilities that move data between the
legacy SQL-Server system (PetAdmin) and the new PostgreSQL schema.

Structure
---------
config.py     — resolves connection strings from YAML / env vars
lookup.py     — run-time lookup tables mapping legacy PKs → new PKs
importer.py   — generic importer that streams rows from SQL-Server
cli.py        — small CLI entry-point so you can run `python -m migration`

Nothing in this package performs DDL.  It's safe to run after
`alembic upgrade head` and can be re-run at any time on a fresh
PostgreSQL database.
""" 