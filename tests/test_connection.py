from sqlalchemy import select

from payment_gateway.database.connection import create_database
from payment_gateway.database.db_models import Base, PaymentRecord


def test_create_database():
    """Test database engine and session factory creation."""

    engine, session_factory = create_database("sqlite://")

    try:
        Base.metadata.create_all(engine)

        with session_factory() as session:
            payments = session.scalars(select(PaymentRecord)).all()

        assert payments == []
        assert engine is not None

    finally:
        engine.dispose()


def test_create_database_uses_environment_variable(monkeypatch):
    """Test database URL configuration through environment variable."""

    monkeypatch.setenv("DATABASE_URL", "sqlite://")

    engine, session_factory = create_database()

    try:
        Base.metadata.create_all(engine)

        assert engine is not None

        with session_factory() as session:
            payments = session.scalars(select(PaymentRecord)).all()

        assert payments == []

    finally:
        engine.dispose()
