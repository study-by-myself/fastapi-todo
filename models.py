import abc
from datetime import datetime
from enum import Enum

from sqlalchemy.ext.hybrid import hybrid_property
from sqlmodel import SQLModel as _SQLModel, Field, func, DateTime, Relationship, null
from sqlmodel._compat import SQLModelConfig


class SQLModel(_SQLModel, abc.ABC):
    __abstract__ = True

    id: int = Field(default=None, primary_key=True)
    created: datetime = Field(
        sa_type=DateTime,
        sa_column_kwargs={"server_default": func.now()},
    )
    updated: datetime = Field(
        sa_type=DateTime,
        sa_column_kwargs={"server_default": func.now(), "server_onupdate": func.now()},
    )
    deleted: datetime = Field(nullable=True)

    model_config = SQLModelConfig(ignored_types=(hybrid_property,))


class User(SQLModel, table=True):
    name: str = Field(max_length=16)
    username: str = Field(max_length=16, unique=True)
    password: str
    tmi: str

    categories: list["Category"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Category(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=16)

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(
        back_populates="categories", sa_relationship_kwargs={"lazy": "selectin"}
    )

    todos: list["Todo"] = Relationship(
        back_populates="category", sa_relationship_kwargs={"lazy": "selectin"}
    )

    @hybrid_property
    def is_deleted(self) -> bool:
        return self.deleted is not None

    @is_deleted.expression
    def is_deleted(cls):
        return ~cls.deleted.is_(null())


class TodoStatus(str, Enum):
    TODO = "todo"
    DONE = "done"


class Todo(SQLModel, table=True):
    title: str
    description: str
    status: TodoStatus = Field(default=TodoStatus.TODO)
    due_date: datetime = Field(nullable=True, default=None)

    category_id: int = Field(foreign_key="category.id")
    category: Category = Relationship(
        back_populates="todos", sa_relationship_kwargs={"lazy": "selectin"}
    )

    model_config = SQLModelConfig(arbitrary_types_allowed=True)

    @hybrid_property
    def is_deleted(self) -> bool:
        return self.deleted is not None

    @is_deleted.expression
    def is_deleted(cls):
        return ~cls.deleted.is_(null())
