import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from payment_gateway.database.db_models import Base


def create_database(database_url=None):
    """Create the database engine and session factory."""

    if database_url is None:
        database_url = os.getenv(
            "DATABASE_URL",
            "sqlite:///payments.db",
        )

    engine = create_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
    )

    Base.metadata.create_all(engine)

    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    return engine, session_factory
