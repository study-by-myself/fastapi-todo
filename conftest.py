import pytest
from sqlmodel import SQLModel

from db import init_db_engine, init_async_session
from models import User, Category


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


@pytest.fixture
async def user(db_session):
    user = User(name="John Doe", username="johndoe", password="password", tmi="tmi")
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def category(db_session, user):
    category = Category(name="Test Category", user_id=user.id)
    db_session.add(category)
    await db_session.commit()
    return category
