from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base and all models for metadata discovery
from app.database import Base
from app.config import settings

# CRITICAL: Import all models to ensure metadata discovery
# Without these imports, Alembic won't detect the tables
from app.models.user import User  # noqa: F401
from app.models.deck import Deck  # noqa: F401
from app.models.job import Job  # noqa: F401
from app.models.setting import Setting  # noqa: F401
from app.models.subscription import Subscription  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.notification import Notification  # noqa: F401

target_metadata = Base.metadata

# Get database URL from settings and convert from async to sync
# Alembic requires sync URL: postgresql:// not postgresql+asyncpg://
def get_url():
    """Get database URL and convert from async to sync driver."""
    database_url = settings.DATABASE_URL
    # Convert asyncpg URL to psycopg2 URL for Alembic
    if "postgresql+asyncpg://" in database_url:
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    return database_url


# Override the sqlalchemy.url in config with our computed URL
config.set_main_option("sqlalchemy.url", get_url())


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with SYNC engine."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
