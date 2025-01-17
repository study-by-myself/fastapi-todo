from sqlmodel import select

from categories import (
    create_category,
    get_category,
    patch_category,
    delete_category,
    get_categories,
)
from models import User, Todo
from todo import create_todo, CreateTodoPayload, get_todos, TodoParams
from users import signup_user


async def test_create_user(db_session):
    user = User(name="John Doe", username="johndoe", password="password", tmi="tmi")
    db_session.add(user)
    await db_session.commit()

    stmt = select(User).where(User.username == "johndoe")
    result = await db_session.execute(stmt)
    user = result.scalars().first()
    assert user.username == "johndoe"


async def test_signup_user(db_session):
    user = await signup_user(
        User(name="John Doe", username="johndoe", password="password", tmi="tmi"),
        db_session,
    )
    assert user.username == "johndoe"

    assert user.categories[0].name == "John Doe Default"


async def test_create_todo(db_session, user, category):
    result_todo = await create_todo(
        CreateTodoPayload(
            title="Test Todo", description="Test Description", category_id=category.id
        ),
        db_session,
        user,
    )

    assert result_todo.title == "Test Todo"
    assert result_todo.description == "Test Description"
    assert result_todo.status == "todo"
    assert result_todo.category_id == category.id


async def test_get_todo_list(db_session, user, category, todo):
    todo_params = TodoParams.model_validate({"category_id": category.id})
    todo2 = Todo(
        title="Test Todo 2", description="Test Description 2", category_id=category.id
    )
    db_session.add(todo2)
    await db_session.commit()

    todos = await get_todos(
        todo_params,
        db_session,
        user,
    )

    assert len(todos) == 2
    assert todos[0].title == "Test Todo"
    assert todos[0].description == "Test Description"
    assert todos[0].status == "todo"
    assert todos[0].category_id == category.id


async def test_create_category(db_session, user):
    category = await create_category(
        "Test Category",
        db_session,
        user,
    )

    assert category.name == "Test Category"
    assert category.user_id == user.id


async def test_get_categories(db_session, user, category):
    categories = await get_categories(
        db_session,
        user,
    )

    assert len(categories) == 1
    assert categories[0].is_deleted is False
    assert categories[0].name == "Test Category"
    assert categories[0].user_id == user.id


async def test_get_category(db_session, user, category):
    result_category = await get_category(
        category.id,
        db_session,
        user,
    )

    assert result_category.name == category.name
    assert result_category.user_id == user.id


async def test_patch_category(db_session, user, category):
    payload = {
        "category_id": category.id,
        "name": "New Category Name",
    }
    # category_name = category.name
    result_category = await patch_category(
        payload["category_id"],
        payload["name"],
        db_session,
        user,
    )

    assert result_category.name == payload["name"]
    assert result_category.user_id == user.id


async def test_delete_category(db_session, user, category):
    result_category = await delete_category(
        category.id,
        db_session,
        user,
    )

    assert result_category.deleted is not None
    assert result_category.user_id == user.id
