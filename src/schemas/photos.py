from pydantic import BaseModel


class Ingredient(BaseModel):
    name: str
    calories: int


class ParsedListIngredient(BaseModel):
    ingredients: list[Ingredient]

    @property
    def calories(self):
        return sum(ingredient.calories for ingredient in self.ingredients)
