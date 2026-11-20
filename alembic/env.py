import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from payment_gateway.database.db_models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Importing PaymentRecord ensures it is registered with Base.metadata.
target_metadata = Base.metadata

# Use DATABASE_URL when supplied; otherwise use the local SQLite database.
database_url = os.getenv(
    "DATABASE_URL",
    "sqlite:///payments.db",
)

# Escape percent signs because ConfigParser treats them as interpolation.
config.set_main_option(
    "sqlalchemy.url",
    database_url.replace("%", "%%"),
)


def run_migrations_offline() -> None:
    """Run migrations without creating a database connection."""

    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using a live database connection."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
