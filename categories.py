from datetime import datetime

from fastapi import APIRouter
from sqlalchemy import null, update
from sqlmodel import select

from db import UseDbSession, UseUser
from models import Category

router = APIRouter(prefix="/category")


@router.post("/")
async def create_category(
    category_name, db_session: UseDbSession, user: UseUser
) -> Category:
    category = Category(name=category_name, user_id=user.id)
    db_session.add(category)
    await db_session.commit()
    return category


@router.get("/")
async def get_categories(db_session: UseDbSession, user: UseUser) -> list[Category]:
    statement = select(Category).where(
        Category.user_id == user.id,
        Category.deleted.is_(null()),
    )
    result = await db_session.execute(statement)
    categories = result.scalars().all()
    return categories


@router.get("/{category_id}")
async def get_category(
    category_id, db_session: UseDbSession, user: UseUser
) -> Category:
    statement = select(Category).where(
        Category.id == category_id,
        Category.user_id == user.id,
        Category.deleted.is_(null()),
    )
    result = await db_session.execute(statement)
    category = result.scalar_one()
    return category


@router.patch("/")
async def patch_category(
    category_id, category_name, db_session: UseDbSession, user: UseUser
) -> Category:
    statement = (
        update(Category)
        .where(
            Category.id == category_id,
            Category.user_id == user.id,
            Category.deleted.is_(null()),
        )
        .values(name=category_name)
    )
    await db_session.execute(statement)

    statement = select(Category).where(Category.id == category_id)
    result = await db_session.execute(statement)
    category = result.scalar_one()
    return category


@router.delete("/")
async def delete_category(
    category_id, db_session: UseDbSession, user: UseUser
) -> Category:
    statement = select(Category).where(
        Category.id == category_id,
        Category.user_id == user.id,
        Category.deleted.is_(null()),
    )
    result = await db_session.execute(statement)
    category = result.scalar_one()
    category.deleted = datetime.now()
    await db_session.commit()
    return category
