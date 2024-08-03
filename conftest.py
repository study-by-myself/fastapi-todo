from db import init_db_engine, init_async_session


async def db_session():
    engine = init_db_engine()
    async with engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()

        session_class = init_async_session(conn)
        async with session_class() as session:
            yield session
        await conn.rollback()

    await engine.dispose()
