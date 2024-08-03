from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=16)
    username: str = Field(max_length=16)
    password: str
    tmi: str

