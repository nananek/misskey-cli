from alembic import context

from nekofedi.db import Base, get_engine

target_metadata = Base.metadata


def run_migrations():
    connectable = get_engine()
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations()
