import pytest

from src.services.api_ml_model import CalorieCounterGPT
from src.schemas.photos import ParsedListIngredient, Ingredient

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))


@pytest.mark.parametrize(
    "image_name",
    [
        ("327.png"),
        ("328.png"),
    ],
)
def test_photo_detect(image_name):
    with open(f"tests/unit/static/{image_name}", "rb") as f:
        result: ParsedListIngredient = CalorieCounterGPT().analyze_food(file=f)

        assert isinstance(result, ParsedListIngredient)
        for ingredient in result.ingredients:
            assert isinstance(ingredient, Ingredient)
