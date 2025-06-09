import asyncio
import logging
from aiogram import Dispatcher, Bot, Router
import sys
from io import BytesIO
from aiogram import types
from pathlib import Path

# добавление src в поле видимости
sys.path.append(str(Path(__file__).parent.parent))

from src.api.users import UserFSM
from src.services.api_ml_model import CalorieCounterGPT
from src.database import Base, engine
from src.models import *
from src.config import settings
from src.api.users import router as user_router

dp = Dispatcher()
bot = Bot(token=settings.API_TOKEN_TG)

photo_router = Router()


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await dp.start_polling(bot)


@photo_router.message(UserFSM.send_photo)
async def get_file_from_message(message: types.Message) -> BytesIO:
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await message.bot.get_file(file_id)
    file_content = await message.bot.download_file(file.file_path)
    file = BytesIO(file_content.getvalue())
    await message.answer("Обрабатываю")
    data = CalorieCounterGPT().analyze_food(file=file)
    result = ""
    for ingredient in data.ingredients:
        result += f"{ingredient.name}\n   Калории: {ingredient.calories} ккал\n\n"
    result += f"\nВсего: {data.calories} ккал"
    await message.answer(result)


if __name__ == "__main__":
    dp.include_router(photo_router)
    dp.include_router(user_router)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
