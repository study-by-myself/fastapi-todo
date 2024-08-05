from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException
from sqlalchemy import update
from sqlmodel import select, null

from db import UseDbSession, UseUser
from models import Todo, Category, TodoStatus
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


class TodoParams(BaseModel):
    category_id: int
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1)
    ordering: Literal["id", "-id", "due_date", "-due_date"] = Field(default="id")
    status: Optional[TodoStatus] = None


@router.get("/")
async def get_todos(payload: TodoParams, db_session: UseDbSession, user: UseUser):
    statement = (
        (
            select(Todo)
            .where(
                ~Todo.is_deleted,
            )
            .join(Category)
            .where(
                Category.user_id == user.id,
                ~Category.is_deleted,
            )
        )
        .offset((payload.page - 1) * payload.limit)
        .limit(payload.limit)
    )

    query_ordering = payload.ordering
    match query_ordering:
        case "due_date" | "-due_date":
            ordering = Todo.due_date
        case _:
            ordering = Todo.id

    if query_ordering.startswith("-"):
        statement = statement.order_by(ordering.desc())
    else:
        statement = statement.order_by(ordering.asc())

    if payload.category_id:
        statement = statement.where(Todo.category_id == payload.category_id)

    if payload.status:
        statement = statement.where(Todo.status == payload.status)

    result = await db_session.execute(statement)
    todos = result.scalars().all()
    return todos


@router.get("/{todo_id}")
async def get_todo(todo_id: int, db_session: UseDbSession, user: UseUser):
    statement = select(Todo).where(
        Todo.id == todo_id,
        Todo.user_id == user.id,
        Todo.deleted.is_(null()),
    )
    result = await db_session.execute(statement)
    todo = result.scalar_one()
    return todo


@router.patch("/{todo_id}")
async def patch_todo(
    todo_id: int, db_session: UseDbSession, user: UseUser, payload: dict
):
    statement = (
        update(Todo)
        .where(
            Todo.id == todo_id,
            Todo.user_id == user.id,
            Todo.deleted.is_(null()),
        )
        .values(**payload)
    )
    await db_session.execute(statement)

    statement = select(Todo).where(Todo.id == todo_id)
    result = await db_session.execute(statement)
    todo = result.scalar_one()
    return todo


@router.delete("/{todo_id}")
async def delete_todo(todo_id: int, db_session: UseDbSession, user: UseUser):
    statement = select(Todo).where(
        Todo.id == todo_id,
        Todo.user_id == user.id,
        Todo.deleted.is_(null()),
    )
    result = await db_session.execute(statement)
    todo = result.scalar_one()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo.deleted = datetime.now()
    db_session.add(todo)
    db_session.commit()
    return todo
