from datetime import datetime

from fastapi import APIRouter, HTTPException
from sqlmodel import select, null

from db import UseDbSession, UseUser
from models import Todo, Category
from pydantic import BaseModel, Field

router = APIRouter(prefix="/todo")


class CreateTodoPayload(BaseModel):
    category_id: int
    title: str
    description: str
    due_date: datetime | None = Field(default=None)


@router.post("/")
async def create_todo(
    payload: CreateTodoPayload, db_session: UseDbSession, user: UseUser
):
    statement = select(Category).where(
        Category.id == payload.category_id,
        Category.user_id == user.id,
        Category.deleted.is_(null()),
    )
    result = await db_session.execute(statement)
    category = result.scalar_one()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    todo = Todo(**payload.model_dump())
    db_session.add(todo)
    db_session.commit()
    db_session.refresh(todo)
    return todo
