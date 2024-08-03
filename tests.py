from models import User
from sqlmodel import select


async def test_create_user(db_session):
    user = User(name="John Doe", username="johndoe", password="password", tmi="tmi")
    db_session.add(user)
    await db_session.commit()

    stmt = select(User).where(User.username == "johndoe")
    result = await db_session.execute(stmt)
    user = result.scalars().first()
    assert user.username == "johndoe"



