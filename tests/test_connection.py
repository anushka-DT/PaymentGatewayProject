from payment_gateway.database.connection import create_database
from payment_gateway.database.db_models import PaymentRecord


def test_create_database():
    """Test database engine and session factory creation."""

    engine, session_factory = create_database("sqlite://")

    try:
        with session_factory() as session:
            payments = session.query(PaymentRecord).all()

        assert payments == []
        assert engine is not None

    finally:
        engine.dispose()


def test_create_database_uses_environment_variable(monkeypatch):
    """Test database URL configuration through environment variable."""

    monkeypatch.setenv("DATABASE_URL", "sqlite://")

    engine, session_factory = create_database()

    try:
        assert engine is not None

        with session_factory() as session:
            payments = session.query(PaymentRecord).all()

        assert payments == []

    finally:
        engine.dispose()
