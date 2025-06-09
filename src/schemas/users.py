from pydantic import BaseModel
from datetime import date, datetime


class User(BaseModel):
    user_id: str
    updated_at: datetime 
    last_date: date 
    calories: int
    calories_limit: int


class UserAdd(BaseModel):
    user_id: str

class UserEditCalories(BaseModel): 
    calories: int | None = None
    updated_at: datetime | None = datetime.now()

class UserEditLimits(BaseModel): 
    calories_limit: int | None = None
    updated_at: datetime | None = datetime.now()

class UserEdit(BaseModel):
    calories: int | None = None
    updated_at: datetime | None = datetime.now()
    last_date: date | None = date.today()