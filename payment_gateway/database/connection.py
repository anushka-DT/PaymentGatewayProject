import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_database(database_url=None, *, engine_options=None):
    """Create the database engine and session factory."""

    if database_url is None:
        database_url = os.getenv(
            "DATABASE_URL",
            "sqlite:///payments.db",
        )

    options = {
        "echo": False,
        "pool_pre_ping": True,
    }

    if engine_options:
        options.update(engine_options)

    engine = create_engine(database_url, **options)

    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    return engine, session_factory
