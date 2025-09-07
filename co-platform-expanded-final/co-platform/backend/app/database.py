"""Database setup for the HR/Support system.

This module configures a SQLAlchemy engine and session maker based on the
``DATABASE_URL`` environment variable. If not provided, it defaults to a
PostgreSQL instance running on a container service named ``db`` with
username/password ``postgres/password``. Declarative base is exposed so
models across the application can inherit from it.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Database connection string; for local development the default will
# connect to the ``db`` service defined in docker-compose.yml. Users can
# override this via the environment variable ``DATABASE_URL``.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@db:5432/postgres",
)

# Create the SQLAlchemy engine; ``pool_pre_ping`` ensures that stale
# connections are checked before use.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Configure session maker; ``autocommit``/``autoflush`` are disabled so
# changes are explicit and controlled via ``session.commit()``.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models.
Base = declarative_base()