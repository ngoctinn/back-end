from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Load environment variables from project .env (if present)
try:
    from dotenv import load_dotenv

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_path = os.path.join(project_root, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
except Exception:
    # python-dotenv is optional at this stage; proceed if missing
    pass

# If DATABASE_URL exists in env, prefer it over alembic.ini
db_url = os.environ.get("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

# Import project metadata (SQLModel / SQLAlchemy metadata)
# Try to import a common metadata object from src.core.db or fall back to
# importing models so that their Table objects register with SQLModel.metadata.
target_metadata = None
try:
    # Expected location: src/core/db.py with 'metadata' attribute
    from src.core.db import metadata as metadata_from_db

    target_metadata = metadata_from_db
except Exception:
    # If that fails, try to import modules to register models' metadata
    try:
        # Import common modules so models are registered. Adjust as needed.
        import importlib

        # Importing module files causes SQLModel models to register with metadata
        modules_to_import = [
            "src.modules.auth.models",
            "src.modules.customers.models",
            "src.modules.services.models",
            "src.modules.appointments.models",
            "src.modules.staff.models",
        ]
        for m in modules_to_import:
            try:
                importlib.import_module(m)
            except Exception:
                # ignore missing modules during initial skeleton phase
                pass

        # Try to import SQLModel metadata directly
        from sqlmodel import SQLModel

        target_metadata = SQLModel.metadata
    except Exception:
        target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
