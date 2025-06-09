from datetime import datetime
from src.schemas.users import User, UserEdit


async def testings_add(db):
    result = await db.users.new_user(
        User(user_id="2387402134", calories=1, calories_limit=12)
    )
    await db.commit()


async def testings_edit(db):
    result = await db.users.update_user_data(
        user_id="2387402134",
        data=UserEdit(
            calories=32,
        ),
    )
    await db.commit()
