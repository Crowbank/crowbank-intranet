from __future__ import annotations

"""Utility that builds SQL-Alchemy connection URLs for both databases."""

import os
import sys
from pathlib import Path

# Add the app module to the Python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.utils.yaml_config import load_config


class Settings:
    """Resolves credentials from YAML configuration."""

    def __init__(self) -> None:
        # Load config using the standard yaml_config loader
        config = load_config()
        nested_config = config['nested']
        
        # PostgreSQL ---------------------------------------------------------
        # Get database configuration
        db = nested_config.get('database', {})
        legacy_db = nested_config.get('legacy_database', {})
        
        # Build PostgreSQL URL if not already in config
        if 'sqlalchemy' in nested_config and 'database_uri' in nested_config['sqlalchemy']:
            self.pg_url = nested_config['sqlalchemy']['database_uri']
        else:
            # Extract required values
            pg_user = db.get('user', '')
            pg_pass = db.get('password', '')
            pg_host = db.get('host', 'localhost')
            pg_port = db.get('port', 5432)
            pg_db = db.get('name', 'crowbank')
            
            # Build the connection URL
            self.pg_url: str = (
                f"postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
            )

        # SQL-Server ---------------------------------------------------------
        # Build SQL Server URL from legacy database config
        if legacy_db:
            driver = legacy_db.get('driver', 'ODBC Driver 18 for SQL Server')
            server = legacy_db.get('server', '192.168.0.200\\SQLEXPRESS')
            database = legacy_db.get('database', 'crowbank')
            username = legacy_db.get('username', 'PA')
            password = legacy_db.get('password', 'petadmin')
            options = legacy_db.get('options', 'TrustServerCertificate=yes;Encrypt=yes')
            
            # Allow override from environment variable
            self.mssql_url: str = os.getenv(
                "LEGACY_DB_URL",
                f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver.replace(' ', '+')}&{options}"
            )
        else:
            # Fallback to environment variable or default
            self.mssql_url: str = os.getenv(
                "LEGACY_DB_URL",
                "mssql+pyodbc://PA:petadmin@192.168.0.200\\SQLEXPRESS/crowbank?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes"
            )

    # ---------------------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover
        return f"Settings(pg_url='{self.pg_url}', mssql_url='{self.mssql_url[:40]}…')"


settings = Settings() 