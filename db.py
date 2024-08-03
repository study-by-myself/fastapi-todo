from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


def init_db_engine(uri="sqlite+aiosqlite:///"):
    return create_async_engine(uri, echo=True, poolclass=NullPool)


def init_async_session(db_engine):
    return async_sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=db_engine,
        class_=AsyncSession,
    )


engine = init_db_engine()
create_async_session = init_async_session(engine)


async def use_session():
    async with create_async_session() as session:
        yield session
