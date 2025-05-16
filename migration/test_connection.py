"""Quick connectivity test for the legacy SQL Server instance.

Usage:
    python -m migration.test_connection
"""

from __future__ import annotations

import sys

import sqlalchemy as sa

from .config import settings


def main() -> None:
    """Attempt to connect and run a trivial query against the SQL Server."""
    engine = sa.create_engine(settings.mssql_url)

    try:
        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
        print("✅ Successfully connected to SQL Server via:", settings.mssql_url)
    except Exception as exc:  # pragma: no cover
        print("❌ Could not connect to SQL Server.", file=sys.stderr)
        print(exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main() 