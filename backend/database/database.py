
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform
Database Configuration
Author : Feroz Ali
=========================================================

Responsibilities
-----------------
1. Create SQLAlchemy database engine.
2. Create database sessions.
3. Provide declarative Base for all models.
4. Provide FastAPI database dependency.
5. Initialize all project database tables.
6. Safely handle database transactions.
7. Support PostgreSQL and other SQLAlchemy-compatible DBs.
=========================================================
"""

import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import settings


# =========================================================
# LOGGER
# =========================================================

logger = logging.getLogger("Database")


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
# SQLALCHEMY BASE
# =========================================================
#
# IMPORTANT:
# Base must be created before importing models because
# every model imports Base from this module.
#
# This prevents circular-import problems.
# =========================================================

Base = declarative_base()


# =========================================================
# ENGINE OPTIONS
# =========================================================

engine_kwargs = {
    "echo": bool(
        getattr(
            settings,
            "DEBUG",
            False,
        )
    ),
    "pool_pre_ping": True,
}


# =========================================================
# CONNECTION POOL
# =========================================================
#
# PostgreSQL supports connection pooling.
#
# SQLite does not use the same pooling configuration.
# Therefore pool_size/max_overflow are only enabled for
# non-SQLite databases.
# =========================================================

if not DATABASE_URL.startswith(
    "sqlite"
):

    engine_kwargs.update(
        {
            "pool_size": 10,
            "max_overflow": 20,
        }
    )


# =========================================================
# ENGINE
# =========================================================

engine = create_engine(
    DATABASE_URL,
    **engine_kwargs,
)


# =========================================================
# SESSION FACTORY
# =========================================================

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# =========================================================
# DATABASE DEPENDENCY
# =========================================================

def get_db():
    """
    FastAPI database dependency.

    Creates one SQLAlchemy session for the request
    and guarantees that the session is closed.

    Any unhandled exception causes a rollback.
    """

    db = SessionLocal()

    try:

        yield db

    except Exception:

        try:
            db.rollback()

        except Exception:

            logger.exception(
                "Database rollback failed."
            )

        raise

    finally:

        db.close()


# =========================================================
# DATABASE CONNECTION TEST
# =========================================================

def check_database_connection() -> bool:
    """
    Test whether the database is reachable.

    Returns
    -------
    bool
        True when the database is reachable.
        False otherwise.
    """

    try:

        with engine.connect() as connection:

            connection.execute(
                text("SELECT 1")
            )

        logger.info(
            "Database connection successful."
        )

        return True

    except Exception:

        logger.exception(
            "Database connection failed."
        )

        return False


# =========================================================
# INITIALIZE ALL DATABASE TABLES
# =========================================================

def init_db() -> None:
    """
    Create all SQLAlchemy tables registered in Base.metadata.

    IMPORTANT:
    Models are imported inside this function intentionally.

    Do NOT import models at module level here because
    models.py imports Base from database.py.

    This avoids:

        database.py
            -> models.py
                -> database.py

    circular import problems.
    """

    try:

        # -------------------------------------------------
        # Import every model module.
        #
        # Your project currently keeps the database models
        # in:
        #
        # backend/database/models.py
        # -------------------------------------------------

        from backend.database import models  # noqa: F401

        # -------------------------------------------------
        # Create all registered tables.
        #
        # Existing tables are NOT dropped.
        #
        # create_all() only creates tables that do not
        # already exist.
        # -------------------------------------------------

        Base.metadata.create_all(
            bind=engine
        )

        logger.info(
            "Database tables initialized successfully."
        )

        logger.info(
            "Registered tables: %s",
            list(
                Base.metadata.tables.keys()
            ),
        )

    except Exception:

        logger.exception(
            "Database table initialization failed."
        )

        raise


# =========================================================
# DROP ALL TABLES
# =========================================================
#
# WARNING:
# This is intentionally NOT called automatically.
#
# Never call this from application startup.
# =========================================================

def drop_all_tables() -> None:
    """
    Explicitly drop all registered tables.

    WARNING:
    This permanently removes database tables and their data.

    This function is provided only for controlled development
    or testing scenarios.
    """

    logger.warning(
        "Dropping ALL registered database tables."
    )

    Base.metadata.drop_all(
        bind=engine
    )

    logger.warning(
        "All registered database tables were dropped."
    )


# =========================================================
# DATABASE STATUS
# =========================================================

def database_status() -> dict:
    """
    Return database connection and table information.
    """

    connected = check_database_connection()

    return {
        "database": "connected"
        if connected
        else "disconnected",

        "database_url_configured": bool(
            DATABASE_URL
        ),

        "tables": list(
            Base.metadata.tables.keys()
        ),
    }


# =========================================================
# MODULE TEST
# =========================================================

if __name__ == "__main__":

    print(
        "\nEnterprise AI Database Status:\n"
    )

    print(
        database_status()
    )

    if check_database_connection():

        print(
            "\nInitializing database tables...\n"
        )

        init_db()

        print(
            "\nDatabase initialization completed."
        )

    else:

        print(
            "\nDatabase connection failed."
        )

