from fastapi import Depends, HTTPException, APIRouter
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from db import use_session
from models import User, Category

UseDbSession = Annotated[AsyncSession, Depends(use_session)]
router = APIRouter(prefix="/auth")


@router.post("/signup/")
async def signup_user(payload: User, db_session: UseDbSession) -> User:
    user = User(**payload.model_dump())
    db_session.add(user)
    await db_session.commit()

    category = Category(name=f"{user.name} Default", user_id=user.id)
    db_session.add(category)
    await db_session.commit()

    await db_session.refresh(user)

    return user


@router.post("/signin/")
async def login_user(username: str, password: str, db_session: UseDbSession) -> User:
    stmt = select(User).where(User.username == username)
    result = await db_session.execute(stmt)
    user = result.scalar_one()
    if user and user.password == password:
        return user
    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/user/")
async def get_user(username: str, db_session: UseDbSession) -> User:
    stmt = select(User).where(User.username == username)
    result = await db_session.execute(stmt)
    user = result.scalar_one()
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")