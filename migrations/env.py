from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv()

# Ensure app is on the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models.base import Base

target_metadata = Base.metadata

# Alembic Config
config = context.config

# Force sqlalchemy.url to use DB_PASSWORD from environment
_db_password = os.getenv("DB_PASSWORD")
_db_url = f"postgresql://crowbank:{_db_password}@localhost/crowbank"
config.set_main_option("sqlalchemy.url", _db_url)

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
