
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Alembic Environment Configuration

Responsibilities:
- Load project settings
- Use the same DATABASE_URL as the application
- Import all SQLAlchemy models
- Provide Base.metadata to Alembic
- Support offline and online migrations
- Support Alembic autogenerate
=========================================================
"""

from logging.config import fileConfig

import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# =========================================================
# PROJECT ROOT
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# =========================================================
# PROJECT DATABASE
# =========================================================

from backend.database.database import Base

# IMPORTANT:
# Import models so every ORM table is registered in
# Base.metadata before Alembic autogenerate runs.
from backend.database import models  # noqa: F401

# =========================================================
# PROJECT SETTINGS
# =========================================================

from config.settings import settings

# =========================================================
# ALEMBIC CONFIGURATION
# =========================================================

config = context.config

# =========================================================
# LOGGING
# =========================================================

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# =========================================================
# TARGET METADATA
# =========================================================

target_metadata = Base.metadata

# =========================================================
# DATABASE URL
# =========================================================

DATABASE_URL = getattr(
    settings,
    "DATABASE_URL",
    None,
)

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured. "
        "Please define DATABASE_URL in your .env file."
    )

# =========================================================
# IMPORTANT
# =========================================================
#
# Override sqlalchemy.url from alembic.ini.
#
# This guarantees that Alembic and FastAPI use the
# same database configured through settings.py/.env.
#
# =========================================================

config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL.replace("%", "%%"),
)

# =========================================================
# OFFLINE MIGRATIONS
# =========================================================


def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.

    Alembic generates SQL statements without creating
    a live database connection.
    """

    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# =========================================================
# ONLINE MIGRATIONS
# =========================================================


def run_migrations_online() -> None:
    """
    Run migrations in online mode.

    Creates a temporary Alembic connection using the
    database configuration loaded above.
    """

    configuration = config.get_section(
        config.config_ini_section
    )

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# =========================================================
# EXECUTION
# =========================================================

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()

