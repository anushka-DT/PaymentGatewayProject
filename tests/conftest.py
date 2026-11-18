import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from payment_gateway.database.db_models import Base
from payment_gateway.database.repository import PaymentRepository


@pytest.fixture
def session_factory():
    """Create an in-memory SQLite database for testing."""

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    test_session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    yield test_session_factory

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def payment_repository(session_factory):
    """Provide a payment repository for tests."""

    return PaymentRepository(session_factory)
