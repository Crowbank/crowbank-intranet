"""Connectivity test for SQL Server using plain pyodbc.

Run with:
    python -m migration.test_connection_raw

It intentionally avoids SQLAlchemy so that only the ODBC layer is involved.
"""

from __future__ import annotations

import sys

import pyodbc

# ---------------------------------------------------------------------------
# Adjust these values if moving to env vars/yaml later.
# ---------------------------------------------------------------------------
DRIVER = "ODBC Driver 18 for SQL Server"
SERVER = "192.168.0.200\\SQLEXPRESS"  # host\\instance or host,port
DATABASE = "crowbank"
USERNAME = "PA"
PASSWORD = "petadmin"
OPTIONS  = "TrustServerCertificate=yes;Encrypt=yes"  # tweak as required

CONN_STR = (
    f"DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};"
    f"UID={USERNAME};PWD={PASSWORD};{OPTIONS}"
)


def main() -> None:  # pragma: no cover
    try:
        conn = pyodbc.connect(CONN_STR, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        value = cursor.fetchone()[0]
        print("✅ pyodbc connection succeeded, SELECT 1 ->", value)
        conn.close()
    except Exception as exc:
        print("❌ pyodbc connection failed:", exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 