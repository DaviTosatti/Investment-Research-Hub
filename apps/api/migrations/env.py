from alembic import context
from hub_api.config import get_settings
from hub_api.models import Base
from sqlalchemy import create_engine, pool

target_metadata = Base.metadata
database_url = context.config.get_main_option("sqlalchemy.url") or get_settings().database_url

if context.is_offline_mode():
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    connectable = create_engine(database_url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
