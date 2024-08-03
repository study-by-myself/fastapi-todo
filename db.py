from typing import Annotated

from fastapi import Depends, Request, HTTPException
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlmodel import select

from models import User


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


UseDbSession = Annotated[AsyncSession, Depends(use_session)]


async def use_user(request: Request, db_session: UseDbSession) -> User:
    username = request.cookies.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid user")

    stmt = select(User).where(User.username == username)
    result = await db_session.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user 2")
    return user


async def use_user_optional(request: Request, db_session: UseDbSession) -> User | None:
    username = request.cookies.get("username")
    if not username:
        return None
    stmt = select(User).where(User.username == username)
    result = await db_session.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user


UseUser = Annotated[User, Depends(use_user)]
UseUserOptional = Annotated[User | None, Depends(use_user_optional)]
