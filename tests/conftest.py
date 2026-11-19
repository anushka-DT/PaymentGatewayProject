import pytest
from sqlalchemy.pool import StaticPool

from payment_gateway.database.connection import create_database
from payment_gateway.database.db_models import Base
from payment_gateway.database.repository import PaymentRepository


@pytest.fixture
def session_factory():
    """Create an isolated in-memory SQLite database for testing."""

    engine, test_session_factory = create_database(
        "sqlite://",
        engine_options={
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        },
    )

    Base.metadata.create_all(engine)

    yield test_session_factory

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def payment_repository(session_factory):
    """Provide a payment repository for tests."""

    return PaymentRepository(session_factory)
