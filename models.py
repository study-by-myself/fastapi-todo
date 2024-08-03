import abc
from datetime import datetime

from sqlmodel import SQLModel as _SQLModel, Field, func, DateTime, Column


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


class User(SQLModel, table=True):
    name: str = Field(max_length=16)
    username: str = Field(max_length=16, unique=True)
    password: str
    tmi: str


class Category(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=16)
