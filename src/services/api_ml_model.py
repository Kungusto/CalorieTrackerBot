import base64
import json
import openai

import sys
from pathlib import Path

# добавление src в поле видимости
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import settings
from src.schemas.photos import Ingredient, ParsedListIngredient


class CalorieCounterGPT:
    def encode_image(self, image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def analyze_food(self, file):
        openai.api_key = settings.API_KEY_GPT

        base64_image = base64.b64encode(file.read()).decode("utf-8")

        system_prompt = """
        Ты — высококвалифицированный диетолог и специалист по анализу пищи. Твоя задача — описать еду на картинке, а затем **максимально точно и ювелирно** проанализировать фото блюда, определить его состав и точно рассчитать калорийность каждого ингредиента. Все данные нужно вернуть в формате **строго JSON**, без косых апострофов. 
        Формат ответа:
        [
        {
            "name": "<ингредиент на русском>",
            "calories": <калорийность всего ингредиента в ккал>
        },
        ...
        ]
        Внимательно оцени состав и калорийность каждого ингредиента на фото, основываясь на визуальных характеристиках. Постарайся быть максимально точным при расчете калорийности, учитывая примерный вес каждого ингредиента на изображении. 
        """

        user_content = [
            {"type": "text", "text": "Фото блюда ниже."},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
        ]

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0,
            max_tokens=500,
        )

        text = response.choices[0].message.content

        ingreadients_text = self.validate_json_simple(text)

        ingreadients = json.loads(ingreadients_text)
        list_ingreadients = []
        for ingredient in ingreadients:
            list_ingreadients.append(Ingredient(**ingredient))
        return ParsedListIngredient(ingredients=list_ingreadients)

    def validate_json_simple(self, text):
        start_index = text.find("[")
        end_index = text.rfind("]")

        if start_index == -1 or end_index == -1 or end_index < start_index:
            return text

        text = text[start_index : end_index + 1]
        return text
