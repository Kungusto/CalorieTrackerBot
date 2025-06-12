from datetime import datetime
from src.schemas.users import User, UserEdit, UserAdd


async def test_auth(db):
    user_data = {
        "user_id":"2387402134", 
    }
    result = await db.users.new_user(
        UserAdd(**user_data)
    )
    added_user = result.model_dump() 
    assert isinstance(result, User)
    assert added_user["user_id"] == user_data["user_id"]
    data_to_update = {
        "calories": 150
    }
    result = await db.users.update_user_data(
        data=UserEdit(**data_to_update),
        user_id="2387402134"
    )
    updated_user = result.model_dump() 
    assert isinstance(result, User)
    assert updated_user["calories"] == data_to_update["calories"]
    await db.commit()
