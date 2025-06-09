from pydantic import BaseModel
from datetime import date, datetime

class User(BaseModel):
    user_id: str
    calories: int
    calories_limit: int

class UserEdit(BaseModel):
    calories: int | None = None
    calories_limit: int | None = None

class Ingredient(BaseModel): 
    name: str
    calories: int

class ParsedListIngredient(BaseModel):
    ingredients: list[Ingredient]

    @property
    def calories(self):
        return sum(ingredient.calories for ingredient in self.ingredients)
    
