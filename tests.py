from sqlmodel import select

from models import User, Category
from todo import create_todo, CreateTodoPayload
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


async def test_create_todo(db_session):
    user = User(name="John Doe", username="johndoe", password="password", tmi="tmi")
    db_session.add(user)
    await db_session.commit()

    category = Category(name="Test Category", user_id=user.id)
    db_session.add(category)
    await db_session.commit()

    todo = await create_todo(
        CreateTodoPayload(
            title="Test Todo", description="Test Description", category_id=category.id
        ),
        db_session,
        user,
    )

    assert todo.title == "Test Todo"
    assert todo.description == "Test Description"
    assert todo.status == "todo"
    assert todo.category_id == 1
