from pydantic import BaseModel
from datetime import date, datetime

class User(BaseModel):
    user_id: str
    calories: int
    calories_limit: int

class UserEdit(BaseModel):
    calories: int | None = None
    calories_limit: int | None = None

    
