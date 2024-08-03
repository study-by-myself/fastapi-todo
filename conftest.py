import pytest
from sqlmodel import SQLModel

from db import init_db_engine, init_async_session


@pytest.fixture
async def db_session():
    engine = init_db_engine()
    async with engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()

        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

        session_class = init_async_session(conn)
        async with session_class() as session:
            yield session
        await conn.rollback()

        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()
