from __future__ import annotations

"""Utility that builds SQL-Alchemy connection URLs for both databases."""

import os
from pathlib import Path
import yaml


class Settings:
    """Resolves credentials from YAML files and environment variables."""

    def __init__(self) -> None:
        root = Path(__file__).resolve().parents[1]  # repo root

        secret_yaml = Path(root, "config/yaml/secret.yaml")
        dev_yaml = Path(root, "config/yaml/dev.yaml")

        secret = yaml.safe_load(secret_yaml.read_text()) if secret_yaml.exists() else {}
        dev = yaml.safe_load(dev_yaml.read_text()) if dev_yaml.exists() else {}

        # PostgreSQL ---------------------------------------------------------
        pg_user = secret["database"]["user"]
        pg_pass = secret["database"]["password"]
        pg_host = dev["database"]["host"]
        pg_port = dev["database"]["port"]
        pg_db   = dev["database"]["name"]

        self.pg_url: str = (
            f"postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
        )

        # SQL-Server ---------------------------------------------------------
        # Provide via env var or fall back to sane default (dev only!).
        self.mssql_url: str = os.getenv(
            "LEGACY_MSSQL_URL",
            "mssql+pyodbc://sa:<password>@192.168.0.150/PetAdmin?driver=ODBC+Driver+18+for+SQL+Server",
        )

    # ---------------------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover
        return f"Settings(pg_url='{self.pg_url}', mssql_url='{self.mssql_url[:40]}…')"


settings = Settings() 